from typing import List
from llm_sdk.llm_sdk import Small_LLM_Model
from src.utils import (softmax, save_content, read_file, validate_json,
                       load_json_content)
from src.model.constrain_decoding import RegexMask
import numpy as np
import regex


class PredictorModel:
    def __init__(self, model_name, file_definition, file_output) -> None:
        self.__model = Small_LLM_Model(model_name)
        self.file_definition = file_definition
        self.file_output = file_output
        self.bad_examples_path = 'src/prompt_examples/bad_prompts.txt'
        self.good_examples_path = 'src/prompt_examples/good_prompts.txt'

        self.__re_format = r'^\{\s*"prompt"\s*:\s*"[^"]*"\s*,\s*"name"\s*:\s*'
        self.__re_format += r'"[^"]*"\s*,\s*"parameters"\s*:\s*(?P<args>'
        self.__re_format += r'\{[^{}]*\})\s*\}$'

        self.__regex = regex.compile(self.__re_format)
        self.__bad_prompts = read_file(self.bad_examples_path)
        self.__good_prompts = read_file(self.good_examples_path)
        self.__expected_output = """
        {
        "prompt": "string",
        "name": "string",
        "parameters": {}
        }"""

        self.__rules = """
        1. Output ONLY valid JSON.
        2. No preamble, no explanation, no markdown blocks.
        3. Keys: "prompt", "name", "parameters".
        4. "name" must match the function definition.
        5. Use null for missing values.
        """

    def encode(self, prompt: str) -> List:
        return self.__model.encode(prompt)

    def decode(self, ids: List) -> str:
        return self.__model.decode(ids)

    def predict_next_token(self, prompt: str) -> float:
        self.next_token = 0
        ids = self.__model.encode(prompt)
        logits = self.__model.get_logits_from_input_ids(ids.tolist()[0])

        mask = RegexMask(self.__model, self.__regex)
        masked_logits = mask(ids, logits)

        sotmax_logits = softmax(masked_logits)
        self.next_token = np.argmax(sotmax_logits)
        return self.next_token

    def decode_next_token(self, next_token: float) -> str:
        return self.__model.decode(next_token)

    def generate_text(self, prompt: str) -> str:
        text = self.init_prompt(prompt)
        adding_to_string = False
        self.__output_text = ""

        while True:
            next_token = self.predict_next_token(text)
            next_word = self.decode_next_token(next_token)
            text += next_word

            if self.__output_text:
                print(self.__output_text)
                if validate_json(self.__output_text):
                    break

            if adding_to_string:
                self.__output_text += next_word

            if '{' in next_word and not adding_to_string:
                self.__output_text += next_word
                adding_to_string = True
        return self.__output_text

    def get_output(self) -> str:
        return self.__output_text

    def execute(self, prompt: str) -> None:
        self.generate_text(prompt)
        save_content(self.get_output(), self.file_output)

    def init_prompt(self, prompt: str) -> str:
        fdef_summary = ''
        functions_def = load_json_content(self.file_definition)

        for function in functions_def:
            name = f'function name: {function["name"]}'
            desc = f"Description: {function['description']}"
            parameters = ", ".join(function['parameters'].keys())
            returns = f"Returns: {function['returns']['type']}"

            fdef_summary += f"{name}\n- {desc}\n- "
            fdef_summary += f"Params: ({parameters})\n- {returns}\n\n"

        model_prompt = f"""
      Act as a JSON-only generator. Convert the user input into a
      function call based on the schema.

    ### Function Definition
    {fdef_summary}


    ### Output Schema
    {self.__expected_output}

    ### Rules
    {self.__rules}

    ### EXAMPLE
    prompt: What is the sum of 2 and 3?
    Output:
    {{
        "prompt": "What is the sum of 2 and 3?",
        "name": "fn_add_numbers",
        "parameters": {{
            "a": 2,
            "b": 3
        }}
    }}

    ### User Input
    {prompt}

    ### JSON Output
      """
        return model_prompt
