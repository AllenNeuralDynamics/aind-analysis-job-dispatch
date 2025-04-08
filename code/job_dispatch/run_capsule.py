"""
Generates the input analysis model from the user provided query
"""

import argparse
import json
import logging
import numpy as np
import pathlib

from job_dispatch import utils
from job_dispatch.analysis_input_model import InputAnalysisModel
from tqdm import tqdm

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
        - `--file_extension`: A string argument for specifying whether or not to find the file extension
        - `--split_files`: Whether or not to group the files into a single model or to split into seperate
        - `--num_parallel_workers`: The number of parallel workers to output, default is 50. Determined by min(length of results returned in query, 50).

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default="")
    parser.add_argument("--file_extension", type=str, default="")
    parser.add_argument("--split_files", type=int, default=1)
    parser.add_argument("--num_parallel_workers", type=int, default=50)

    return parser


def get_input_model_list(
    docdb_query: dict,
    file_extension: str = "",
    split_files: bool = True,
) -> list[InputAnalysisModel]:
    """
    Writes the input model with the S3 location from the query and input arguments for each path returned from the query.

    Parameters
    ----------
    docdb_query : dict
        A dictionary representing the query to retrieve documents from the database.

    file_extension : str, optional
        The file extension to filter for when searching the S3 locations. Defaults to empty, meaning the bucket path will be returned from the query.

    split_files : bool, optional
        Whether or not to split files into seperate models or to store in one model as a single list.

    Returns
    -------
    list: InputAnalysisModel
        Returns a list of input analysis jobs 
    """
    s3_buckets, s3_asset_ids, s3_paths = utils.get_s3_file_locations_from_docdb_query(
        docdb_query, file_extension=file_extension, split_files=split_files
    )

    input_model_jobs = []

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
        
        input_model_jobs.append(input_analysis_model)

    return input_model_jobs

def write_input_model_list(input_model_list: list[InputAnalysisModel], num_parallel_workers: int) -> None:
    """
    Distributes a list of input models across a specified number of parallel workers, 
    writes the models to disk in JSON format, and logs the progress.

    Parameters
    ----------
    input_model_list : list of InputAnalysisModel
        A list of InputAnalysisModel instances to be processed and written to disk.
        
    num_parallel_workers : int
        The maximum number of parallel workers that can be used to process the input models.

    Returns
    -------
    None
        This function does not return any value. It writes JSON files to disk for each input model.
    """

    num_actual_workers = min(len(input_model_list), num_parallel_workers)
    jobs_for_each_worker = np.array_split(input_model_list, num_actual_workers)
    
    for n_worker, input_model_jobs in tqdm(
        enumerate(jobs_for_each_worker), 
        desc="Assigning jobs to workers",
        total=len(jobs_for_each_worker)
    ):
        results_directory_worker_path = utils.RESULTS_PATH / f"{n_worker}"
        if not results_directory_worker_path.exists():
            results_directory_worker_path.mkdir()

        for input_model_job in input_model_jobs:
            with open(
                results_directory_worker_path / f"{input_model_job.location_asset_id}.json",
                "w",
            ) as f:
                f.write(input_model_job.model_dump_json(indent=4))

        logger.info(
            f"{len(input_model_jobs)} input analysis models written to {utils.RESULTS_PATH} for worker {n_worker}"
        )

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = get_input_parser()
    args = parser.parse_args()
    if args.query == "":
        args.query = '{"name": {"$regex": "^behavior_741213.*processed"}}'
        args.file_extension = "nwb"
        args.split_files = bool(1)
        args.num_parallel_workers = 50
    logger.info(args)

    query = json.loads(args.query)

    input_model_list = get_input_model_list(
        docdb_query=query,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
    )

    write_input_model_list(input_model_list, args.num_parallel_workers)
