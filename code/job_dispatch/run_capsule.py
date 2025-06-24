"""
Generates the input analysis model from the user provided query
"""

import argparse
import json
import logging
from pathlib import Path
import uuid
from typing import Union

import numpy as np
import pandas as pd
from tqdm import tqdm

from job_dispatch import utils
from aind_analysis_results.analysis_dispatch_model import AnalysisDispatchModel

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
        - `--use_data_asset_csv`: If true, read in list of data asset ids and use those instead of query
        - `--file_extension`: A string argument for specifying whether or not to find the file extension
        - `--split_files`: Whether or not to group the files into a single model or to split into seperate
        - `--num_parallel_workers`: The number of parallel workers to output, default is 50. Determined by min(length of results returned in query, 50).

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--docdb_query", type=str, default="")
    parser.add_argument("--use_data_asset_csv", type=int, default=0)
    parser.add_argument("--file_extension", type=str, default="")
    parser.add_argument("--split_files", type=int, default=1)
    parser.add_argument("--num_parallel_workers", type=int, default=50)

    return parser


def get_input_model_list(
    data_asset_ids: Union[list[str], list[list[str]]],
    file_extension: str = "",
    split_files: bool = True,
) -> list[AnalysisDispatchModel]:
    """
    Writes the input model with the S3 location from the query and input arguments

    Parameters
    ----------

    data_asset_ids: Union[list[str], list[list[str]], None]
        The data asset ids to get input models for. Either a flat list or nested list of lists.

    file_extension : str, optional
        The file extension to filter for when searching the S3 locations. Defaults to empty, meaning the bucket path will be returned from the query.

    split_files : bool, optional
        Whether or not to split files into seperate models or to store in one model as a single list.

    Returns
    -------
    list: AnalysisDispatchModel
        Returns a list of input analysis jobs
    """

    # Normalize to grouped format
    is_flat = True
    if isinstance(data_asset_ids, list) and all(
        isinstance(i, str) for i in data_asset_ids
    ):
        logger.info("Flat data asset ids list provided")
        grouped_asset_ids = [data_asset_ids]
    elif isinstance(data_asset_ids, list) and all(
        isinstance(i, list) for i in data_asset_ids
    ):
        logger.info("Nested data asset ids list provided")
        grouped_asset_ids = data_asset_ids
        is_flat = False

    all_grouped_models = []

    for group in grouped_asset_ids:
        s3_buckets, s3_asset_ids, s3_paths, s3_asset_names = utils.get_s3_input_information(
            data_asset_ids=group,
            file_extension=file_extension,
            split_files=split_files,
        )

        if is_flat:
            for index, s3_bucket in enumerate(s3_buckets):
                all_grouped_models.append(
                    AnalysisDispatchModel(
                        s3_location=[s3_bucket],
                        asset_id=[s3_asset_ids[index]],
                        file_location=[s3_paths[index]] if s3_paths else None,
                        asset_name=[s3_asset_names[index]],
                    )
                )
        else:
            all_grouped_models.append(
                AnalysisDispatchModel(
                    s3_location=s3_buckets,
                    asset_id=s3_asset_ids,
                    file_location=s3_paths if s3_paths else None,
                    asset_name=s3_asset_names,
                )
            )

    return all_grouped_models


def write_input_model_list(
    input_model_list: list[AnalysisDispatchModel],
    num_parallel_workers: int,
) -> None:
    """
    Distributes a list of input models across a specified number of parallel workers,
    writes the models to disk in JSON format, and logs the progress.

    Parameters
    ----------
    input_model_list : list of AnalysisDispatchModel
        A list of AnalysisDispatchModel instances to be processed and written to disk.

    num_parallel_workers : int
        The maximum number of parallel workers that can be used to process the input models.

    Returns
    -------
    None
        This function does not return any value. It writes JSON files to disk for each input model.
    """

    # Step 1: Split into worker batches
    num_actual_workers = min(len(input_model_list), num_parallel_workers)
    jobs_for_each_worker = np.array_split(input_model_list, num_actual_workers)

    # Step 2: Write output per job inside worker folder
    for worker_id, job_group in enumerate(
        tqdm(jobs_for_each_worker, desc="Distributing jobs")
    ):
        worker_folder = utils.RESULTS_PATH / f"{worker_id}"
        worker_folder.mkdir(parents=True, exist_ok=True)

        for job_id, job_model in enumerate(job_group):
            # Write input model
            with open(worker_folder / f"{uuid.uuid4()}.json", "w") as f:
                f.write(job_model.model_dump_json(indent=4))

        logger.info(f"{len(job_group)} jobs written to {worker_folder}")


def get_data_asset_ids(args) -> list[str]:
    """
    Retrieve a list of data asset IDs based on the provided arguments.

    Parameters
    ----------
    args : input arguments for determining which input to use - query or list of ids

    Returns
    -------
    list of str
        A list of data asset ID strings that match the provided filters.
    """
    if bool(args.use_data_asset_csv):
        data_asset_ids_path = tuple(utils.DATA_PATH.glob("*.csv"))
        if not data_asset_ids_path:
            raise FileNotFoundError("Using data asset ids, but no path to csv provided")

        data_asset_df = pd.read_csv(data_asset_ids_path[0])
        if data_asset_df["asset_id"].isna().all():
            raise ValueError("Asset id column is empty")

        data_asset_ids = data_asset_df["asset_id"].tolist()

    if args.docdb_query and not bool(args.use_data_asset_csv):
        logger.info("Using query")
        if isinstance(args.docdb_query, str) and Path(args.docdb_query).exists():
            logger.info(f"Query input as json file at path {Path(args.docdb_query)}")
            with open(Path(args.docdb_query), "r") as f:
                query = json.load(f)
        else:
            query = json.loads(args.docdb_query)

        logger.info(f"Query {query}")
        data_asset_ids = utils.get_data_asset_ids_from_query(query)

    logger.info(f"Returned {len(data_asset_ids)} records")
    return data_asset_ids


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = get_input_parser()
    args = parser.parse_args()
    logger.info(args)

    data_asset_ids = get_data_asset_ids(args)
    ### IF YOU WANT TO GROUP DATA ASSETS, REPLACE THIS TO GET GROUPED IDS
    ### OR RESTRUCTURE FLAT LIST INTO GROUPS

    input_model_list = get_input_model_list(
        data_asset_ids=data_asset_ids,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
    )

    write_input_model_list(input_model_list, args.num_parallel_workers)
