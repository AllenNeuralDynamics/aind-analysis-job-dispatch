"""
Generates the input analysis model from the user provided query
"""

import json
import logging
from pathlib import Path
from typing import Optional, List
from analysis_pipeline_utils.utils_analysis_dispatch import (
    get_data_asset_records,
    get_input_model_list,
    write_input_model_list,
    filter_processed_jobs,
)
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AnalysisDispatchSettings(BaseSettings, cli_parse_args=True):
    """
    Pydantic settings model for input arguments.
    """

    docdb_query: str = Field(
        default="",
        description="JSON string of query for getting data assets or path to query json file",
    )
    use_data_asset_csv: bool = Field(
        default=False,
        description="Use CSV list of data asset IDs instead of a query",
    )
    file_extension: Optional[str] = Field(
        default=None,
        description="Specify file extension filter",
    )
    split_files: bool = Field(
        default=True,
        description="Whether to split files into separate models",
    )
    tasks_per_job: int = Field(
        default=1,
        description="Number of tasks per job",
    )
    max_number_of_tasks_dispatched: int = Field(
        default=1000,
        description="Maximum number of tasks to be dispatched",
    )
    group_by: Optional[List[str]] = Field(
        default=None,
        description="DocDB record field(s) to group records by",
    )
    filter_latest: Optional[str] = Field(
        default=None,
        description="DocDB field to filter latest records, keeping only the most recent per group",
    )
    filter_by: Optional[List[str]] = Field(
        default=None,
        description="Field(s) to group by when filtering latest records",
    )
    unwind_list_fields: Optional[List[str]] = Field(
        default=None,
        description="Field(s) to unwind (flatten) before grouping",
    )
    drop_null_groups: bool = Field(
        default=True,
        description="If True, filter out records where grouping fields are None",
    )
    input_directory: Path = Field(
        default=Path("/data"),
        description="Input directory",
    )
    output_directory: Path = Field(
        default=Path("/results"),
        description="Output directory",
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    args = AnalysisDispatchSettings()
    logger.info(args)

    records = get_data_asset_records(**vars(args))

    analysis_parameters_path = args.input_directory / "analysis_parameters.json"

    if analysis_parameters_path.exists():
        with open(analysis_parameters_path, "r") as f:
            distributed_parameters = json.load(f).get("distributed_parameters")
        if distributed_parameters:
            logger.info(
                f"Found analysis parameters json file "
                f"with {len(distributed_parameters)} sets of parameters "
                "Will compute product of data records and parameter sets."
            )
    else:
        distributed_parameters = None

    input_model_list = get_input_model_list(
        records=records,
        file_extension=args.file_extension,
        split_files=args.split_files,
        distributed_analysis_parameters=distributed_parameters,
    )

    models_to_run = filter_processed_jobs(input_model_list)

    write_input_model_list(
        models_to_run,
        output_directory=args.output_directory,
        tasks_per_job=args.tasks_per_job,
        max_number_of_tasks_dispatched=args.max_number_of_tasks_dispatched,
    )
