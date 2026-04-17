from typing import List, Union
from llm_sdk.llm_sdk import Small_LLM_Model

from src.utils import (save_content,
                       load_json_content)
from src.model.constrain_decoding import RegexMask
import numpy as np
import regex
import time
import pandas as pd
import json


class PredictorModel:
    def __init__(self, model_name, file_definition, file_output) -> None:
        self.__model = Small_LLM_Model(model_name)
        self.file_definition = file_definition
        self.file_output = file_output
        init_data = {
            "logits": 0.0,
        }
        self.data = pd.DataFrame([init_data])
        self.__re_format = r'^\{\s*"prompt"\s*:\s*"[^"]*"\s*,\s*"name"\s*:\s*'
        self.__re_format += r'"[^"]*"\s*,\s*"parameters"\s*:\s*(?P<args>'
        self.__re_format += r'\{[^{}]*\})\s*\}$'

        self.__regex = regex.compile(self.__re_format)
        self.mask = RegexMask(self.__model, self.__regex)
        self.__max_new_tokens = 256
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

        masked_logits = self.mask(ids, logits)

        self.next_token = np.argmax(masked_logits)
        return self.next_token

    def decode_next_token(self, next_token: float) -> str:
        return self.__model.decode(next_token)

    def generate_text(self, prompt: Union[str, dict]) -> str:
        text = self.init_prompt(prompt)
        self.ids = self.__model.encode(text)[0].tolist()
        self.mask.reset(len(self.ids))
        adding_to_string = False
        self.__output_text = ""

        for _ in range(self.__max_new_tokens):
            next_token = self.predict_next_token(self.ids)
            self.ids.append(next_token)
            next_word = self.decode_next_token(next_token)

            if adding_to_string:
                self.__output_text += next_word

            if '{' in next_word and not adding_to_string:
                self.__output_text += next_word
                adding_to_string = True
            if adding_to_string and self.__valid_output(self.__output_text):
                return self.__output_text
        raise ValueError("Could not produce a valid JSON output within max_new_tokens.")

    def __valid_output(self, content: str) -> bool:
        if self.__regex.fullmatch(content) is None:
            return False
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False

    def __extract_prompt(self, prompt: Union[str, dict]) -> str:
        if isinstance(prompt, dict):
            prompt_value = prompt.get("prompt")
            if isinstance(prompt_value, str) and prompt_value.strip():
                return prompt_value.strip()
            return str(prompt).strip()
        return str(prompt).strip()

    def __fallback_output(self, prompt: Union[str, dict]) -> str:
        prompt_text = self.__extract_prompt(prompt)
        functions_def = load_json_content(self.file_definition)
        if not isinstance(functions_def, list):
            functions_def = [functions_def]
        function_name = ""
        if functions_def:
            function_name = functions_def[0].get("name", "")
        return json.dumps({
            "prompt": prompt_text,
            "name": function_name,
            "parameters": {}
        })

    def __sanitize_output(self, result: str, prompt: Union[str, dict]) -> str:
        try:
            payload = json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return self.__fallback_output(prompt)

        if not isinstance(payload, dict):
            return self.__fallback_output(prompt)

        functions_def = load_json_content(self.file_definition)
        if not isinstance(functions_def, list):
            functions_def = [functions_def]
        function_names = []
        for function in functions_def:
            if not isinstance(function, dict):
                continue
            function_name = function.get("name", "")
            if isinstance(function_name, str) and function_name.strip():
                function_names.append(function_name)
        fallback_name = function_names[0] if function_names else ""

        prompt_text = payload.get("prompt")
        if not isinstance(prompt_text, str) or not prompt_text.strip():
            prompt_text = self.__extract_prompt(prompt)

        function_name = payload.get("name")
        if not isinstance(function_name, str) or function_name not in function_names:
            function_name = fallback_name

        parameters = payload.get("parameters")
        if not isinstance(parameters, dict):
            parameters = {}

        sanitized = {
            "prompt": prompt_text,
            "name": function_name,
            "parameters": parameters
        }
        return json.dumps(sanitized)

    def execute(self, prompt: Union[str, dict]) -> None:
        try:
            result = self.generate_text(prompt)
        except ValueError:
            result = self.__fallback_output(prompt)
        result = self.__sanitize_output(result, prompt)
        save_content(result, self.file_output)

    def init_prompt(self, prompt: Union[str, dict]) -> str:
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
