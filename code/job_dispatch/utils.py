import pathlib

import s3fs
from aind_data_access_api.document_db import MetadataDbClient

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
    query: dict, file_extension: str = "nwb"
) -> list[str]:
    """
    Returns list of s3 locations, looking for the file extension, from the given docdb query

    Parameters
    ----------
    query : dict
        A dictionary representing the query to retrieve records from the document database. 
        The query typically contains a filter to search for specific documents.
    
    file_extension : str, optional
        The file extension to filter for when searching the S3 locations. Default is "nwb".

    Returns
    -------
    list of str
        A list of S3 file locations (URLs) that match the query and the specified file extension. 
        Each location is prefixed with "s3://".
    """
    s3_paths = []
    s3_file_system = s3fs.S3FileSystem()
    response = docdb_api_client.retrieve_docdb_records(
        filter_query=query, projection={"location": 1}
    )
    for record in response:
        file_path = tuple(
            s3_file_system.glob(f"{record['location']}/**/*{file_extension}")
        )
        if file_path:
            s3_paths.append(f"s3://{file_path[0]}")

    return s3_paths