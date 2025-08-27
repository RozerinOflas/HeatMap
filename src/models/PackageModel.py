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
class OutputImageFrame(Output):
    name: Literal["outputFrame"] = "outputFrame"
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
    value: Literal["ReferencePoint1"] = "ReferencePoint1"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"
    class Config:
        title = "ReferencePoint1"
class ReferencePoint2(Config):
    name: Literal["ReferencePoint2"] = "ReferencePoint2"
    value: Literal["ReferencePoint2"] = "ReferencePoint2"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"
    class Config:
        title = "ReferencePoint2"
class ReferencePoint(Config):
    """
        Reference point
    """
    name: Literal["ReferencePoint"] = "ReferencePoint"
    value: Union[ReferencePoint1, ReferencePoint2]
    type: Literal["object"] = "object"
    field: Literal["dropdownlist"] = "dropdownlist"
    class Config:
        title = "ReferencePoint"

class HeatMapTime(Config):
    """
    """
    name: Literal["HeatMapTime"] = "HeatMapTime"
    value: int = Field(ge=-359.0, le=359.0,default=0)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "HeatMapTime"
class FrameTime(Config):
    """
    """
    name: Literal["FrameTime"] = "FrameTime"
    value: int = Field(ge=-359.0, le=359.0,default=0)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "FrameTime"


class HeatMapGeneral(Config):
    name: Literal["HeatMapGeneral"] = "HeatMapGeneral"
    value: Literal["HeatMapGeneral"] = "HeatMapGeneral"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"
    class Config:
        title = "Heat Map General"
class HeatMapId(Config):
    name: Literal["HeatMapId"] = "HeatMapId"
    value: Literal["HeatMapId"] = "HeatMapId"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"
    class Config:
        title = "Heat Map Id"
class HeatMapTypeIdGeneral(Config):
    name: Literal["Id_General"]="Id_General"
    heatMapId: HeatMapId
    heatMapGeneral: HeatMapGeneral
    value: Literal["Id_General"] ="Id_General"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Id - General"


class HeatMapType(Config):
    """
    id or general
    """
    name: Literal["configType"] = "configType"
    value:Union[HeatMapId,HeatMapGeneral]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Heat Map Type"


class HeatMapExecutorInputs(Inputs):
    inputImage: InputImage
class HeatMapExecutorConfigs(Configs):
    heatMapTime: HeatMapTime
    frameTime: FrameTime
    heatMapType: HeatMapType
    referencePoint: ReferencePoint


class HeatMapExecutorRequest(Request):
    inputs: Optional[HeatMapExecutorInputs]
    configs: HeatMapExecutorConfigs

    class Config:
        json_schema_extra = {
            "target": "configs"
        }
class HeatMapExecutorOutputs(Outputs):
    outputImageFrame: OutputImageFrame
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
