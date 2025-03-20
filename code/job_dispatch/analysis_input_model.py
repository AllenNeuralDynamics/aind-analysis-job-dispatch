"""
Class that represents the input analysis job model
"""

from typing import List, Union

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
    location_uri : str
        The input path on S3 that will be used by the analysis function.

    analysis_spec : AnalysisSpecification
        The analysis specification that defines the details of the analysis,
        such as name, version, and parameters.
    """

    location_uri: Union[str, List[str]] = Field(
        ..., title="The input path(s) that will be used by analysis function"
    )
    analysis_spec: AnalysisSpecification = Field(..., title="The analysis specification.")
