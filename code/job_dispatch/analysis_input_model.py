"""
Class that represents the input analysis job model
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class InputAnalysisModel(BaseModel):
    """
    Represents the input model for an analysis, including the input location
    and the analysis specification.

    Attributes
    ----------
    location_bucket: str
        The input path to the bucket that will be used by the analysis function

    location_asset_id: str
        The asset id associated with the bucket

    location_uri : str
        The input path on S3 that will be used by the analysis function.
    """

    location_bucket: str = Field(
        ..., title="The input path to the bucket that will be used in analysis"
    )
    location_asset_id: str = Field(..., title="The asset id associated with the bucket")

    location_uri: Optional[Union[str, List[str]]] = Field(
        None,
        title="The input path(s) within the location bucket that will be used by analysis function if there are file extensions specified to be found",
    )
