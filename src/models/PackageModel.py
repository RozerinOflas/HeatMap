from pydantic import Field, validator
from typing import List, Optional, Union, Literal
from sdks.novavision.src.base.model import Package, Image, Inputs, Configs, Outputs, Response, Request, Output, Input, Config


class InputImage(Input):
    name: Literal["inputImage"] = "inputImage"
    value: Union[List[Image], Image]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, Image):
            return "object"
        elif isinstance(value, list):
            return "list"

    class Config:
        title = "Image"
class OutputImageId(Output):
    name: Literal["outputImage"] = "outputImage"
    value: Union[List[Image],Image]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, Image):
            return "object"
        elif isinstance(value, list):
            return "list"

    class Config:
        title = "Image"
class OutputImageGeneral(Output):
    name: Literal["outputImage"] = "outputImage"
    value: Union[List[Image],Image]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, Image):
            return "object"
        elif isinstance(value, list):
            return "list"

    class Config:
        title = "Image"


class ReferencePoint1(Config):
    name: Literal["ReferencePoint1"] = "ReferencePoint1"
    value: Literal[False] = False
    type: Literal["bool"] = "bool"
    field: Literal["option"] = "option"
    class Config:
        title = "ReferencePoint1"

class ReferencePoint2(Config):
    name: Literal["ReferencePoint2"] = "ReferencePoint2"
    value: Literal[True] = True
    type: Literal["bool"] = "bool"
    field: Literal["option"] = "option"
    class Config:
        title = "ReferencePoint2"

class ReferencePoint(Config):
    """
        Rotate image without catting off sides.
    """
    name: Literal["ReferencePoint"] = "ReferencePoint"
    value: Union[ReferencePoint1, ReferencePoint2]
    type: Literal["object"] = "object"
    field: Literal["dropdownlist"] = "dropdownlist"
    class Config:
        title = "ReferencePoint"

class HeatMapTime(Config):
    """
        Positive angles specify counterclockwise rotation while negative angles indicate clockwise rotation.
    """
    name: Literal["HeatMapTime"] = "HeatMapTime"
    value: int = Field(ge=-359.0, le=359.0,default=0)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "HeatMapTime"
class FrameTime(Config):
    """
        Positive angles specify counterclockwise rotation while negative angles indicate clockwise rotation.
    """
    name: Literal["HeatMapTime"] = "HeatMapTime"
    value: int = Field(ge=-359.0, le=359.0,default=0)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "HeatMapTime"

class HeatMapExecutorInputs(Inputs):
    inputImage: InputImage
class HeatMapExecutorConfigs(Configs):
    heatMapTime: HeatMapTime
    frameTime: FrameTime
    referencePoint: ReferencePoint
class HeatMapExecutorRequest(Request):
    inputs: Optional[HeatMapExecutorInputs]
    configs: HeatMapExecutorConfigs

    class Config:
        json_schema_extra = {
            "target": "configs"
        }
class HeatMapExecutorOutputs(Outputs):
    outputImageId: OutputImageId
    outputImageGeneral : OutputImageGeneral
class HeatMapExecutorResponse(Response):
    outputs: HeatMapExecutorOutputs

class HeatMapExecutor(Config):
    name: Literal["HeatMapExecutor"] = "HeatMapExecutor"
    value: Union[HeatMapExecutorRequest, HeatMapExecutorResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "Package"
        json_schema_extra = {
            "target": {
                "value": 0
            }
        }


class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: Union[HeatMapExecutor]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Task"
        json_schema_extra = {
            "target": "value"
        }


class PackageConfigs(Configs):
    executor: ConfigExecutor
class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["HeatMap"] = "HeatMap"
