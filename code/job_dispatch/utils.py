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
    if group_by:
        response = docdb_api_client.aggregate_docdb_records(
            pipeline=[
                {'$match':query},
                {'$group':{
                    "_id": f"${group_by}",
                    asset_id_prefix: {"$push$": f"${asset_id_prefix}"}
                    }
                }
            ]
        )
    else:
        response = docdb_api_client.retrieve_docdb_records(
            filter_query=query, projection={asset_id_prefix: 1}
        )


    return [x[asset_id_prefix] for x in response]


def get_s3_input_information(
    data_asset_ids: list[str],
    file_extension: str = "",
    split_files: bool = True,
) -> tuple[List[str], List[str], List[Union[str, List[str]]], List[str]]:
    """
    Returns tuple of list of s3 buckets, list of s3 asset ids,
    and list of s3 paths, looking for the file extension if specified

    Parameters
    ----------
    data_asset_ids: list[str]
        A list of data asset ids which will be used to get S3 information

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

    s3_asset_ids: list of str
        A list of S3 data asset ids for each S3 bucket path returned

    s3_paths: list of str
        A list of either single S3 file locations (URLs) that match the query
        and the specified file extension or a list of S3 file locations
        if multiple files are returned for the file extension and split_files is False.
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
    response = docdb_api_client.retrieve_docdb_records(
        filter_query={"external_links.Code Ocean": {"$in": data_asset_ids}},
        projection=projection,
    )

    for record in response:
        s3_buckets.append(f"{record['location']}")
        s3_asset_ids.append(record["external_links"]["Code Ocean"][0])
        s3_asset_names.append(record["name"])
        if file_extension != "":
            file_paths = tuple(
                s3_file_system.glob(
                    f"{record['location']}/**/*{file_extension}"
                )
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
            logger.info(
                f"Found {len(s3_paths)} *.{file_extension} files from s3"
            )

    return s3_buckets, s3_asset_ids, s3_paths, s3_asset_names
