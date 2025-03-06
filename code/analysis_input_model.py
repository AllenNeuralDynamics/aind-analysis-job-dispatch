"""
Class that represents the input analysis job model
"""
from pydantic import BaseModel, Field
from typing import List


class AnalysisSpec(BaseModel):
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
    s3_location: str = Field(
        ..., title="The input path on s3 that will be used by analysis function"
    )
    analysis_spec: AnalysisSpec = Field(..., title="The analysis specification.")