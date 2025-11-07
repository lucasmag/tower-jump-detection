import unittest
import pandas as pd
import numpy as np
from io import StringIO
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processor import DataProcessor


class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = DataProcessor()

        # Sample valid CSV data
        self.valid_csv_data = """Page,Item,UTCDateTime,LocalDateTime,Latitude,Longitude,TimeZone,City,County,State,Country,CellType
        1,1,1/26/22 22:00,1/26/22 17:00,40.7128,-74.0060,EST,New York,New York,New York,USA,LTE
        2,2,1/26/22 22:30,1/26/22 17:30,41.2033,-73.1234,EST,Stamford,Fairfield,Connecticut,USA,LTE
        3,3,1/26/22 23:00,1/26/22 18:00,40.7589,-73.9851,EST,New York,New York,New York,USA,5G
        """

        # Invalid CSV data (missing required columns)
        self.invalid_csv_data = """Page,Item,DateTime,Lat,Lng
        1,1,1/26/22 22:00,40.7128,-74.0060
        """


class TestDataProcessorInit(TestDataProcessor):
    def test_init_sets_required_columns(self):
        """Test that initialization sets the required columns."""
        expected_columns = [
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
        self.assertEqual(self.processor.required_columns, expected_columns)


class TestLoadCSVFromFile(TestDataProcessor):
    def test_load_valid_csv(self):
        """Test loading a valid CSV file."""
        mock_file = StringIO(self.valid_csv_data)

        with patch("builtins.print"):  # Suppress print statements
            result_df = self.processor.load_csv_from_file(mock_file)

        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 3)
        self.assertIn("UTCDateTime", result_df.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result_df["UTCDateTime"]))

    def test_load_invalid_csv_missing_columns(self):
        """Test loading CSV with missing required columns raises error."""
        mock_file = StringIO(self.invalid_csv_data)

        with self.assertRaises(Exception) as context:
            self.processor.load_csv_from_file(mock_file)

        self.assertIn("Missing required columns", str(context.exception))

    def test_load_csv_exception_handling(self):
        """Test that CSV loading exceptions are properly handled."""
        mock_file = Mock()
        mock_file.side_effect = Exception("File read error")

        with self.assertRaises(Exception) as context:
            self.processor.load_csv_from_file(mock_file)

        self.assertIn("Error loading CSV", str(context.exception))


class TestPreprocessData(TestDataProcessor):
    def test_preprocess_removes_zero_coordinates(self):
        """Test that records with zero coordinates are removed."""
        df = pd.DataFrame(
            {
                "Page": [1, 2, 3],
                "Item": [1, 2, 3],
                "UTCDateTime": ["1/26/22 22:00", "1/26/22 22:30", "1/26/22 23:00"],
                "LocalDateTime": ["1/26/22 17:00", "1/26/22 17:30", "1/26/22 18:00"],
                "Latitude": [0, 40.7128, 41.2033],
                "Longitude": [0, -74.0060, -73.1234],
                "TimeZone": ["EST", "EST", "EST"],
                "City": ["", "New York", "Stamford"],
                "County": ["", "New York", "Fairfield"],
                "State": ["New York", "New York", "Connecticut"],
                "Country": ["USA", "USA", "USA"],
                "CellType": ["LTE", "LTE", "5G"],
            }
        )

        with patch("builtins.print"):  # Suppress print statements
            result = self.processor._preprocess_data(df)

        self.assertEqual(len(result), 2)  # Should remove the (0,0) record
        self.assertNotIn(0, result["Latitude"].values)

    def test_preprocess_removes_missing_coordinates(self):
        """Test that records with missing coordinates are removed."""
        df = pd.DataFrame(
            {
                "Page": [1, 2, 3],
                "Item": [1, 2, 3],
                "UTCDateTime": ["1/26/22 22:00", "1/26/22 22:30", "1/26/22 23:00"],
                "LocalDateTime": ["1/26/22 17:00", "1/26/22 17:30", "1/26/22 18:00"],
                "Latitude": [np.nan, 40.7128, 41.2033],
                "Longitude": [-74.0060, np.nan, -73.1234],
                "TimeZone": ["EST", "EST", "EST"],
                "City": ["New York", "New York", "Stamford"],
                "County": ["New York", "New York", "Fairfield"],
                "State": ["New York", "New York", "Connecticut"],
                "Country": ["USA", "USA", "USA"],
                "CellType": ["LTE", "LTE", "5G"],
            }
        )

        with patch("builtins.print"):  # Suppress print statements
            result = self.processor._preprocess_data(df)

        self.assertEqual(len(result), 1)  # Should only keep the complete record

    def test_preprocess_converts_datetime_columns(self):
        """Test that datetime columns are properly converted."""
        df = pd.DataFrame(
            {
                "Page": [1],
                "Item": [1],
                "UTCDateTime": ["1/26/22 22:00"],
                "LocalDateTime": ["1/26/22 17:00"],
                "Latitude": [40.7128],
                "Longitude": [-74.0060],
                "TimeZone": ["EST"],
                "City": ["New York"],
                "County": ["New York"],
                "State": ["New York"],
                "Country": ["USA"],
                "CellType": ["LTE"],
            }
        )

        with patch("builtins.print"):  # Suppress print statements
            result = self.processor._preprocess_data(df)

        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result["UTCDateTime"]))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result["LocalDateTime"]))

    def test_preprocess_fills_missing_string_fields(self):
        """Test that missing string fields are filled with empty strings."""
        df = pd.DataFrame(
            {
                "Page": [1],
                "Item": [1],
                "UTCDateTime": ["1/26/22 22:00"],
                "LocalDateTime": ["1/26/22 17:00"],
                "Latitude": [40.7128],
                "Longitude": [-74.0060],
                "TimeZone": [np.nan],
                "City": [np.nan],
                "County": [np.nan],
                "State": ["New York"],
                "Country": [np.nan],
                "CellType": ["LTE"],
            }
        )

        with patch("builtins.print"):  # Suppress print statements
            result = self.processor._preprocess_data(df)

        self.assertEqual(result["TimeZone"].iloc[0], "")
        self.assertEqual(result["City"].iloc[0], "")
        self.assertEqual(result["County"].iloc[0], "")
        self.assertEqual(result["Country"].iloc[0], "")

    def test_preprocess_sorts_by_datetime(self):
        """Test that data is sorted by UTCDateTime."""
        df = pd.DataFrame(
            {
                "Page": [1, 2, 3],
                "Item": [1, 2, 3],
                "UTCDateTime": ["1/26/22 23:00", "1/26/22 22:00", "1/26/22 22:30"],
                "LocalDateTime": ["1/26/22 18:00", "1/26/22 17:00", "1/26/22 17:30"],
                "Latitude": [40.7589, 40.7128, 41.2033],
                "Longitude": [-73.9851, -74.0060, -73.1234],
                "TimeZone": ["EST", "EST", "EST"],
                "City": ["New York", "New York", "Stamford"],
                "County": ["New York", "New York", "Fairfield"],
                "State": ["New York", "New York", "Connecticut"],
                "Country": ["USA", "USA", "USA"],
                "CellType": ["5G", "LTE", "LTE"],
            }
        )

        with patch("builtins.print"):  # Suppress print statements
            result = self.processor._preprocess_data(df)

        # Check that the first row has the earliest time
        self.assertEqual(result.iloc[0]["Page"], 2)  # Originally second row


