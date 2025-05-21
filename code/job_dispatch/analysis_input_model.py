"""
Class that represents the input analysis job model
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class AnalysisSpecification(BaseModel):
    """
    Represents the specification for an analysis, including its name,
    version, libraries to track, and parameters.

    Attributes
    ----------
    analysis_name : str
        The name of the analysis function that will be run.

    analysis_version : str
        The version of the analysis to run.

    analysis_libraries_to_track : List[str]
        A list of libraries to track that will be used in the analysis.

    analysis_parameters : dict, optional
        A dictionary of user-defined input parameters that the analysis
        function will use. Defaults to an empty dictionary.
    """

    analysis_name: str = Field(..., title="The analysis function that will be run")
    analysis_version: str = Field(..., title="The version of the analysis to run")
    analysis_libraries_to_track: List[str] = Field(
        ..., title="The analysis libraries that will be used"
    )
    analysis_parameters: dict = Field(
        default={},
        title="The user defined input parameters that the analysis function will use",
    )


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

    asset_name: str
        The name of the asset
    """

    s3_location: str = Field(
        ..., title="The input path to the bucket that will be used in analysis"
    )

    location_asset_id: str = Field(..., title="The asset id associated with the bucket")

    location_uri: Optional[Union[str, List[str]]] = Field(
        None,
        title="The input path(s) within the location bucket that will be used by analysis function if there are file extensions specified to be found",
    )

    asset_name: str = Field(..., title="The name of the data asset")

    parameters: AnalysisSpecification = Field(
        ..., title="The analysis specification to be applied to the data"
    )
