"""
Generates the input analysis model from the user provided query
"""

import argparse
import json
import logging
import pathlib

from job_dispatch import utils
from job_dispatch.analysis_input_model import InputAnalysisModel

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
        - `--file_extension': A string argument for specifying whether or not to find the file extension
        - `--split_files': Whether or not to group the files into a single model or to split into seperate

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default="")
    parser.add_argument("--file_extension", type=str, default="")
    parser.add_argument("--split_files", type=int, default=1)

    return parser


def write_input_model(
    docdb_query: dict,
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
    s3_buckets, s3_asset_ids, s3_paths = utils.get_s3_file_locations_from_docdb_query(
        docdb_query, file_extension=file_extension, split_files=split_files
    )

    for index, bucket in enumerate(s3_buckets):
        s3_asset_id = s3_asset_ids[index]
        if s3_paths:
            s3_bucket_paths = s3_paths[index]
            input_analysis_model = InputAnalysisModel(
                location_bucket=bucket,
                location_asset_id=s3_asset_id,
                location_uri=s3_bucket_paths,
            )
        else:
            input_analysis_model = InputAnalysisModel(
                location_bucket=bucket, location_asset_id=s3_asset_id
            )
        # saving hash as session_analysis-name_analysis-version, can modify based on feedback
        with open(
            utils.RESULTS_PATH / f"{pathlib.Path(bucket).stem}.json",
            "w",
        ) as f:
            f.write(input_analysis_model.model_dump_json(indent=4))

    logger.info(
        f"{len(s3_buckets)} input analysis models written to {utils.RESULTS_PATH}"
    )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = get_input_parser()
    args = parser.parse_args()
    if args.query == "":
        args.query = '{"name": {"$regex": "^behavior_741213.*processed"}}'
        args.file_extension = ""
        args.split_files = bool(1)
    logger.info(args)

    query = json.loads(args.query)

    write_input_model(
        docdb_query=query,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
    )
