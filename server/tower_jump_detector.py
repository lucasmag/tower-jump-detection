import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from geopy.distance import geodesic
from typing import List, Dict, Any, Tuple


class TowerJumpDetector:
    """Detects tower jumps in cellular carrier data."""

    def __init__(
        self, max_speed_kmh: float = 1000.0, min_confidence_threshold: float = 50.0
    ):
        """
        Initialize the tower jump detector.

        Args:
            max_speed_kmh: Maximum realistic travel speed in km/h (default 1000 km/h ~ aircraft speed)
            min_confidence_threshold: Minimum confidence level to consider valid
        """
        self.max_speed_kmh = max_speed_kmh
        self.min_confidence_threshold = min_confidence_threshold

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze the data to detect tower jumps.

        Args:
            df: Preprocessed carrier data DataFrame

        Returns:
            DataFrame with analysis results
        """
        if df.empty:
            return pd.DataFrame()

        # Group consecutive records by location/state with time windows
        periods = self._create_time_periods(df)

        # Analyze each period for tower jumps
        results = []
        for period in periods:
            analysis = self._analyze_period(period, df)
            results.append(analysis)

        return pd.DataFrame(results)

    def _create_time_periods(
        self, df: pd.DataFrame, time_window_minutes: int = 30
    ) -> List[Dict]:
        """
        Create time periods by grouping consecutive records.

        Args:
            df: Input DataFrame
            time_window_minutes: Time window for grouping records

        Returns:
            List of time period dictionaries
        """
        periods = []

        if df.empty:
            return periods

        # Sort by time
        df_sorted = df.sort_values("UTCDateTime").reset_index()

        current_period = {
            "start_time": df_sorted.iloc[0]["UTCDateTime"],
            "end_time": df_sorted.iloc[0]["UTCDateTime"],
            "records": [0],
            "states": [df_sorted.iloc[0]["State"]],
            "locations": [
                (df_sorted.iloc[0]["Latitude"], df_sorted.iloc[0]["Longitude"])
            ],
        }

        # Iterate through remaining records starting from index 1
        # (index 0 was already added to the first period above)
        for i in range(1, len(df_sorted)):
            current_row = df_sorted.iloc[i]

            # Calculate time difference between current record and the end of current period
            # Convert from seconds to minutes for easier comparison with time_window_minutes
            time_diff = (
                current_row["UTCDateTime"] - current_period["end_time"]
            ).total_seconds() / 60

            # Decision point: Should this record extend the current period or start a new one?
            # If the time gap is larger than our window (default 30 minutes),
            # we consider this record to be from a separate activity session
            if time_diff > time_window_minutes:
                # Time gap is too large - finalize current period and start new one

                # Save the completed period to our results list
                periods.append(current_period)

                # Initialize a new period starting with this record
                # This record becomes both the start and end of the new period
                current_period = {
                    "start_time": current_row["UTCDateTime"],  # Period begins here
                    "end_time": current_row[
                        "UTCDateTime"
                    ],  # Period ends here (for now)
                    "records": [i],  # List of record indices in this period
                    "states": [
                        current_row["State"]
                    ],  # List of states visited in this period
                    "locations": [
                        (current_row["Latitude"], current_row["Longitude"])
                    ],  # List of (lat, lng) tuples
                }
            else:
                # Time gap is small enough - extend current period with this record

                # Update the end time of current period to include this record
                current_period["end_time"] = current_row["UTCDateTime"]

                # Add this record's index to the period's record list
                # This helps us track which original data rows belong to this period
                current_period["records"].append(i)

                # Add this record's state to the period's state history
                # This creates a chronological list of state changes within the period
                current_period["states"].append(current_row["State"])

                # Add this record's location to the period's location history
                # This creates a chronological path of locations within the period
                current_period["locations"].append(
                    (current_row["Latitude"], current_row["Longitude"])
                )

        # Don't forget the last period! After the loop ends, we still have
        # the final period in current_period that needs to be added to results
        # Only add it if it actually contains records (safety check)
        if current_period["records"]:
            periods.append(current_period)

        return periods

    def _analyze_period(self, period: Dict, df: pd.DataFrame) -> Dict:
        """
        Analyze a single time period for tower jumps.

        Args:
            period: Time period dictionary
            df: Original DataFrame

        Returns:
            Analysis result dictionary
        """
        # Calculate basic metrics
        duration_minutes = (
            period["end_time"] - period["start_time"]
        ).total_seconds() / 60
        unique_states = list(set(period["states"]))
        num_state_changes = len(
            [
                i
                for i in range(1, len(period["states"]))
                if period["states"][i] != period["states"][i - 1]
            ]
        )

        # Calculate distances and speeds
        max_distance_km = self._calculate_max_distance(period["locations"])
        max_speed_kmh = self._calculate_max_speed(period, df)

        # Determine if this is a tower jump
        is_tower_jump = self._is_tower_jump(
            num_state_changes, max_speed_kmh, duration_minutes, unique_states, max_distance_km
        )

        # Calculate confidence level
        confidence = self._calculate_confidence(
            num_state_changes,
            max_speed_kmh,
            duration_minutes,
            len(period["records"]),
            unique_states,
            max_distance_km,
            is_tower_jump,
        )

        # Determine primary state (most frequent)
        state_counts = {}
        for state in period["states"]:
            state_counts[state] = state_counts.get(state, 0) + 1
        primary_state = max(state_counts, key=state_counts.get)

        # Calculate average location
        avg_lat = np.mean([loc[0] for loc in period["locations"]])
        avg_lng = np.mean([loc[1] for loc in period["locations"]])

        return {
            "TimeStart": period["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "TimeEnd": period["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "DurationMinutes": round(duration_minutes, 2),
            "State": primary_state,
            "AllStates": ", ".join(unique_states),
            "IsTowerJump": "yes" if is_tower_jump else "no",
            "ConfidenceLevel": round(confidence, 1),
            "RecordCount": len(period["records"]),
            "StateChanges": num_state_changes,
            "MaxSpeedKMH": round(max_speed_kmh, 1),
            "MaxDistanceKM": round(max_distance_km, 2),
            "AvgLatitude": round(avg_lat, 6),
            "AvgLongitude": round(avg_lng, 6),
        }

    def _calculate_max_distance(self, locations: List[Tuple[float, float]]) -> float:
        """Calculate maximum distance between any two points in kilometers."""
        if len(locations) < 2:
            return 0.0

        max_distance = 0.0
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                try:
                    distance = geodesic(locations[i], locations[j]).kilometers
                    max_distance = max(max_distance, distance)
                except:
                    continue

        return max_distance

    def _calculate_max_speed(self, period: Dict, df: pd.DataFrame) -> float:
        """Calculate maximum speed between consecutive records in km/h."""
        if len(period["records"]) < 2:
            return 0.0

        max_speed = 0.0

        for i in range(1, len(period["records"])):
            prev_idx = period["records"][i - 1]
            curr_idx = period["records"][i]

            prev_row = df.iloc[prev_idx]
            curr_row = df.iloc[curr_idx]

            # Calculate time difference in hours
            time_diff = (
                curr_row["UTCDateTime"] - prev_row["UTCDateTime"]
            ).total_seconds() / 3600

            if time_diff > 0:
                try:
                    # Calculate distance in kilometers
                    distance = geodesic(
                        (prev_row["Latitude"], prev_row["Longitude"]),
                        (curr_row["Latitude"], curr_row["Longitude"]),
                    ).kilometers

                    speed = distance / time_diff
                    max_speed = max(max_speed, speed)
                except:
                    continue

        return max_speed

    def _is_tower_jump(
        self,
        state_changes: int,
        max_speed: float,
        duration: float,
        unique_states: List[str],
        max_distance: float,
    ) -> bool:
        """
        Determine if this period represents a tower jump.

        Args:
            state_changes: Number of state changes
            max_speed: Maximum speed detected (km/h)
            duration: Duration in minutes
            unique_states: List of unique states
            max_distance: Maximum distance between any two points (km)

        Returns:
            True if this is likely a tower jump
        """
        # Criteria for tower jump detection:
        # 1. Multiple state changes in short time
        # 2. Impossible travel speeds (>1000 km/h ~ aircraft speed)
        # 3. Rapid ping-ponging between states
        # 4. Large distances covered in short time

        # Speed-based detection
        if max_speed > self.max_speed_kmh:
            return True

        # Distance-based detection: covering large distances quickly
        if duration > 0 and max_distance > 0:
            distance_per_hour = max_distance / (duration / 60)  # km/h equivalent
            if distance_per_hour > self.max_speed_kmh:  # Same threshold as speed
                return True

        # Frequency-based detection
        if state_changes >= 3 and duration < 60:  # 3+ state changes in under 1 hour
            return True

        if len(unique_states) >= 2 and state_changes >= 5:  # Rapid ping-ponging
            return True

        # Check for NY/CT specific ping-ponging
        if "New York" in unique_states and "Connecticut" in unique_states:
            if state_changes >= 2 and duration < 120:  # 2+ changes in 2 hours
                return True

        return False

    def _calculate_confidence(
        self,
        state_changes: int,
        max_speed: float,
        duration: float,
        record_count: int,
        unique_states: List[str],
        max_distance: float,
        is_tower_jump: bool,
    ) -> float:
        """
        Calculate confidence level for the tower jump detection.

        Returns:
            Confidence percentage (0-100)
        """
        confidence = 50.0  # Base confidence

        # More records = higher confidence in any decision
        if record_count >= 10:
            confidence += 10
        elif record_count >= 5:
            confidence += 5

        if is_tower_jump:
            # We think this is cell tower ping-pong, not real movement
            # Confidence based on how impossible the movement is

            # Distance-based evidence
            if max_distance > 500:  # Long distance jump (cross-country)
                confidence += 20  # Very confident it's tower error
            elif max_distance > 100:  # Medium distance jump (cross-state)
                confidence += 15  # Confident it's tower error
            elif max_distance < 10:  # Short distance ping-pong (border area)
                confidence += 10  # Likely tower triangulation error

            # Speed-based evidence (backup to distance)
            if max_speed > self.max_speed_kmh * 2:  # Physically impossible (>2000 km/h)
                confidence += 15  # Very confident it's tower error
            elif max_speed > self.max_speed_kmh:  # Very unlikely (>1000 km/h)
                confidence += 10  # Confident it's tower error

            # Pattern-based evidence
            if state_changes >= 5:  # Rapid ping-pong pattern
                confidence += 10  # Likely tower error
            elif duration < 30 and state_changes >= 3:  # Quick back-and-forth
                confidence += 10  # Likely tower ping-pong
            else:
                confidence += 5   # Possible tower error

        else:
            # We think this represents real subscriber location/movement
            if state_changes == 0 and max_distance < 5:  # Stayed in same local area
                confidence += 20  # Very confident in actual location
            elif state_changes <= 1 and max_speed < 100:  # Minimal, reasonable movement
                confidence += 15  # Confident in actual location
            elif state_changes <= 2 and max_speed < 200:  # Reasonable travel
                confidence += 10  # Confident in actual location
            else:
                confidence += 5   # Somewhat confident

        # NY/CT border area: Known for triangulation issues
        if "New York" in unique_states and "Connecticut" in unique_states:
            if is_tower_jump:
                confidence += 10  # Even more confident it's ping-pong
            else:
                confidence -= 5   # Less confident in actual cross-border travel

        return min(confidence, 100.0)

    def get_summary_stats(self, results: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of the analysis results."""
        if results.empty:
            return {}

        tower_jumps = results[results["IsTowerJump"] == "yes"]

        return {
            "total_periods": len(results),
            "tower_jumps_detected": len(tower_jumps),
            "tower_jump_percentage": round(len(tower_jumps) / len(results) * 100, 1),
            "avg_confidence": round(results["ConfidenceLevel"].mean(), 1),
            "max_speed_detected": round(results["MaxSpeedKMH"].max(), 1),
            "states_involved": list(results["State"].unique()),
            "date_range": {
                "start": results["TimeStart"].min(),
                "end": results["TimeEnd"].max(),
            },
        }
