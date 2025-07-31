"""
Generates the input analysis model from the user provided query
"""

import json
import logging
import math
import uuid
from pathlib import Path
from typing import Any, Union

import numpy as np
import pandas as pd
from analysis_pipeline_utils.analysis_dispatch_model import (
    AnalysisDispatchModel,
)
from pydantic import Field
from pydantic_settings import BaseSettings
from tqdm import tqdm

import utils

logger = logging.getLogger(__name__)


class InputSettings(BaseSettings, cli_parse_args=True):
    """
    Pydantic settings model for input arguments.
    """

    docdb_query: str = Field(
        default="",
        description=(
            "JSON string of query "
            "for getting data assets or path to query json file",
        )[0]
    )
    use_data_asset_csv: int = Field(
        default=0,
        description="Use CSV list of data asset IDs instead of a query",
    )
    file_extension: str = Field(
        default="", description="Specify file extension filter"
    )
    split_files: int = Field(
        default=1, description="Whether to split files into separate models"
    )
    tasks_per_job: int = Field(
        default=1, description="Number of tasks per job"
    )
    group_by: str = Field(default="", description="Field to group data by")
    input_directory: Path = Field(
        default=Path("/data"), description="Input directory"
    )
    output_directory: Path = Field(
        default=Path("/results"), description="Output directory"
    )


def get_input_model_list(
    data_asset_ids: Union[list[str], list[list[str]]],
    file_extension: str = "",
    split_files: bool = True,
    distributed_analysis_parameters: Union[list[dict[str, Any]], None] = None,
) -> list[AnalysisDispatchModel]:
    """
    Writes the input model with the S3 location from the query and input arguments

    Parameters
    ----------

    data_asset_ids: Union[list[str], list[list[str]], None]
        The data asset ids to get input models for.
        Either a flat list or nested list of lists.

    file_extension : str, optional
        The file extension to filter for when searching the S3 locations.
        Defaults to empty, meaning the bucket path
        will be returned from the query.

    split_files : bool, optional
        Whether or not to split files into seperate models
        or to store in one model as a single list.

    distributed_analysis_parameters: Union[list[dict[str, Any]], None]
        List of dicts of analysis parameters.
        The dispatch will compute the product over
        input data and analysis dict for each in list.

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
        s3_buckets, s3_paths = utils.get_s3_input_information(
            data_asset_paths=group,
            file_extension=file_extension,
            split_files=split_files,
        )

        if not s3_buckets:
            continue
            
        if is_flat:
            for index, s3_bucket in enumerate(s3_buckets):
                if distributed_analysis_parameters is None:
                    all_grouped_models.append(
                        AnalysisDispatchModel(
                            s3_location=[s3_bucket],
                            file_location=(
                                [s3_paths[index]] if s3_paths else None
                            ),
                        )
                    )
                else:
                    for parameters in distributed_analysis_parameters:
                        all_grouped_models.append(
                            AnalysisDispatchModel(
                                s3_location=[s3_bucket],
                                file_location=(
                                    [s3_paths[index]] if s3_paths else None
                                ),
                                distributed_parameters=parameters,
                            )
                        )
        else:
            if distributed_analysis_parameters is None:
                all_grouped_models.append(
                    AnalysisDispatchModel(
                        s3_location=s3_buckets,
                        file_location=s3_paths if s3_paths else None,
                    )
                )
            else:
                for parameters in distributed_analysis_parameters:
                    all_grouped_models.append(
                        AnalysisDispatchModel(
                            s3_location=s3_buckets,
                            file_location=s3_paths if s3_paths else None,
                            distributed_parameters=parameters,
                        )
                    )

    return all_grouped_models


def write_input_model_list(
    input_model_list: list[AnalysisDispatchModel], tasks_per_job: int = 1
) -> None:
    """
    Distributes a list of input models across a specified number of parallel workers,
    writes the models to disk in JSON format, and logs the progress.

    Parameters
    ----------
    input_model_list : list of AnalysisDispatchModel
        A list of AnalysisDispatchModel instances to be processed and written to disk.

    tasks_per_job: int = 1 : int
        The number of tasks to group per job when dispatching

    Returns
    -------
    None
        This function does not return any value.
        It writes JSON files to disk for each input model.
    """

    # Step 1: Split into worker batches
    if tasks_per_job < 1:
        raise ValueError("tasks_per_job must be at least 1")

    number_of_jobs = math.ceil(len(input_model_list) / tasks_per_job)
    jobs_for_each_worker = np.array_split(input_model_list, number_of_jobs)
    logger.info(f"Tasks per job: {tasks_per_job}")

    # Step 2: Write output per job inside worker folder
    for worker_id, job_group in enumerate(
        tqdm(jobs_for_each_worker, desc="Distributing jobs")
    ):
        worker_folder = args.output_directory / f"{worker_id}"
        worker_folder.mkdir(parents=True, exist_ok=True)

        for job_id, job_model in enumerate(job_group):
            # Write input model
            with open(worker_folder / f"{uuid.uuid4()}.json", "w") as f:
                f.write(job_model.model_dump_json(indent=4))

        logger.info(f"{len(job_group)} jobs written to {worker_folder}")


def get_data_asset_ids(
    use_data_asset_csv=False, docdb_query=None, group_by=None, **kwargs
) -> list[str]:
    """
    Retrieve a list of data asset IDs based on the provided arguments.

    Parameters
    ----------

    Returns
    -------
    list of str
        A list of data asset ID strings that match the provided filters.
    """
    if use_data_asset_csv:
        data_asset_ids_path = tuple(utils.DATA_PATH.glob("*.csv"))
        if not data_asset_ids_path:
            raise FileNotFoundError(
                "Using data asset ids, but no path to csv provided"
            )

        data_asset_df = pd.read_csv(data_asset_ids_path[0])
        if data_asset_df["asset_id"].isna().all():
            raise ValueError("Asset id column is empty")

        data_asset_ids = data_asset_df["asset_id"].tolist()

    elif docdb_query:
        logger.info("Using query")
        if (
            isinstance(args.docdb_query, str)
            and Path(args.docdb_query).exists()
        ):
            logger.info(
                f"Query input as json file at path {Path(args.docdb_query)}"
            )
            with open(Path(args.docdb_query), "r") as f:
                query = json.load(f)
        else:
            query = json.loads(args.docdb_query)

        logger.info(f"Query {query}")
        data_asset_ids = utils.get_data_asset_ids_from_query(query, group_by)

    logger.info(f"Returned {len(data_asset_ids)} records")
    return data_asset_ids


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    args = InputSettings()
    logger.info(args)

    data_asset_ids = get_data_asset_ids(**vars(args))

    analysis_parameters_path = args.input_directory / "analysis_parameters.json"

    if analysis_parameters_path.exists():
        with open(analysis_parameters_path, "r") as f:
            distributed_parameters = json.load(f).get("distributed_parameters")
        if distributed_parameters:
            logger.info(
                f"Found analysis parameters json file "
                f"with {len(distributed_parameters)} sets of parameters "
                "Will compute product over parameters"
            )
    else:
        distributed_parameters = None
    input_model_list = get_input_model_list(
        data_asset_ids=data_asset_ids,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
        distributed_analysis_parameters=distributed_parameters,
    )

    write_input_model_list(input_model_list, args.tasks_per_job)
