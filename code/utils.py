import logging
import pathlib
from typing import List, Optional, Union

import s3fs
from aind_data_access_api.document_db import MetadataDbClient

logger = logging.getLogger(__name__)

API_GATEWAY_HOST = "api.allenneuraldynamics.org"
DATABASE = "metadata_index"
COLLECTION = "data_assets"

docdb_api_client = MetadataDbClient(
    host=API_GATEWAY_HOST,
    database=DATABASE,
    collection=COLLECTION,
)


def get_data_asset_ids_from_query(query: dict, group_by: Optional[str]):
    """
    Retrieve data asset IDs based on query passed in.

    Parameters
    ----------
    query : dict
        A dictionary representing the query criteria used to filter data assets

    Returns
    -------
    list of str
        A list of data asset IDs that match the provided query criteria.
    """
    asset_id_prefix = "external_links.Code Ocean.0"
    asset_id_prefix = "location"
    if True:
        response = docdb_api_client.aggregate_docdb_records(
            pipeline=[
                {"$match": query},
                {
                    "$group": {
                        "_id": "$" + group_by if group_by else "$_id",
                        "asset_id": {"$push": f"${asset_id_prefix}"},
                    }
                },
            ]
        )
    else:
        response = docdb_api_client.retrieve_docdb_records(
            filter_query=query, projection={asset_id_prefix: 1}
        )

    return [x["asset_id"] for x in response]


def get_s3_input_information(
    data_asset_paths: list[str],
    file_extension: str = "",
    split_files: bool = True,
) -> tuple[List[str], List[str], List[Union[str, List[str]]], List[str]]:
    """
    Returns tuple of list of s3 bucket paths, and
    s3 filepaths looking for the file extension if specified

    Parameters
    ----------
    data_asset_paths: list[str]
        A list of data asset paths which will be used to get S3 information

    file_extension : str, optional
        The file extension to filter for when searching the S3 locations.
        If no file extension is provided,
        the path to the bucket is returned from the query

    split_files : bool
        Whether or not to split files into seperate models
        or to store in one model as a single list.

    Returns
    -------
    s3_buckets: list of str
        A list of S3 bucket paths for each record returned by the query
    s3_file_paths: list of str
        A list of s3 file paths if file extension is specified
    """
    s3_paths = []
    s3_file_paths = []
    s3_file_system = s3fs.S3FileSystem()

    for location in data_asset_paths:
        if file_extension != "":
            file_paths = tuple(s3_file_system.glob(f"{location}/**/*{file_extension}"))
            if not file_paths:
                logging.warning(f"No {file_extension} found in {location} - skipping.")
                continue

            if split_files:
                for file in file_paths:
                    s3_file_paths.append(f"s3://{file}")
            else:
                s3_file_paths.append([f"s3://{file}" for file in file_paths])
            logger.info(f"Found {len(file_paths)} *{file_extension} files from s3")
            s3_paths.append(location)
        else:
            s3_paths.append(location)

    return s3_paths, s3_file_paths
