import argparse
from typing import Dict


class FindArgs:
    def __init__(self) -> None:
        self.__content = []

    def init_args(self) -> Dict:
        parser = argparse.ArgumentParser()
        parser.add_argument("--functions_definition")
        parser.add_argument("--input")
        parser.add_argument("--output")

        args = parser.parse_args()

        self.functions_file = args.functions_definition
        self.input_file = args.input
        self.output_file = args.output

        return {
            "functions_definition": self.functions_file,
            "input": self.input_file,
            "output": self.output_file
        }
