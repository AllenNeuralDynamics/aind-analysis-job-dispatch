"""
Class that represents the input analysis job model
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class InputAnalysisModel(BaseModel):
    """
    Represents the input model for an analysis, including the input location, id, and name

    Attributes
    ----------
    s3_location: str
        The input path to the bucket that will be used by the analysis function

    location_asset_id: str
        The asset id associated with the bucket

    file_extension_locations : str
        The input path(s) within the location bucket that will be used by analysis function if there are file extensions specified to be found.

    asset_name: str
        The name of the asset
    """

    s3_location: List[str] = Field(..., title="S3 bucket path(s) used in analysis")

    location_asset_id: List[str] = Field(
        ..., title="Asset ID(s) associated with the bucket"
    )

    file_extension_locations: Optional[List[str]] = Field(
        None, title="Filtered path(s) in the bucket if file extension filtering is used"
    )

    asset_name: List[str] = Field(..., title="Name(s) of the data asset(s)")
