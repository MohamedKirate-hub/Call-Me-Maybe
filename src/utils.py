import json
import numpy as np
from typing import Any
import os


def save_content(self, content: str, file_path: str) -> None:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        if not isinstance(data, list):
            data = [data]
    except json.JSONDecodeError:
        data = []
    except FileNotFoundError:
        data = []

    json_content = json.loads(content)
    data.append(json_content)

    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except PermissionError:
        message = f"Permission denied. Cannot write to '{file_path}'."
        raise ValueError(message)
    except FileNotFoundError:
        message = f"The directory for '{file_path}'"
        message += " does not exist."
        raise ValueError(message)


def file_checker(file_path: str, mode: str):
    file_modes = {
        'r': os.R_OK,
        'w': os.W_OK,
    }
    if not file_path:
        message = "File path is required and cannot be empty."
        raise ValueError(message)

    if not os.path.exists(file_path):
        message = f"The file {file_path} not available."
        raise ValueError(message)

    permission = file_modes.get(mode)
    if not os.access(file_path, permission):
        message = f"The file {file_path} doesn't have {mode} permision."
        raise ValueError(message)


def read_file(self, file_path: str) -> Any:
    if not file_path:
        raise ValueError("File path is required and cannot be empty.")

    with open(file_path, 'r') as file:
        data = file.read()
    return data


def write_json_file(self, file_path: str, data=None) -> None:
    if not file_path:
        raise ValueError("File path is required and cannot be empty.")

    if not data:
        raise ValueError(f"Warning: No data provided to write to {file_path}.")

    try:
        with (file_path, 'w') as file:
            file.write(data)
    except FileNotFoundError:
        message = f"The directory for '{file_path}' does not exist."
        raise ValueError(message)
    except PermissionError:
        message = f"Permission denied. Cannot write to '{file_path}'."
        raise ValueError(message)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def validate_json(self, content: str) -> bool:
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False


def softmax(self, data: list) -> list:
    exp_value = np.exp(data)
    exp_sum = np.sum(exp_value)
    return exp_value / exp_sum
