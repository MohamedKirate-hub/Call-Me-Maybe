from src.parsing.get_args import FindArgs
from src.parsing.parsing_file import (ParsingContent, ParsingFiles,
                                      ParseJsonDefinitionContent,
                                      ParseJsonOutput, ParseJsonPrompt)
from src.utils import load_json_content


class Parser:
    def __init__(self):
        args_model = FindArgs()
        args = args_model.init_args()
        self.functions_file = args.get('functions_definition')
        self.input_file = args.get('input')
        self.output_file = args.get('output')

    def start_parsing(self):
        ParsingFiles(functions_definition_file=self.functions_file,
                     input_file=self.input_file,
                     output_file=self.output_file)
        json_content_parser = ParsingContent(
                              functions_file=self.functions_file,
                              input_file=self.input_file)
        json_content_parser.valid_files()
        # Function Definitions
        functions_contents = load_json_content(self.functions_file)
        if not isinstance(functions_contents, list):
            functions_contents = [functions_contents]

        for content in functions_contents:
            ParseJsonDefinitionContent(json_content=content)

        # Prompts
        input_content = load_json_content(self.input_file)
        if not isinstance(input_content, list):
            input_content = [input_content]
        for prompt in input_content:
            ParseJsonPrompt(prompt=prompt)

    def parsing_output(self):
        output_contents = load_json_content(self.output_file)
        if not isinstance(output_contents, list):
            output_contents = [output_contents]
        for output in output_contents:
            ParseJsonOutput(output_content=output)
