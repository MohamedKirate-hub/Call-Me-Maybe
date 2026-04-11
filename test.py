from pydantic import BaseModel, Field, model_validator
from typing import Union, Dict
import json


class ParseJsonContent(BaseModel):
    json_content: Dict = Field(...)

    @model_validator(mode='after')
    def checker(self) -> 'ParseJsonContent':

        valid_keys = ["name", "description", "parameters", "returns"]
        parametrs_type = ["number", "string", "bool"]

        for key in self.json_content.keys():
            if key not in valid_keys:
                messsage = "There are Invalid Key at the file."
                raise ValueError(messsage)

        name = self.json_content.get("name", None)
        description = self.json_content.get("description", None)
        parameters = self.json_content.get("parameters")

        for key in [name, description, parameters]:
            if not key or (isinstance(key, str) and not key.strip()):
                pass
            if key == "parameters":
                for k, v in self.json_content[key]:
                    if not isinstance(v, dict):
                        pass
                    if not v.get("type"):
                        pass
                    if v.get("type") not in parametrs_type:
                        pass
            if key == "returns":
                if not isinstance(self.json_content[key], dict):
                    pass
                if not self.json_content[key].get("type"):
                    pass
                if self.json_content[key].get("type") not in parametrs_type:
                    pass
        return self
