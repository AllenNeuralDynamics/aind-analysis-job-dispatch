import logging
import pathlib
from typing import List, Union

import s3fs
from aind_data_access_api.document_db import MetadataDbClient

logger = logging.getLogger(__name__)

DATA_PATH = pathlib.Path("/data")
RESULTS_PATH = pathlib.Path("/results")

API_GATEWAY_HOST = "api.allenneuraldynamics.org"
DATABASE = "metadata_index"
COLLECTION = "data_assets"

docdb_api_client = MetadataDbClient(
    host=API_GATEWAY_HOST,
    database=DATABASE,
    collection=COLLECTION,
)


def get_s3_file_locations(
    query: Union[dict, None] = None,
    data_asset_ids: Union[list[str], None] = None,
    file_extension: str = "",
    split_files: bool = True,
) -> tuple[List[str], List[str], List[Union[str, List[str]]], List[str]]:
    """
    Returns tuple of list of s3 buckets, list of s3 asset ids, and list of s3 paths, looking for the file extension if specified

    Parameters
    ----------
    query : dict | None
        A dictionary representing the query to retrieve records from the document database.
        The query typically contains a filter to search for specific documents.

    data_asset_ids: list[str] | None
        A list of data asset ids which will be used to get S3 information

    file_extension : str, optional
        The file extension to filter for when searching the S3 locations. If no file extension is provided, the path to the bucket is returned from the query

    split_files : bool
        Whether or not to split files into seperate models or to store in one model as a single list.

    Returns
    -------
    s3_buckets: list of str
        A list of S3 bucket paths for each record returned by the query

    s3_asset_ids: list of str
        A list of S3 data asset ids for each S3 bucket path returned

    s3_paths: list of str
        A list of either single S3 file locations (URLs) that match the query and the specified file extension or a list of S3 file locations if multiple files are returned for the file extension and split_files is False.
        Each location is prefixed with "s3://".

    s3_asset_names: list of str
        A list with the name of each asset
    """
    s3_paths = []
    s3_buckets = []
    s3_asset_ids = []
    s3_asset_names = []
    s3_file_system = s3fs.S3FileSystem()

    projection = {"location": 1, "external_links": 1, "name": 1}
    if query is not None:
        logger.info(f"Using query {query}")
        response = docdb_api_client.retrieve_docdb_records(
            filter_query=query, projection=projection
        )
    else:  # use list of data asset ids
        logger.info(f"Using list of data asset ids provided {data_asset_ids}")
        response = []
        for data_asset_id in data_asset_ids:
            record = docdb_api_client.retrieve_docdb_records(
                filter_query={"external_links": {"Code Ocean": [data_asset_id]}},
                projection=projection,
            )
            if record:
                response.append(record[0])

    logger.info(f"Found {len(response)} records")
    for record in response:
        s3_buckets.append(f"{record['location']}")
        s3_asset_ids.append(record["external_links"]["Code Ocean"][0])
        s3_asset_names.append(record["name"])
        if file_extension != "":
            file_paths = tuple(
                s3_file_system.glob(f"{record['location']}/**/*{file_extension}")
            )
            if not file_paths:
                raise FileNotFoundError(
                    f"No {file_extension} found in {record['location']}"
                )

            if split_files:
                for file in file_paths:
                    s3_paths.append(f"s3://{file}")
            else:
                s3_paths.append([f"s3://{file}" for file in file_paths])
            logger.info(f"Found {len(s3_paths)} *.{file_extension} files from s3")

    return s3_buckets, s3_asset_ids, s3_paths, s3_asset_names
