"""
Generates the input analysis model from the user provided query
"""

import argparse
import json
import logging
import pathlib

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
    parser.add_argument("--file_extension", type=str, default="")
    parser.add_argument("--split_files", type=int, default=1)

    return parser


def write_input_model(
    docdb_query: dict,
    analysis_spec: AnalysisSpecification,
    file_extension: str = "",
    split_files: bool = True,
) -> None:
    """
    Writes the input model with the S3 location from the query and input arguments for each path returned from the query.

    Parameters
    ----------
    docdb_query : dict
        A dictionary representing the query to retrieve documents from the database.

    analysis_spec : AnalysisSpecification
        An object that contains the specifications for the analysis, including `analysis_name` and `analysis_version`.

    file_extension : str, optional
        The file extension to filter for when searching the S3 locations. Defaults to empty, meaning the bucket path will be returned from the query.

    split_files : bool, optional
        Whether or not to split files into seperate models or to store in one model as a single list.

    Returns
    -------
    None
        This function does not return any value. It writes the input analysis model to disk.
    """
    s3_paths = utils.get_s3_file_locations_from_docdb_query(
        docdb_query, file_extension=file_extension, split_files=split_files
    )

    for path in s3_paths:
        input_analysis_model = InputAnalysisModel(
            location_uri=path, analysis_spec=analysis_spec
        )
        # saving hash as session_analysis-name_analysis-version, can modify based on feedback
        with open(
            utils.RESULTS_PATH
            / f"{pathlib.Path(path).stem}_{analysis_spec.analysis_name}_{analysis_spec.analysis_version}.json",
            "w",
        ) as f:
            f.write(input_analysis_model.model_dump_json(indent=4))

    logger.info(f"{len(s3_paths)} input analysis models written to {utils.RESULTS_PATH}")


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = get_input_parser()
    args = parser.parse_args()
    if args.query == "":
        args.query = '{"name": {"$regex": "^behavior_741213.*processed"}}'
        args.analysis_name = "Unit_Yield"
        args.analysis_version = "0.1.0"
        args.analysis_libraries = '["aind-ephys-utils"]'
        args.analysis_parameters = '{"alpha": "0.1"}'
        args.file_extension = ""
        args.split_files = bool(1)
    logger.info(args)

    query = json.loads(args.query)
    analysis_spec = AnalysisSpecification(
        analysis_name=args.analysis_name,
        analysis_version=args.analysis_version,
        analysis_libraries_to_track=json.loads(args.analysis_libraries),
        analysis_parameters=json.loads(args.analysis_parameters),
    )
    logger.info(analysis_spec)

    write_input_model(
        docdb_query=query,
        analysis_spec=analysis_spec,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
    )
