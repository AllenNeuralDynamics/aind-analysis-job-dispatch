"""
Generates the input analysis model from the user provided query
"""

import argparse
import json
import pathlib
import logging

from job_dispatch import utils
from job_dispatch.analysis_input_model import AnalysisSpecification, InputAnalysisModel

logger = logging.getLogger(__name__)

def get_input_parser() -> argparse.ArgumentParser:
    """
    Creates and returns an argument parser for input arguments.

    Parameters
    ----------
    None

    Returns
    -------
    argparse.ArgumentParser
        A configured ArgumentParser object with predefined command-line arguments for:
        - `--query`: A string argument for the query (default is an empty string).
        - `--analysis_name`: A string argument for the analysis name (default is an empty string).
        - `--analysis_version`: A string argument for the analysis version (default is an empty string).
        - `--analysis_libraries`: A string argument for the list of analysis libraries (default is an empty string).
        - `--analysis_parameters`: A string argument for the dict of analysis parameters (default is an empty string).

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default="")
    parser.add_argument("--analysis_name", type=str, default="")
    parser.add_argument("--analysis_version", type=str, default="")
    parser.add_argument("--analysis_libraries", type=str, default="")
    parser.add_argument("--analysis_parameters", type=str, default="")

    return parser


def write_input_model(docdb_query: dict, analysis_spec: AnalysisSpecification) -> None:
    """
    Writes the input model with the S3 location from the query and input arguments for each path returned from the query.

    Parameters
    ----------
    docdb_query : dict
        A dictionary representing the query to retrieve documents from the database.

    analysis_spec : AnalysisSpecification
        An object that contains the specifications for the analysis, including `analysis_name` and `analysis_version`.

    Returns
    -------
    None
        This function does not return any value. It writes the input analysis model to disk.
    """
    s3_paths = utils.get_s3_file_locations_from_docdb_query(docdb_query)
    
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

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = get_input_parser()
    args = parser.parse_args()
    if args.query == '':
        args.query = '{"name": "behavior_724910_2024-09-13_09-45-06"}'
        args.analysis_name = "Unit_Yield"
        args.analysis_version = "0.1.0"
        args.analysis_libraries = '["aind-ephys-utils"]'
        args.analysis_parameters = '{"alpha": "0.1"}'
    print(args)
    
    query = json.loads(args.query)
    analysis_spec = AnalysisSpecification(
        analysis_name=args.analysis_name,
        analysis_version=args.analysis_version,
        analysis_libraries_to_track=json.loads(args.analysis_libraries),
        analysis_parameters=json.loads(args.analysis_parameters),
    )

    print(analysis_spec)
    write_input_model(docdb_query=query, analysis_spec=analysis_spec)