class TestGetDateRange(TestDataProcessor):
    def test_get_date_range_valid_data(self):
        """Test getting date range from valid data."""
        df = pd.DataFrame(
            {
                "UTCDateTime": pd.to_datetime(
                    [
                        "2022-01-26 22:00:00",
                        "2022-01-26 23:00:00",
                        "2022-01-27 00:00:00",
                    ]
                )
            }
        )

        result = self.processor.get_date_range(df)

        self.assertEqual(result["start"], "2022-01-26 22:00:00")
        self.assertEqual(result["end"], "2022-01-27 00:00:00")

    def test_get_date_range_empty_dataframe(self):
        """Test getting date range from empty DataFrame."""
        df = pd.DataFrame()

        result = self.processor.get_date_range(df)

        self.assertEqual(result["start"], "N/A")
        self.assertEqual(result["end"], "N/A")

    def test_get_date_range_no_datetime_column(self):
        """Test getting date range when UTCDateTime column is missing."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})

        result = self.processor.get_date_range(df)

        self.assertEqual(result["start"], "N/A")
        self.assertEqual(result["end"], "N/A")

    def test_get_date_range_no_valid_dates(self):
        """Test getting date range when all dates are NaT."""
        df = pd.DataFrame(
            {
                "UTCDateTime": pd.to_datetime(
                    ["invalid", "also_invalid", "still_invalid"], errors="coerce"
                )
            }
        )

        result = self.processor.get_date_range(df)

        self.assertEqual(result["start"], "N/A")
        self.assertEqual(result["end"], "N/A")


class TestGetDataStats(TestDataProcessor):
    def test_get_data_stats_complete_data(self):
        """Test getting statistics from complete data."""
        df = pd.DataFrame(
            {
                "UTCDateTime": pd.to_datetime(
                    ["2022-01-26 22:00:00", "2022-01-26 23:00:00"]
                ),
                "Latitude": [40.7128, 41.2033],
                "Longitude": [-74.0060, -73.1234],
                "State": ["New York", "Connecticut"],
                "CellType": ["LTE", "5G"],
            }
        )

        result = self.processor.get_data_stats(df)

        self.assertEqual(result["total_records"], 2)
        self.assertEqual(result["records_with_location"], 2)
        self.assertEqual(result["unique_states"], 2)
        self.assertIn("date_range", result)
        self.assertIn("cell_types", result)
        self.assertIn("states", result)
        self.assertEqual(result["cell_types"]["LTE"], 1)
        self.assertEqual(result["cell_types"]["5G"], 1)

    def test_get_data_stats_missing_columns(self):
        """Test getting statistics when some columns are missing."""
        df = pd.DataFrame({"Latitude": [40.7128], "Longitude": [-74.0060]})

        result = self.processor.get_data_stats(df)

        self.assertEqual(result["total_records"], 1)
        self.assertEqual(result["records_with_location"], 1)
        self.assertEqual(result["unique_states"], 0)
        self.assertEqual(result["cell_types"], {})

    def test_get_data_stats_empty_dataframe(self):
        """Test getting statistics from empty DataFrame."""
        df = pd.DataFrame()

        result = self.processor.get_data_stats(df)

        self.assertEqual(result["total_records"], 0)
        self.assertEqual(result["records_with_location"], 0)
        self.assertEqual(result["unique_states"], 0)


if __name__ == "__main__":
    unittest.main()
