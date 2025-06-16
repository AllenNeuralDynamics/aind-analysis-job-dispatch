import unittest
from unittest.mock import patch, MagicMock
from typing import List
from job_dispatch.run_capsule import get_input_model_list
from job_dispatch.analysis_input_model import InputAnalysisModel

class TestGetInputModelList(unittest.TestCase):
    @patch('job_dispatch.analysis_input_model.InputAnalysisModel')
    @patch("job_dispatch.utils.get_s3_file_locations_from_docdb_query")
    @patch("job_dispatch.utils.docdb_api_client.retrieve_docdb_records")
    def test_get_input_model_list(self, MockInputAnalysisModel, mock_get_s3_file_locations_from_docdb_query, mock_records_from_docdb):
        # Define the mock return values for `get_s3_file_locations_from_docdb_query`
        mock_get_s3_file_locations_from_docdb_query.return_value = (
            ['bucket1'],
            ['asset_id1'],
            ['path1']
        )


        # Define the input arguments
        docdb_query = {'key': 'value'}
        file_extension = '.json'
        split_files = True

        # Call the function we're testing
        result = get_input_model_list(docdb_query, file_extension, split_files)

        # Check that `get_s3_file_locations_from_docdb_query` was called with correct arguments
        mock_get_s3_file_locations_from_docdb_query.assert_called_once_with(
            docdb_query, file_extension=file_extension, split_files=split_files
        )

        # Check the structure and values of the returned result
        self.assertEqual(len(result), 1)  # We expect two results

        # Validate the result list contents
        self.assertIsInstance(result[0], InputAnalysisModel)
        self.assertEqual(result[0].location_bucket, 'bucket1')
        self.assertEqual(result[0].location_asset_id, 'asset_id1')
        self.assertEqual(result[0].location_uri, 'path1')

if __name__ == '__main__':
    unittest.main()
