import argparse
from typing import Dict
from src.parsing import ParsingFiles, ParsingContent


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

        fl = self.functions_file

        self.__files = ParsingFiles(functions_definition_file=fl,
                                    input_file=self.input_file,
                                    output_file=self.output_file)

        self.__content = ParsingContent(self.__files.functions_definition_file,
                                        self.__files.input_file,
                                        self.__files.output_file)

        return {
            "functions_definition": self.functions_file,
            "input": self.input_file,
            "output": self.output_file
        }

    def parse_content(self) -> Dict:
        if (self.__content.valid_files()):
            return {
                    "functions_definition": self.functions_file,
                    "input": self.input_file,
                    "output": self.output_file
                }
        message = "Invalid files detected: ensure all required files exist"
        message += " and contain properly formatted JSON."
        raise ValueError(message)
