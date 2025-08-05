"""
Generates the input analysis model from the user provided query
"""

import json
import logging
import math
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from analysis_pipeline_utils.analysis_dispatch_model import (
    AnalysisDispatchModel,
)
from analysis_pipeline_utils.utils_analysis_dispatch import (
    get_data_asset_paths_from_query,
    get_input_model_list,
)
from pydantic import Field
from pydantic_settings import BaseSettings
from tqdm import tqdm

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
        )[0],
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
    max_number_of_tasks_dispatched: int = Field(
        default=1000, description="Maximum number of tasks to be dispatched"
    )
    group_by: str = Field(default="", description="Field to group data by")
    input_directory: Path = Field(
        default=Path("/data"), description="Input directory"
    )
    output_directory: Path = Field(
        default=Path("/results"), description="Output directory"
    )


def write_input_model_list(
    input_model_list: list[AnalysisDispatchModel],
    tasks_per_job: int = 1,
    max_number_of_tasks_dispatched: int = 1000,
) -> None:
    """
    Distributes a list of input models across a specified number of tasks per job,
    writes the models to disk in JSON format, and logs the progress.

    Parameters
    ----------
    input_model_list : list of AnalysisDispatchModel
        A list of AnalysisDispatchModel instances to be processed and written to disk.

    tasks_per_job: int = 1 : int
        The number of tasks to group per job when dispatching

    max_number_of_tasks_dispatched: int, Default = 1000
        The maximum number of tasks to dispatch

    Returns
    -------
    None
        This function does not return any value.
        It writes JSON files to disk for each input model.
    """

    # Step 1: Split into tasks per job batches
    if tasks_per_job < 1:
        raise ValueError("tasks_per_job must be at least 1")

    logger.info(
        "Max number of tasks to dispatch "
        f"{max_number_of_tasks_dispatched}"
    )
    input_model_list = input_model_list[:max_number_of_tasks_dispatched]
    number_of_jobs = math.ceil(len(input_model_list) / tasks_per_job)
    tasks_for_each_job = np.array_split(input_model_list, number_of_jobs)
    logger.info(f"Tasks per job: {tasks_per_job}")

    # Step 2: Write output per task inside job folder
    for job_id, task_group in enumerate(
        tqdm(tasks_for_each_job, desc="Distributing jobs")
    ):
        job_folder = args.output_directory / f"{job_id}"
        job_folder.mkdir(parents=True, exist_ok=True)

        for task_id, task_model in enumerate(task_group):
            # Write input model
            with open(job_folder / f"{uuid.uuid4()}.json", "w") as f:
                f.write(task_model.model_dump_json(indent=4))

        logger.info(f"{len(task_group)} tasks written to {job_folder}")


def get_data_asset_paths(
    use_data_asset_csv=False, docdb_query=None, group_by=None, **kwargs
) -> list[str]:
    """
    Retrieve a list of data asset paths based on the provided arguments.

    Parameters
    ----------

    Returns
    -------
    list of str
        A list of data asset ID strings that match the provided filters.
    """
    if use_data_asset_csv:
        data_asset_ids_path = tuple(args.input_directory.glob("*.csv"))
        if not data_asset_ids_path:
            raise FileNotFoundError(
                "Using data asset ids, but no path to csv provided"
            )

        data_asset_df = pd.read_csv(data_asset_ids_path[0])
        if data_asset_df["asset_id"].isna().all():
            raise ValueError("Asset id column is empty")

        data_asset_ids = data_asset_df["asset_id"].tolist()
        data_asset_paths = get_data_asset_paths_from_query(
            query={"external_links.Code Ocean.0": {"$in": data_asset_ids}},
            group_by=args.group_by,
        )

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
        data_asset_paths = get_data_asset_paths_from_query(query, group_by)

    logger.info(f"Returned {len(data_asset_paths)} records")
    return data_asset_paths


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    args = InputSettings()
    logger.info(args)

    data_asset_paths = get_data_asset_paths(**vars(args))

    analysis_parameters_path = (
        args.input_directory / "analysis_parameters.json"
    )

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
        data_asset_paths=data_asset_paths,
        file_extension=args.file_extension,
        split_files=bool(args.split_files),
        distributed_analysis_parameters=distributed_parameters,
    )

    write_input_model_list(
        input_model_list,
        args.tasks_per_job,
        args.max_number_of_tasks_dispatched,
    )
