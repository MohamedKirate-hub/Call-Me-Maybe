from pydantic import BaseModel, Field, model_validator
from typing import Union, Dict
import json
from utils import file_checker


class ParsingFiles(BaseModel):
    functions_definition_file: Union[str, None] = Field(...)
    input_file: Union[str, None] = Field(...)
    output_file: Union[str, None] = Field(...)

    @model_validator(mode='after')
    def check_validation(self) -> 'ParsingFiles':
        file_checker(self.functions_definition_file, 'w')
        file_checker(self.input_file, 'w')
        file_checker(self.output_file, 'r')
        file_checker(self.output_file, 'w')
        return self


class ParsingContent:
    def __init__(self, functions_file: str,
                 input_file: str, output_file: str) -> None:
        self.functions_file = functions_file
        self.input_file = input_file
        self.output_file = output_file
        self.__files = (self.functions_file, self.input_file,
                        self.output_file)

    def valid_file(self, file_name: str) -> bool:
        try:
            with open(file_name, 'r') as file:
                json.load(file)
            return True
        except Exception:
            return False

    def valid_files(self) -> bool:
        for file_path in self.__files:
            if not (self.valid_file(file_path)):
                return False
        return True


class ParseJsonContent(BaseModel):
    json_content: Dict = Field(...)

    @model_validator(mode='after')
    def checker(self):
        valid_keys = ["name", "description", "parameters"]
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
                    # checking the types if there are in
                    pass
