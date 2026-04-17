from typing import List

from llm_sdk.llm_sdk import Small_LLM_Model

from src.utils import (save_content, validate_json,
                       load_json_content)
from src.model.constrain_decoding import RegexMask
import numpy as np
import regex
import time
import pandas as pd


# 0:09:11.549487
class PredictorModel:
    def __init__(self, model_name, file_definition, file_output) -> None:
        self.__model = Small_LLM_Model(model_name)
        self.file_definition = file_definition
        self.file_output = file_output
        init_data = {
            "init_prompt": 0.0,
            "encode_prompt": 0.0,
            "append_ids": 0.0,
            "decode_next": 0.0,
            "validate_json": 0.0,
            "adding_next": 0.0,
            "saving_result": 0.0,
            "logits": 0.0,
            "masking": 0.0
        }
        self.data = pd.DataFrame([init_data])
        self.__re_format = r'^\{\s*"prompt"\s*:\s*"[^"]*"\s*,\s*"name"\s*:\s*'
        self.__re_format += r'"[^"]*"\s*,\s*"parameters"\s*:\s*(?P<args>'
        self.__re_format += r'\{[^{}]*\})\s*\}$'

        self.__regex = regex.compile(self.__re_format)
        self.mask = RegexMask(self.__model, self.__regex)
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

    def predict_next_token(self, ids: List) -> float:

        self.next_token = 0
        start_time = time.perf_counter()
        max_tokens = 290
        if len(ids) > max_tokens:
            ids = ids[-max_tokens:]
        logits = self.__model.get_logits_from_input_ids(ids)
        elapsed = time.perf_counter() - start_time
        self.data.loc[0, "logits"] += float(elapsed / 60)


        start_time = time.perf_counter()
        masked_logits = self.mask(ids, logits)
        elapsed = time.perf_counter() - start_time
        self.data.loc[0, "masking"] += float(elapsed / 60)

        self.next_token = np.argmax(masked_logits)
        return self.next_token

    def decode_next_token(self, next_token: float) -> str:
        return self.__model.decode(next_token)

    def generate_text(self, prompt: str) -> str:

        start_time = time.perf_counter()
        text = self.init_prompt(prompt)
        elapsed = time.perf_counter() - start_time
        self.data.loc[0, "init_prompt"] += float(elapsed / 60)

        start_time = time.perf_counter()
        self.ids = self.__model.encode(text)[0].tolist()
        elapsed = time.perf_counter() - start_time
        self.data.loc[0, "encode_prompt"] += float(elapsed / 60)
        adding_to_string = False
        self.__output_text = ""

        self.consume_time = {
            'append_ids': 0.0,
            'decode_next': 0.0,
            'validate_json': 0.0,
            'adding_next': 0.0,
            'logits': 0.0,
            "masking": 0.0
        }

        while True:
            next_token = self.predict_next_token(self.ids)
            start_time = time.perf_counter()
            self.ids.append(next_token)
            elapsed = time.perf_counter() - start_time
            self.consume_time["append_ids"] += float(elapsed / 60)

            start_time = time.perf_counter()
            next_word = self.decode_next_token(next_token)
            elapsed = time.perf_counter() - start_time
            self.consume_time["decode_next"] += float(elapsed / 60)

            start_time = time.perf_counter()
            is_valid = validate_json(self.__output_text)
            elapsed = time.perf_counter() - start_time
            self.consume_time["validate_json"] += float(elapsed / 60)
            if is_valid:
                self.data.loc[0, "append_ids"] = self.consume_time.get("append_ids", 0)
                self.data.loc[0, "decode_next"] = self.consume_time.get("decode_next", 0)
                self.data.loc[0, "validate_json"] = self.consume_time.get("validate_json", 0)
                self.data.loc[0, "adding_next"] = self.consume_time.get("adding_next", 0)
                break


            if adding_to_string:
                start_time = time.perf_counter()
                self.__output_text += next_word
                elapsed = time.perf_counter() - start_time
                self.consume_time["adding_next"] += float(elapsed / 60)

            if '{' in next_word and not adding_to_string:
                self.__output_text += next_word
                adding_to_string = True
        return self.__output_text

    def get_output(self) -> str:
        return self.__output_text

    def execute(self, prompt: str) -> None:
        self.generate_text(prompt)
        start_time = time.perf_counter()
        save_content(self.get_output(), self.file_output)
        elapsed = time.perf_counter() - start_time
        self.data.loc[0, "saving_result"] += float(elapsed / 60)
        print("--" * 20, end='\n\n\n\n\n')

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
