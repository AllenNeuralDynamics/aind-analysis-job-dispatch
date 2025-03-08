import unittest
from unittest.mock import MagicMock, patch
import s3fs
from job_dispatch.utils import get_s3_file_locations_from_docdb_query


class TestGetS3FileLocationsFromDocdbQuery(unittest.TestCase):
    @patch("s3fs.S3FileSystem")  # Mock s3fs.S3FileSystem
    @patch(
        "job_dispatch.utils.docdb_api_client.retrieve_docdb_records"
    )  # Mock docdb_api_client.retrieve_docdb_records
    def test_get_s3_file_locations(self, mock_retrieve_docdb_records, MockS3FileSystem):
        # Setup mock return values
        mock_s3_fs = MockS3FileSystem.return_value
        mock_s3_fs.glob.return_value = ["bucket/path/to/file1.nwb"]

        mock_retrieve_docdb_records.return_value = [
            {"location": "bucket/path/to"},
        ]

        query = {
            "name": "behavior_769038_2025-02-10_13-16-09_processed_2025-02-11_07-14-26"
        }
        file_extension = "nwb"

        # Call the function
        s3_paths = get_s3_file_locations_from_docdb_query(query, file_extension)

        # Check the expected result
        self.assertEqual(s3_paths, ["s3://bucket/path/to/file1.nwb"])

        # Verify the interactions with the mocks
        mock_retrieve_docdb_records.assert_called_with(
            filter_query=query, projection={"location": 1}
        )
        mock_s3_fs.glob.assert_any_call(f"bucket/path/to/*/*.{file_extension}")


if __name__ == "__main__":
    unittest.main()
