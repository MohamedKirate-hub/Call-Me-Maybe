from pydantic import BaseModel, Field, model_validator
from typing import Union
import json


class ParsingFiles(BaseModel):
    functions_definition_file: Union[str, None] = Field(...)
    input_file: Union[str, None] = Field(...)
    output_file: Union[str, None] = Field(...)

    @model_validator(mode='after')
    def check_validation(self) -> 'ParsingFiles':
        if not self.functions_definition_file:
            message = "Invalid configuration: 'functions_definition_file' "
            message += "is required and cannot be empty."
            raise ValueError(message)
        try:
            with open(self.functions_definition_file, 'r'):
                pass
        except FileNotFoundError as e:
            message = f"The file {e.filename} not available."
            raise ValueError(f"[ERROR]: {message}")
        except PermissionError as e:
            message = f"The file {e.filename} doesn't have read permision."
            raise ValueError(f"[ERROR]: {message}")
        except Exception as e:
            raise ValueError(f"[ERROR]: {e}")

        if not self.input_file:
            message = "Invalid configuration: 'input_file' "
            message += "is required and cannot be empty."
            raise ValueError(message)
        try:
            with open(self.input_file, 'r'):
                pass
        except FileNotFoundError as e:
            message = f"The file {e.filename} not available."
            raise ValueError(f"[ERROR]: {message}")
        except PermissionError as e:
            message = f"The file {e.filename} doesn't have read permision."
            raise ValueError(f"[ERROR]: {message}")
        except Exception as e:
            raise ValueError(f"[ERROR]: {e}")

        if not self.output_file:
            message = "Invalid configuration: 'output_file' "
            message += "is required and cannot be empty."
            raise ValueError(message)
        try:
            with open(self.output_file, 'w'):
                pass
        except FileNotFoundError as e:
            message = f"The file {e.filename} not available."
            raise ValueError(f"[ERROR]: {message}")
        except PermissionError as e:
            message = f"The file {e.filename} doesn't have write permision."
            raise ValueError(f"[ERROR]: {message}")
        except Exception as e:
            raise ValueError(f"[ERROR]: {e}")

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
        for file_name in self.__files:
            if not (self.valid_file(file_name)):
                return False
        return True


def ParsingOutputFile(BaseModel):
    pass
