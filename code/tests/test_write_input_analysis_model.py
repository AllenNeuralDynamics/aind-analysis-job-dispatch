import json
import pathlib
import unittest
from unittest.mock import mock_open, patch

from job_dispatch import utils
from job_dispatch.run_capsule import write_input_model


class TestWriteInputModel(unittest.TestCase):
    @patch(
        "job_dispatch.utils.get_s3_file_locations_from_docdb_query"
    )  # Mock get_s3_file_locations_from_docdb_query
    @patch("builtins.open", new_callable=mock_open)  # Mock the open function
    @patch(
        "job_dispatch.analysis_input_model.InputAnalysisModel.model_dump_json"
    )  # Mock model_dump_json
    def test_write_input_model(
        self,
        mock_model_dump_json,
        mock_open,
        mock_get_s3_file_locations_from_docdb_query,
    ):
        # Setup mock return values for get_s3_file_locations_from_docdb_query
        mock_get_s3_file_locations_from_docdb_query.return_value = [
            ["s3://bucket/path/to"],
            ["12345"],
            ["s3://bucket/path/to/file1.nwb"],
        ]

        # Expected serialzed input model
        expected_json = {
            "location_bucket": "s3://bucket/path/to/",
            "location_asset_id": "12345",
            "location_uri": "s3://bucket/path/to/file1.nwb",
        }
        expected_json_string = json.dumps(expected_json)
        mock_model_dump_json.return_value = expected_json_string

        # Sample input arguments
        query = {
            "name": "behavior_769038_2025-02-10_13-16-09_processed_2025-02-11_07-14-26"
        }

        # Call the function
        write_input_model(query, file_extension="nwb")

        # Check that the file write was called with the expected file path
        mock_open.assert_any_call(
            utils.RESULTS_PATH / "to.json",
            "w",
        )


if __name__ == "__main__":
    unittest.main()
