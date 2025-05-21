"""
Generates the input analysis model from the user provided query
"""

import argparse
import json
import logging
import pathlib
from typing import Union

import numpy as np
from tqdm import tqdm

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
        - `--file_extension`: A string argument for specifying whether or not to find the file extension
        - `--split_files`: Whether or not to group the files into a single model or to split into seperate
        - `--num_parallel_workers`: The number of parallel workers to output, default is 50. Determined by min(length of results returned in query, 50).

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--file_extension", type=str, default="")
    parser.add_argument("--split_files", type=int, default=1)
    parser.add_argument("--num_parallel_workers", type=int, default=50)

    return parser


def get_analysis_specifications() -> list[AnalysisSpecification]:
    """
    Returns a list of analysis specifications provided by the user
    THE FIELDS MUST BE REPLACED WITH USERD DEFINED ANALYSIS SPECIFICATIONS
    """
    analysis_specifications = []
    ### CREATE DESIRED NUMBER OF ANALYSIS SPEC HERE.
    ### REPLACE BELOW
    analysis_specification = AnalysisSpecification(
        analysis_name="Unit Yield",
        analysis_version="v0.0.1",
        analysis_libraries_to_track=["aind-ephys-utils"],
        analysis_parameters={"isi_violations": 0.5},
    )
    another_specification = AnalysisSpecification(
        analysis_name="Drift",
        analysis_version="v0.0.1",
        analysis_libraries_to_track=["aind-ephys-utils"],
    )
    analysis_specifications.append(analysis_specification)
    analysis_specifications.append(another_specification)
    return analysis_specifications


def get_input_model_list(
    analysis_specifications: list[AnalysisSpecification],
    docdb_query: Union[dict, None] = None,
    data_asset_ids: Union[list[str], None] = None,
    file_extension: str = "",
    split_files: bool = True,
) -> list[InputAnalysisModel]:
    """
    Writes the input model with the S3 location from the query and input arguments

    Parameters
    ----------
    analysis_specifications: list[AnalysisSpecification]
        The list of analysis to run on data 

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
    if docdb_query is None and data_asset_ids is None:
        raise ValueError(
            "Either one of docdb query or list of data asset ids must be provided"
        )

    s3_buckets, s3_asset_ids, s3_paths, s3_asset_names = utils.get_s3_file_locations(
        query=docdb_query,
        data_asset_ids=data_asset_ids,
        file_extension=file_extension,
        split_files=split_files,
    )

    input_model_jobs = []

    for index, bucket in enumerate(s3_buckets):
        s3_asset_id = s3_asset_ids[index]
        s3_asset_name = s3_asset_names[index]
        s3_bucket_paths = None
        if s3_paths:
            s3_bucket_paths = s3_paths[index]

        for analysis_specification in analysis_specifications:
            if s3_bucket_paths is not None:
                input_analysis_model = InputAnalysisModel(
                    s3_location=bucket,
                    location_asset_id=s3_asset_id,
                    location_uri=s3_bucket_paths,
                    asset_name=s3_asset_name,
                    parameters=analysis_specification,
                )
            else:
                input_analysis_model = InputAnalysisModel(
                    s3_location=bucket,
                    location_asset_id=s3_asset_id,
                    asset_name=s3_asset_name,
                    parameters=analysis_specification,
                )
            input_model_jobs.append(input_analysis_model)

    return input_model_jobs


def write_input_model_list(
    input_model_list: list[InputAnalysisModel], num_parallel_workers: int
) -> None:
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
        total=len(jobs_for_each_worker),
    ):
        results_directory_worker_path = utils.RESULTS_PATH / f"{n_worker}"
        if not results_directory_worker_path.exists():
            results_directory_worker_path.mkdir()

        for input_model_job in input_model_jobs:
            with open(
                results_directory_worker_path
                / f"{input_model_job.location_asset_id}.json",
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
    logger.info(args)

    # REPLACE QUERY WITH DESIRED ONE
    query = {"name": {"$regex": "^behavior_741213.*processed"}}
    # query = None

    # REPLACE WITH DATA ASSET IDS IF USING THAT METHOD AND SET QUERY TO None
    data_asset_ids = None
    # data_asset_ids = ["93c1606f-4c0b-4638-97b1-0f1a3756d9c2", "02f84cad-fe35-4c82-a5da-c10921fb7869", "d87d3913-6d97-4cdb-8132-b043f4a10fa2"]
    
    analysis_specifications = get_analysis_specifications() # GO TO THIS FUNCTION AND REPLACE WITH DESIRED ANALYSIS SPECS

    input_model_list = get_input_model_list(
        analysis_specifications=analysis_specifications,
        docdb_query=query,
        data_asset_ids=data_asset_ids,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
    )

    write_input_model_list(input_model_list, args.num_parallel_workers)
