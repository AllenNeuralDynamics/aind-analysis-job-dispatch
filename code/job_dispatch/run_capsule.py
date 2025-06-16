"""
Generates the input analysis model from the user provided query
"""

import argparse
import json
import logging
import pathlib
import uuid
from typing import Union

import numpy as np
import pandas as pd
from tqdm import tqdm

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
        - `--docdb_query`: A json string of query for getting data assets
        - `--use_data_assets`: If true, read in list of data asset ids and use those instead of query
        - `--file_extension`: A string argument for specifying whether or not to find the file extension
        - `--split_files`: Whether or not to group the files into a single model or to split into seperate
        - `--num_parallel_workers`: The number of parallel workers to output, default is 50. Determined by min(length of results returned in query, 50).

    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--docdb_query', type=str, default="")
    parser.add_argument('--use_data_assets', type=int, default=0)
    parser.add_argument("--file_extension", type=str, default="")
    parser.add_argument("--split_files", type=int, default=1)
    parser.add_argument("--num_parallel_workers", type=int, default=50)

    return parser



def get_input_model_list(
    docdb_query: Union[dict, None] = None,
    data_asset_ids: Union[list[str], list[list[str]], None] = None,
    file_extension: str = "",
    split_files: bool = True,
) -> list[InputAnalysisModel]:
    """
    Writes the input model with the S3 location from the query and input arguments

    Parameters
    ----------

    docdb_query : Union[dict, None]
        A dictionary representing the query to retrieve documents from the database.
    
    data_asset_ids: Union[list[str], list[list[str]], None]
        The data asset ids to get input models for. Either a flat list or nested list of lists.

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


    # Handle docdb_query-only mode
    if data_asset_ids is None:
        s3_buckets, s3_asset_ids, s3_paths, s3_asset_names = utils.get_s3_file_locations(
            query=docdb_query,
            data_asset_ids=data_asset_ids,
            file_extension=file_extension,
            split_files=split_files,
        )

        return [
            InputAnalysisModel(
                s3_location=bucket,
                location_asset_id=asset_id,
                file_extension_locations=paths if paths else None,
                asset_name=asset_name,
            )
            for bucket, asset_id, paths, asset_name in zip(s3_buckets, s3_asset_ids, s3_paths, s3_asset_names)
        ]

    # Normalize to grouped format
    is_flat = True
    if isinstance(data_asset_ids, list) and all(isinstance(i, str) for i in data_asset_ids):
        logger.info("Flat data asset ids list provided")
        grouped_asset_ids = [data_asset_ids]
    elif isinstance(data_asset_ids, list) and all(isinstance(i, list) for i in data_asset_ids):
        logger.info("Nested data asset ids list provided")
        grouped_asset_ids = data_asset_ids
        is_flat = False
    else:
        raise ValueError("data_asset_ids must be None, a list of strings, or list of list of strings")

    all_grouped_models = []

    for group in grouped_asset_ids:
        s3_buckets, s3_asset_ids, s3_paths, s3_asset_names = utils.get_s3_file_locations(
            query=docdb_query,
            data_asset_ids=group,
            file_extension=file_extension,
            split_files=split_files,
        )

        if is_flat:
            for index, s3_bucket in enumerate(s3_buckets):
                all_grouped_models.append(
                    InputAnalysisModel(
                        s3_location=s3_bucket,
                        location_asset_id=s3_asset_ids[index],
                        file_extension_locations=s3_paths[index] if s3_paths else None,
                        asset_name=s3_asset_names[index],
                    )
                )
        else:
            all_grouped_models.append(
                InputAnalysisModel(
                    s3_location=s3_buckets,
                    location_asset_id=s3_asset_ids,
                    file_extension_locations=s3_paths if s3_paths else None,
                    asset_name=s3_asset_names,
                )
            )

    return all_grouped_models


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
                / f"{str(uuid.uuid4())}.json",
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

    query = None
    data_asset_ids = None

    if bool(args.use_data_assets):
        data_asset_ids_path = tuple(utils.DATA_PATH.glob("*.csv"))
        if not data_asset_ids_path:
            raise FileNotFoundError("Using data asset ids, but no path to csv provided")
        
        data_asset_df = pd.read_csv(data_asset_ids_path[0])
        if data_asset_df["asset_id"].isna().all():
            raise ValueError("Asset id column is empty")
        
        data_asset_ids = data_asset_df["asset_id"].tolist()
            
    if args.docdb_query and not bool(args.use_data_assets):
        query = json.loads(args.docdb_query)
    
    #data_asset_ids = [[data_asset_ids[0]], [data_asset_ids[1], data_asset_ids[2]]] # GROUPING OF DATA ASSETS - REPLACE WITH FUNCTION
    input_model_list = get_input_model_list(
        docdb_query=query,
        data_asset_ids=data_asset_ids,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
    )

    write_input_model_list(input_model_list, args.num_parallel_workers)
