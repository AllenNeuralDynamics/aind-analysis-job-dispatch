import json
import pathlib
import unittest
from unittest.mock import mock_open, patch

from job_dispatch import utils
from job_dispatch.analysis_input_model import AnalysisSpecification, InputAnalysisModel
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
            "s3://bucket/path/to/file1.nwb",
        ]

        # Expected serialzed input model
        expected_json = {
            "s3_location": "s3://bucket/path/to/file1.nwb",
            "analysis_spec": {
                "analysis_name": "Unit Yield",
                "analysis_version": "0.1.0",
                "analysis_libraries_to_track": ["aind-ephys-utils"],
                "analysis_parameters": {"alpha": "0.1"},
            },
        }
        expected_json_string = json.dumps(expected_json)
        mock_model_dump_json.return_value = expected_json_string

        # Sample input arguments
        query = {
            "name": "behavior_769038_2025-02-10_13-16-09_processed_2025-02-11_07-14-26"
        }
        analysis_spec = AnalysisSpecification(
            analysis_name="Unit Yield",
            analysis_version="0.1.0",
            analysis_libraries_to_track=["aind-ephys_utils"],
            analysis_parameters={"param1": "value1"},
        )

        # Call the function
        write_input_model(query, analysis_spec)

        # Check that the file write was called with the expected file path
        mock_open.assert_any_call(
            utils.RESULTS_PATH
            / f"{pathlib.Path('s3://bucket/path/to/file1.nwb').stem}_{analysis_spec.analysis_name}_{analysis_spec.analysis_version}.json",
            "w",
        )

        # Verify that model_dump_json was called to generate the expected JSON
        mock_model_dump_json.assert_any_call()

        # Check that the content written to the file matches the expected serialized JSON
        handle = mock_open()  # Access the mock file handle
        handle.write.assert_any_call(expected_json_string)


if __name__ == "__main__":
    unittest.main()
