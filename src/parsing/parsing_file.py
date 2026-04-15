from pydantic import BaseModel, Field, model_validator
from typing import Union
import json
from src.utils import file_checker


class ParsingFiles(BaseModel):
    functions_definition_file: Union[str, None] = Field(...)
    input_file: Union[str, None] = Field(...)
    output_file: Union[str, None] = Field(...)

    @model_validator(mode='after')
    def check_validation(self) -> 'ParsingFiles':
        file_checker(self.functions_definition_file, 'r')
        file_checker(self.input_file, 'r')
        file_checker(self.output_file, 'r')
        file_checker(self.output_file, 'w')
        return self


class ParsingContent:
    def __init__(self, functions_file: str,
                 input_file: str) -> None:
        self.functions_file = functions_file
        self.input_file = input_file
        self.__files = (self.functions_file, self.input_file)

    def valid_file(self, file_name: str) -> bool:
        try:
            with open(file_name, 'r') as file:
                json.load(file)
            return True
        except Exception:
            return False

    def valid_files(self) -> None:
        for file_path in self.__files:
            if not (self.valid_file(file_path)):
                raise ValueError(f"The file {file_path} must contain "
                                 "json content.")


class ParseJsonDefinitionContent(BaseModel):
    json_content: dict = Field(...)

    @model_validator(mode='after')
    def checker(self) -> 'ParseJsonDefinitionContent':

        valid_keys = ["name", "description", "parameters", "returns"]
        parametrs_type = ["number", "string", "bool"]

        for key in self.json_content.keys():
            if key not in valid_keys:
                messsage = "There are Invalid Key at the file."
                raise ValueError(messsage)

        for key in valid_keys:
            if not self.json_content.get(key, None):
                raise ValueError(f"The key '{key}' is missing.")

        name = self.json_content.get("name", None)
        description = self.json_content.get("description", None)
        parameters = self.json_content.get("parameters")
        returns = self.json_content.get("returns", None)

        for value in [name, description, parameters, returns]:
            if (isinstance(value, str) and not value.strip()):
                raise ValueError("Value cannot empty, or whitespace.")

        for key in self.json_content.keys():
            if key == "description":
                value = self.json_content.get(key)
                if not value:
                    pass
                if not isinstance(value, str):
                    pass
                if value.strip():
                    pass

            if key == "parameters":
                for k, v in self.json_content[key].items():
                    if not isinstance(v, dict):
                        raise ValueError(f"Parameter '{k}' must be an object/"
                                         "dictionary. Found: "
                                         f"{type(v)}")

                    if not v.get("type"):
                        raise ValueError(
                            f"Parameter '{k}' is missing the required "
                            "'type' field."
                        )

                    if v.get("type") not in parametrs_type:
                        raise ValueError(
                            f"Invalid type |{v.get('type')}| for parameter "
                            f"'{k}'. "
                            f"Must be one of: {parametrs_type}"
                        )

            if key == "returns":
                value = self.json_content[key]
                if not isinstance(value, dict):
                    raise ValueError(f"The 'returns' field must be a "
                                     "dictionary. Found: "
                                     f"{type(value)}")
                if not value.get("type"):
                    raise ValueError(
                            "The 'returns' object is missing the "
                            "required 'type' field."
                        )
                if value.get("type") not in parametrs_type:
                    raise ValueError(
                            f"Invalid type |{value.get('type')}| for 'return' "
                            f"Must be one of: {parametrs_type}"
                        )
        return self


class ParseJsonPrompt(BaseModel):
    prompt: dict = Field(...)

    @model_validator(mode="after")
    def checker(self) -> 'ParseJsonPrompt':
        valid_keys = ['prompt']
        for key in self.prompt.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid key: {key}.")
        for key in valid_keys:
            if key not in self.prompt.keys():
                raise ValueError("Missing prompt key.")

        prompt_value = self.prompt.get('prompt')
        if not prompt_value:
            raise ValueError("Missing the value of prompt.")
        if not isinstance(prompt_value, str):
            raise ValueError("The prompt value must be str.")
        if not prompt_value.strip():
            raise ValueError("Value cannot empty, or whitespace.")

        return self


class ParseJsonOutput(BaseModel):
    output_content: dict = Field(...)

    @model_validator(mode='after')
    def checker(self) -> 'ParseJsonOutput':
        valid_keys = ['prompt', 'name', 'parameters']
        for key in self.output_content.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid key: {key}.")

        for key in valid_keys:
            if key not in self.output_content.keys():
                raise ValueError(f"Missing '{key}' key.")

        for key in self.output_content.keys():
            value = self.output_content.get(key, None)
            if key == 'parameters':
                if not value:
                    raise ValueError("Missing values for 'parameters'.")
                if not isinstance(value, dict):
                    raise ValueError("Invalid type for 'parameters'."
                                     " Expected a dictionary.")
            else:
                if not value:
                    raise ValueError(f"Required field '{key}' is"
                                     " missing or empty.")
                if not isinstance(value, str):
                    raise ValueError(f"Data type mismatch for '{key}'."
                                     " Expected a string.")
                if not value.strip():
                    raise ValueError(f"The field '{key}' cannot be empty.")
        return self
