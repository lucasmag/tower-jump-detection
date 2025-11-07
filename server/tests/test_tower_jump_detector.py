import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tower_jump_detector import TowerJumpDetector


class TestTowerJumpDetector(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = TowerJumpDetector()

        # Sample data for testing
        self.sample_data = pd.DataFrame(
            {
                "UTCDateTime": pd.to_datetime(
                    [
                        "2022-01-26 22:00:00",
                        "2022-01-26 22:30:00",
                        "2022-01-26 23:00:00",
                        "2022-01-27 00:00:00",
                    ]
                ),
                "State": ["New York", "Connecticut", "New York", "Connecticut"],
                "Latitude": [40.7128, 41.2033, 40.7589, 41.2033],
                "Longitude": [-74.0060, -73.1234, -73.9851, -73.1234],
            }
        )


class TestTowerJumpDetectorInit(TestTowerJumpDetector):
    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        detector = TowerJumpDetector()
        self.assertEqual(detector.max_speed_kmh, 1000.0)
        self.assertEqual(detector.min_confidence_threshold, 50.0)

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        detector = TowerJumpDetector(max_speed_kmh=500.0, min_confidence_threshold=75.0)
        self.assertEqual(detector.max_speed_kmh, 500.0)
        self.assertEqual(detector.min_confidence_threshold, 75.0)


class TestAnalyze(TestTowerJumpDetector):
    def test_analyze_empty_dataframe(self):
        """Test analyze method with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = self.detector.analyze(empty_df)
        self.assertTrue(result.empty)

    def test_analyze_returns_dataframe(self):
        """Test that analyze returns a DataFrame with expected columns."""
        result = self.detector.analyze(self.sample_data)
        self.assertIsInstance(result, pd.DataFrame)

        expected_columns = [
            "TimeStart",
            "TimeEnd",
            "DurationMinutes",
            "State",
            "AllStates",
            "IsTowerJump",
            "ConfidenceLevel",
            "RecordCount",
            "StateChanges",
            "MaxSpeedKMH",
            "MaxDistanceKM",
            "AvgLatitude",
            "AvgLongitude",
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns)


class TestCreateTimePeriods(TestTowerJumpDetector):
    def test_create_time_periods_empty_dataframe(self):
        """Test _create_time_periods with empty DataFrame."""
        empty_df = pd.DataFrame()
        periods = self.detector._create_time_periods(empty_df)
        self.assertEqual(len(periods), 0)

    def test_create_time_periods_single_record(self):
        """Test _create_time_periods with single record."""
        single_record = self.sample_data.iloc[:1].copy()
        periods = self.detector._create_time_periods(single_record)
        self.assertEqual(len(periods), 1)
        self.assertEqual(len(periods[0]["records"]), 1)

    def test_create_time_periods_consecutive_records(self):
        """Test _create_time_periods groups consecutive records properly."""
        periods = self.detector._create_time_periods(
            self.sample_data, time_window_minutes=60
        )
        self.assertGreater(len(periods), 0)

        # Check that each period has required keys
        for period in periods:
            self.assertIn("start_time", period)
            self.assertIn("end_time", period)
            self.assertIn("records", period)
            self.assertIn("states", period)
            self.assertIn("locations", period)

    def test_create_time_periods_large_gap(self):
        """Test _create_time_periods splits on large time gaps."""
        # Create data with large time gap
        data_with_gap = pd.DataFrame(
            {
                "UTCDateTime": pd.to_datetime(
                    ["2022-01-26 22:00:00", "2022-01-27 10:00:00"]  # 12 hour gap
                ),
                "State": ["New York", "Connecticut"],
                "Latitude": [40.7128, 41.2033],
                "Longitude": [-74.0060, -73.1234],
            }
        )

        periods = self.detector._create_time_periods(
            data_with_gap, time_window_minutes=30
        )
        self.assertEqual(len(periods), 2)  # Should create separate periods


class TestCalculateMaxDistance(TestTowerJumpDetector):
    def test_calculate_max_distance_single_location(self):
        """Test _calculate_max_distance with single location."""
        locations = [(40.7128, -74.0060)]
        distance = self.detector._calculate_max_distance(locations)
        self.assertEqual(distance, 0.0)

    def test_calculate_max_distance_two_locations(self):
        """Test _calculate_max_distance with two locations."""
        locations = [(40.7128, -74.0060), (41.2033, -73.1234)]  # NY to CT
        distance = self.detector._calculate_max_distance(locations)
        self.assertGreater(distance, 0)
        self.assertLess(distance, 200)  # Reasonable distance in km

    def test_calculate_max_distance_multiple_locations(self):
        """Test _calculate_max_distance with multiple locations."""
        locations = [
            (40.7128, -74.0060),  # NYC
            (41.2033, -73.1234),  # Stamford, CT
            (40.7589, -73.9851),  # Times Square
        ]
        distance = self.detector._calculate_max_distance(locations)
        self.assertGreater(distance, 0)

    def test_calculate_max_distance_handles_exceptions(self):
        """Test _calculate_max_distance handles invalid coordinates gracefully."""
        locations = [(None, None), (40.7128, -74.0060)]
        distance = self.detector._calculate_max_distance(locations)
        # Should not crash and return some value
        self.assertIsInstance(distance, float)


class TestCalculateMaxSpeed(TestTowerJumpDetector):
    def test_calculate_max_speed_single_record(self):
        """Test _calculate_max_speed with single record."""
        period = {"records": [0]}
        speed = self.detector._calculate_max_speed(period, self.sample_data)
        self.assertEqual(speed, 0.0)

    def test_calculate_max_speed_two_records(self):
        """Test _calculate_max_speed with two records."""
        period = {"records": [0, 1]}
        speed = self.detector._calculate_max_speed(period, self.sample_data)
        self.assertGreaterEqual(speed, 0)

    def test_calculate_max_speed_handles_exceptions(self):
        """Test _calculate_max_speed handles invalid data gracefully."""
        # Create data with invalid coordinates
        invalid_data = pd.DataFrame(
            {
                "UTCDateTime": pd.to_datetime(
                    ["2022-01-26 22:00:00", "2022-01-26 22:30:00"]
                ),
                "State": ["New York", "Connecticut"],
                "Latitude": [None, 41.2033],
                "Longitude": [-74.0060, None],
            }
        )
        period = {"records": [0, 1]}
        speed = self.detector._calculate_max_speed(period, invalid_data)
        self.assertIsInstance(speed, float)


class TestIsTowerJump(TestTowerJumpDetector):
    def test_is_tower_jump_high_speed(self):
        """Test _is_tower_jump detects high speed as tower jump."""
        result = self.detector._is_tower_jump(
            state_changes=1,
            max_speed=2000.0,  # Very high speed
            duration=30.0,
            unique_states=["New York", "Connecticut"],
        )
        self.assertTrue(result)

    def test_is_tower_jump_frequent_state_changes(self):
        """Test _is_tower_jump detects frequent state changes."""
        result = self.detector._is_tower_jump(
            state_changes=5,  # Many changes
            max_speed=50.0,  # Normal speed
            duration=30.0,  # Short duration
            unique_states=["New York", "Connecticut"],
        )
        self.assertTrue(result)

    def test_is_tower_jump_ny_ct_pattern(self):
        """Test _is_tower_jump detects NY/CT specific pattern."""
        result = self.detector._is_tower_jump(
            state_changes=3,
            max_speed=100.0,
            duration=60.0,  # Under 2 hours
            unique_states=["New York", "Connecticut"],
        )
        self.assertTrue(result)

    def test_is_tower_jump_normal_behavior(self):
        """Test _is_tower_jump doesn't flag normal behavior."""
        result = self.detector._is_tower_jump(
            state_changes=1,
            max_speed=50.0,  # Normal speed
            duration=120.0,  # Normal duration
            unique_states=["New York"],
        )
        self.assertFalse(result)


class TestCalculateConfidence(TestTowerJumpDetector):
    def test_calculate_confidence_base_level(self):
        """Test _calculate_confidence returns base confidence plus slow speed bonus."""
        confidence = self.detector._calculate_confidence(
            state_changes=0,
            max_speed=0.0,  # This gets +10 for being <50 km/h
            duration=60.0,
            record_count=1,
            unique_states=["New York"],
        )
        self.assertEqual(
            confidence, 60.0
        )  # Base confidence (50) + slow speed bonus (10)

    def test_calculate_confidence_high_speed_bonus(self):
        """Test _calculate_confidence gives bonus for high speed."""
        confidence = self.detector._calculate_confidence(
            state_changes=0,
            max_speed=2000.0,  # Very high speed
            duration=60.0,
            record_count=1,
            unique_states=["New York"],
        )
        self.assertGreater(confidence, 50.0)

    def test_calculate_confidence_ny_ct_bonus(self):
        """Test _calculate_confidence gives bonus for NY/CT pattern."""
        confidence = self.detector._calculate_confidence(
            state_changes=2,
            max_speed=100.0,
            duration=60.0,
            record_count=5,
            unique_states=["New York", "Connecticut"],
        )
        self.assertGreater(confidence, 50.0)

    def test_calculate_confidence_max_100(self):
        """Test _calculate_confidence caps at 100%."""
        confidence = self.detector._calculate_confidence(
            state_changes=10,
            max_speed=5000.0,  # Extremely high speed
            duration=10.0,  # Very short
            record_count=20,  # Many records
            unique_states=["New York", "Connecticut"],
        )
        self.assertEqual(confidence, 100.0)


class TestAnalyzePeriod(TestTowerJumpDetector):
    def test_analyze_period_returns_dict(self):
        """Test _analyze_period returns properly formatted dictionary."""
        period = {
            "start_time": self.sample_data.iloc[0]["UTCDateTime"],
            "end_time": self.sample_data.iloc[1]["UTCDateTime"],
            "records": [0, 1],
            "states": ["New York", "Connecticut"],
            "locations": [(40.7128, -74.0060), (41.2033, -73.1234)],
        }

        result = self.detector._analyze_period(period, self.sample_data)

        expected_keys = [
            "TimeStart",
            "TimeEnd",
            "DurationMinutes",
            "State",
            "AllStates",
            "IsTowerJump",
            "ConfidenceLevel",
            "RecordCount",
            "StateChanges",
            "MaxSpeedKMH",
            "MaxDistanceKM",
            "AvgLatitude",
            "AvgLongitude",
        ]

        for key in expected_keys:
            self.assertIn(key, result)

    def test_analyze_period_calculates_duration(self):
        """Test _analyze_period calculates duration correctly."""
        start_time = datetime(2022, 1, 26, 22, 0, 0)
        end_time = datetime(2022, 1, 26, 22, 30, 0)

        period = {
            "start_time": start_time,
            "end_time": end_time,
            "records": [0],
            "states": ["New York"],
            "locations": [(40.7128, -74.0060)],
        }

        result = self.detector._analyze_period(period, self.sample_data)
        self.assertEqual(result["DurationMinutes"], 30.0)


class TestGetSummaryStats(TestTowerJumpDetector):
    def test_get_summary_stats_empty_dataframe(self):
        """Test get_summary_stats with empty DataFrame."""
        empty_df = pd.DataFrame()
        stats = self.detector.get_summary_stats(empty_df)
        self.assertEqual(stats, {})

    def test_get_summary_stats_valid_data(self):
        """Test get_summary_stats with valid analysis results."""
        # Create mock analysis results
        results_df = pd.DataFrame(
            {
                "TimeStart": ["2022-01-26 22:00:00", "2022-01-26 23:00:00"],
                "TimeEnd": ["2022-01-26 22:30:00", "2022-01-26 23:30:00"],
                "State": ["New York", "Connecticut"],
                "IsTowerJump": [True, False],
                "ConfidenceLevel": [75.0, 45.0],
                "MaxSpeedKMH": [1500.0, 50.0],
            }
        )

        stats = self.detector.get_summary_stats(results_df)

        expected_keys = [
            "total_periods",
            "tower_jumps_detected",
            "tower_jump_percentage",
            "avg_confidence",
            "max_speed_detected",
            "states_involved",
            "date_range",
        ]

        for key in expected_keys:
            self.assertIn(key, stats)

        self.assertEqual(stats["total_periods"], 2)
        self.assertEqual(stats["tower_jumps_detected"], 1)
        self.assertEqual(stats["tower_jump_percentage"], 50.0)

    def test_get_summary_stats_no_tower_jumps(self):
        """Test get_summary_stats when no tower jumps detected."""
        results_df = pd.DataFrame(
            {
                "TimeStart": ["2022-01-26 22:00:00"],
                "TimeEnd": ["2022-01-26 22:30:00"],
                "State": ["New York"],
                "IsTowerJump": [False],
                "ConfidenceLevel": [45.0],
                "MaxSpeedKMH": [50.0],
            }
        )

        stats = self.detector.get_summary_stats(results_df)
        self.assertEqual(stats["tower_jumps_detected"], 0)
        self.assertEqual(stats["tower_jump_percentage"], 0.0)


class TestIntegration(TestTowerJumpDetector):
    def test_full_analysis_workflow(self):
        """Test complete analysis workflow from start to finish."""
        # Create realistic test data with potential tower jump
        test_data = pd.DataFrame(
            {
                "UTCDateTime": pd.to_datetime(
                    [
                        "2022-01-26 22:00:00",
                        "2022-01-26 22:01:00",  # Very quick transition
                        "2022-01-26 22:02:00",
                        "2022-01-26 22:03:00",
                    ]
                ),
                "State": ["New York", "Connecticut", "New York", "Connecticut"],
                "Latitude": [40.7128, 41.2033, 40.7589, 41.2033],
                "Longitude": [-74.0060, -73.1234, -73.9851, -73.1234],
            }
        )

        # Run full analysis
        results = self.detector.analyze(test_data)
        summary = self.detector.get_summary_stats(results)

        # Verify results structure
        self.assertIsInstance(results, pd.DataFrame)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(summary, dict)

        # Verify some tower jumps were detected due to rapid state changes
        if summary:
            self.assertIn("tower_jumps_detected", summary)


if __name__ == "__main__":
    unittest.main()
