import unittest
from typing import List, Union
from unittest.mock import MagicMock, patch


class TestGetS3FileLocationsFromDocdbQuery(unittest.TestCase):

    @patch("s3fs.S3FileSystem")
    @patch("job_dispatch.utils.docdb_api_client.retrieve_docdb_records")
    def test_get_s3_file_locations_from_docdb_query(
        self, mock_retrieve_docdb_records, MockS3FileSystem
    ):
        # Setup mock data for docdb response
        docdb_query = {"filter_key": "filter_value"}
        mock_records = [{"location": "bucket1/path/to/file1"}]

        # Mock the response of docdb API call
        mock_retrieve_docdb_records.return_value = mock_records

        # Setup mock for S3 file system
        mock_s3 = MagicMock()
        MockS3FileSystem.return_value = mock_s3
        mock_s3.glob.return_value = [
            "bucket1/path/to/file1.csv",
            "bucket1/path/to/file1.csv",
        ]

        # Test when file_extension is provided, but split_files is False
        file_extension = ".csv"
        split_files = False
        expected_result = [
            ["s3://bucket1/path/to/file1.csv", "s3://bucket1/path/to/file1.csv"]
        ]

        # Call the function
        from job_dispatch.utils import get_s3_file_locations_from_docdb_query

        result = get_s3_file_locations_from_docdb_query(
            docdb_query, file_extension, split_files
        )

        # Assertions
        mock_retrieve_docdb_records.assert_called_once_with(
            filter_query=docdb_query, projection={"location": 1}
        )
        mock_s3.glob.assert_called_with("bucket1/path/to/file1/**/*" + file_extension)
        self.assertEqual(result, expected_result)

        # Test when split_files is True
        split_files = True
        expected_result_split_files = [
            "s3://bucket1/path/to/file1.csv",
            "s3://bucket1/path/to/file1.csv",
        ]

        # Call the function again
        result_split_files = get_s3_file_locations_from_docdb_query(
            docdb_query, file_extension, split_files
        )

        # Assertions
        self.assertEqual(result_split_files, expected_result_split_files)

        # Test when file_extension is not provided
        file_extension = ""
        expected_result_no_extension = ["s3://bucket1/path/to/file1"]

        result_no_extension = get_s3_file_locations_from_docdb_query(
            docdb_query, file_extension, split_files
        )

        # Assertions
        self.assertEqual(result_no_extension, expected_result_no_extension)


if __name__ == "__main__":
    unittest.main()
