from aind_data_access_api.document_db import MetadataDbClient
import s3fs
import pathlib

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
    """
    s3_paths = []
    s3_file_system = s3fs.S3FileSystem()
    response = docdb_api_client.retrieve_docdb_records(
        filter_query=query, projection={"location": 1}
    )
    for record in response:
        # only looking for nwb files for now, and this assumes the following directory structure where the nwb will be found.
        # another assumption is only 1 nwb file per record in processed data - think this is ok for now
        # might have to modify this based on feedback
        file_path = tuple(
            s3_file_system.glob(f"{record['location']}/*/*.{file_extension}")
        )
        if file_path:
            s3_paths.append(f"s3://{file_path[0]}")

    return s3_paths
