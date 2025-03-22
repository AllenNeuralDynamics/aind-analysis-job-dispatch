import logging
import unittest
from typing import List, Union
from unittest.mock import MagicMock, patch

from job_dispatch.utils import get_s3_file_locations_from_docdb_query


class TestGetS3FileLocationsFromDocdbQuery(unittest.TestCase):

    @patch("s3fs.S3FileSystem")
    @patch("job_dispatch.utils.docdb_api_client.retrieve_docdb_records")
    def test_get_s3_file_locations_from_docdb_query(
        self, mock_retrieve_docdb_records, MockS3FileSystem
    ):
        # Test setup
        query = {"filter": "example"}  # Example query
        file_extension = ".txt"
        split_files = True

        # Mock the docdb response
        mock_response = [
            {
                "location": "my-bucket/first-file",
                "external_links": {"Code Ocean": ["asset-id-1"]},
            },
        ]
        mock_retrieve_docdb_records.return_value = mock_response

        # Mock S3FileSystem.glob() method to simulate file paths
        mock_s3fs_instance = MockS3FileSystem.return_value
        mock_s3fs_instance.glob.return_value = [
            "my-bucket/first-file/file1.txt",
        ]

        # Call the function under test
        s3_buckets, s3_asset_ids, s3_paths = get_s3_file_locations_from_docdb_query(
            query=query, file_extension=file_extension, split_files=split_files
        )

        # Assertions
        self.assertEqual(s3_buckets, ["s3://my-bucket/first-file"])
        self.assertEqual(s3_asset_ids, ["asset-id-1"])
        self.assertEqual(s3_paths, ["s3://my-bucket/first-file/file1.txt"])

    @patch("s3fs.S3FileSystem")
    @patch("job_dispatch.utils.docdb_api_client.retrieve_docdb_records")
    def test_get_s3_file_locations_no_files(
        self, mock_retrieve_docdb_records, MockS3FileSystem
    ):
        # Test when no matching files are found in the S3 bucket
        query = {"filter": "example"}  # Example query
        file_extension = ".txt"
        split_files = True

        # Mock the docdb response
        mock_response = [
            {
                "location": "my-bucket/no-file",
                "external_links": {"Code Ocean": ["asset-id-1"]},
            }
        ]
        mock_retrieve_docdb_records.return_value = mock_response

        # Mock S3FileSystem.glob() to return no files
        mock_s3fs_instance = MockS3FileSystem.return_value
        mock_s3fs_instance.glob.return_value = []

        # Call the function and assert exception is raised
        with self.assertRaises(FileNotFoundError):
            get_s3_file_locations_from_docdb_query(
                query=query, file_extension=file_extension, split_files=split_files
            )

    @patch("s3fs.S3FileSystem")
    @patch("job_dispatch.utils.docdb_api_client.retrieve_docdb_records")
    def test_get_s3_file_locations_no_extension(
        self, mock_retrieve_docdb_records, MockS3FileSystem
    ):
        # Test with no file extension provided
        query = {"filter": "example"}  # Example query
        file_extension = ""
        split_files = True

        # Mock the docdb response
        mock_response = [
            {
                "location": "my-bucket/first-file",
                "external_links": {"Code Ocean": ["asset-id-1"]},
            }
        ]
        mock_retrieve_docdb_records.return_value = mock_response

        # Mock S3FileSystem.glob() to return file paths
        mock_s3fs_instance = MockS3FileSystem.return_value
        mock_s3fs_instance.glob.return_value = [
            "my-bucket/first-file/file1.txt",
        ]

        # Call the function under test
        s3_buckets, s3_asset_ids, s3_paths = get_s3_file_locations_from_docdb_query(
            query=query, file_extension=file_extension, split_files=split_files
        )

        # Assertions (file paths are returned even if no extension is provided)
        self.assertEqual(s3_buckets, ["s3://my-bucket/first-file"])
        self.assertEqual(s3_asset_ids, ["asset-id-1"])
        self.assertEqual(s3_paths, [])

    @patch("s3fs.S3FileSystem")
    @patch("job_dispatch.utils.docdb_api_client.retrieve_docdb_records")
    def test_get_s3_file_locations_split_files_false(
        self, mock_retrieve_docdb_records, MockS3FileSystem
    ):
        # Test with split_files set to False
        query = {"filter": "example"}  # Example query
        file_extension = ".txt"
        split_files = False

        # Mock the docdb response
        mock_response = [
            {
                "location": "my-bucket/first-file",
                "external_links": {"Code Ocean": ["asset-id-1"]},
            }
        ]
        mock_retrieve_docdb_records.return_value = mock_response

        # Mock S3FileSystem.glob() to return file paths
        mock_s3fs_instance = MockS3FileSystem.return_value
        mock_s3fs_instance.glob.return_value = ["my-bucket/first-file/file1.txt"]

        # Call the function under test
        s3_buckets, s3_asset_ids, s3_paths = get_s3_file_locations_from_docdb_query(
            query=query, file_extension=file_extension, split_files=split_files
        )

        # Assertions
        self.assertEqual(s3_buckets, ["s3://my-bucket/first-file"])
        self.assertEqual(s3_asset_ids, ["asset-id-1"])
        self.assertEqual(s3_paths, [["s3://my-bucket/first-file/file1.txt"]])


if __name__ == "__main__":
    unittest.main()
