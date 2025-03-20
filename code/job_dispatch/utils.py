import logging
import pathlib
from typing import List, Union

import s3fs
from aind_data_access_api.document_db import MetadataDbClient

logger = logging.getLogger(__name__)

RESULTS_PATH = pathlib.Path("/results")

API_GATEWAY_HOST = "api.allenneuraldynamics.org"
DATABASE = "metadata_index"
COLLECTION = "data_assets"

docdb_api_client = MetadataDbClient(
    host=API_GATEWAY_HOST,
    database=DATABASE,
    collection=COLLECTION,
)


def get_s3_file_locations_from_docdb_query(
    query: dict, file_extension: str = "", split_files: bool = True
) -> List[Union[str, List[str]]]:
    """
    Returns s3 location or a list of s3 locations, looking for the file extension, from the given docdb query

    Parameters
    ----------
    query : dict
        A dictionary representing the query to retrieve records from the document database.
        The query typically contains a filter to search for specific documents.

    file_extension : str, optional
        The file extension to filter for when searching the S3 locations. If no file extension is provided, the path to the bucket is returned from the query

    split_files : bool
        Whether or not to split files into seperate models or to store in one model as a single list.

    Returns
    -------
    list of str
        A list of either single S3 file locations (URLs) that match the query and the specified file extension or a list of S3 file locations if multiple files are returned for the file extension and split_files is False.
        Each location is prefixed with "s3://".
    """
    s3_paths = []
    s3_file_system = s3fs.S3FileSystem()
    response = docdb_api_client.retrieve_docdb_records(
        filter_query=query, projection={"location": 1}
    )
    logger.info(f"Found {len(response)} records from docDB for the query: {query}")
    for record in response:
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
        else:
            s3_paths.append(f"s3://{record['location']}")

    return s3_paths
