import pandas as pd
from typing import Dict, Any


class DataProcessor:
    """Handles loading and preprocessing of carrier data CSV files."""

    def __init__(self):
        self.required_columns = [
            "Page",
            "Item",
            "UTCDateTime",
            "LocalDateTime",
            "Latitude",
            "Longitude",
            "TimeZone",
            "City",
            "County",
            "State",
            "Country",
            "CellType",
        ]

    def load_csv_from_file(self, file) -> pd.DataFrame:
        """Load and preprocess CSV data from uploaded file."""
        try:
            df = pd.read_csv(file)

            missing_cols = [
                col for col in self.required_columns if col not in df.columns
            ]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            df = self._preprocess_data(df)

            return df

        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the carrier data."""
        initial_count = len(df)
        print(f"Initial data count: {initial_count}")

        # Remove records with missing or zero coordinates
        df = df[~((df["Latitude"] == 0) & (df["Longitude"] == 0))]
        df = df.dropna(subset=["Latitude", "Longitude", "State"])
        after_location_cleanup = len(df)
        print(
            f"After location cleanup: {after_location_cleanup} ({initial_count - after_location_cleanup} removed)"
        )

        # Convert datetime columns
        df["UTCDateTime"] = pd.to_datetime(
            df["UTCDateTime"], format="%m/%d/%y %H:%M", errors="coerce"
        )
        df["LocalDateTime"] = pd.to_datetime(
            df["LocalDateTime"], format="%m/%d/%y %H:%M", errors="coerce"
        )
        valid_datetime_count = len(df.dropna(subset=["UTCDateTime"]))
        print(f"Valid datetime records: {valid_datetime_count}")

        # Convert coordinates to numeric, handling missing values
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        # Fill missing string fields
        string_columns = ["City", "County", "State", "Country", "TimeZone"]
        for col in string_columns:
            df[col] = df[col].fillna("")

        # Sort by datetime for chronological processing
        df = df.sort_values("UTCDateTime").reset_index(drop=True)

        return df

    def get_date_range(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get the date range of the data."""
        if df.empty or "UTCDateTime" not in df.columns:
            return {"start": "N/A", "end": "N/A"}

        valid_dates = df["UTCDateTime"].dropna()
        if valid_dates.empty:
            return {"start": "N/A", "end": "N/A"}

        return {
            "start": valid_dates.min().strftime("%Y-%m-%d %H:%M:%S"),
            "end": valid_dates.max().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_data_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic statistics about the data."""
        stats = {
            "total_records": len(df),
            "records_with_location": (
                len(df.dropna(subset=["Latitude", "Longitude"]))
                if all(col in df.columns for col in ["Latitude", "Longitude"])
                else 0
            ),
            "unique_states": df["State"].nunique() if "State" in df.columns else 0,
            "date_range": self.get_date_range(df),
            "cell_types": (
                df["CellType"].value_counts().to_dict()
                if "CellType" in df.columns
                else {}
            ),
        }

        if "State" in df.columns:
            stats["states"] = df["State"].value_counts().to_dict()

        return stats
