"""
Generates the input analysis model from the user provided query
"""

from job_dispatch.analysis_input_model import AnalysisSpec, InputAnalysisModel
import pathlib
import argparse
from job_dispatch import utils
import json


parser = argparse.ArgumentParser()
parser.add_argument("--query", type=str, default="")
parser.add_argument("--analysis_name", type=str, default="")
parser.add_argument("--analysis_version", type=str, default="")
parser.add_argument("--analysis_libraries", type=str, default="")
parser.add_argument("--analysis_parameters", type=str, default="")


def write_input_model(query: dict, analysis_spec: AnalysisSpec) -> None:
    """
    writes the input model with the s3 location from the query and input args for each path returned from the query
    """
    s3_paths = utils.get_s3_file_locations_from_docdb_query(query)
    for path in s3_paths:
        input_analysis_model = InputAnalysisModel(
            s3_location=path, analysis_spec=analysis_spec
        )
        # saving hash as session_analysis-name_analysis-version, can modify based on feedback
        with open(
            utils.RESULTS_PATH
            / f"{pathlib.Path(path).stem}_{analysis_spec.analysis_name}_{analysis_spec.analysis_version}.json",
            "w",
        ) as f:
            f.write(input_analysis_model.model_dump_json())


if __name__ == "__main__":
    args = parser.parse_args()
    query = json.loads(args.query)
    analysis_spec = AnalysisSpec(
        analysis_name=args.analysis_name,
        analysis_version=args.analysis_version,
        analysis_libraries_to_track=json.loads(args.analysis_libraries),
        analysis_parameters=json.loads(args.analysis_parameters),
    )

    write_input_model(query=query, analysis_spec=analysis_spec)
