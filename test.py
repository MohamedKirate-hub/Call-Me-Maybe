# import pandas as pd

# file1 = '/home/mkirate/goinfre/Call_Me_Maybe/timings1.csv'
# # file2 = '/home/mkirate/goinfre/Call_Me_Maybe/timings2.csv'
# # file3 = '/home/mkirate/goinfre/Call_Me_Maybe/timings3.csv'
# pd.set_option('display.max_columns', None)
# for file in [file1]:
#     df = pd.read_csv(file)
#     print(df.head())


from typing import List
from llm_sdk.llm_sdk import Small_LLM_Model

from src.utils import (save_content, validate_json,
                       load_json_content)
from src.model.constrain_decoding import RegexMask
import numpy as np
import regex
import time
import pandas as pd


class PredictorModel:
    def __init__(self, model_name, file_definition, file_output) -> None:
        self.__model = Small_LLM_Model(model_name)
        self.file_definition = file_definition
        self.file_output = file_output
        init_data = {
            "logits": 0.0,
        }
        self.data = pd.DataFrame([init_data])
        self.__re_format = r'^\{\s*"name"\s*:\s*'
        self.__re_format += r'"[^"]*"\s*,\s*"parameters"\s*:\s*(?P<args>'
        self.__re_format += r'\{[^{}]*\})\s*\}$'

        self.__regex = regex.compile(self.__re_format)
        self.mask = RegexMask(self.__model, self.__regex)
        self.__expected_output = """
        {
        "name": "string",
        "parameters": {}
        }"""

        self.__rules = """
        1. Output ONLY valid JSON.
        2. No preamble, no explanation, no markdown blocks.
        3. Keys: "name", "parameters".
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

    def generate_text(self, prompt: str) -> str:
        text = self.init_prompt(prompt)
        self.ids = self.__model.encode(text)[0].tolist()
        adding_to_string = False
        self.__output_text = ""

        while True:
            next_token = self.predict_next_token(self.ids)
            self.ids.append(next_token)
            next_word = self.decode_next_token(next_token)

            if adding_to_string:
                self.__output_text += next_word

            if self.__output_text.count('{') == self.__output_text.count('}') and self.__output_text.count('{') > 0:
                print(self.__output_text)
                try:
                    import json
                    json.loads(self.__output_text)
                    break
                except Exception:
                    pass

            if '{' in next_word and not adding_to_string:
                self.__output_text += next_word
                adding_to_string = True
            # print(self.__output_text)
        return self.__output_text

    def execute(self, prompt: str) -> None:
        result = self.generate_text(prompt)
        save_content(result, self.file_output)

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
        "name": "fn_add_numbers",
        "parameters": {{
            "a": 2,
            "b": 3
        }}
    }}

    ### User Input (remember the prompt)
    {prompt}

    ### JSON Output
      """
        return model_prompt
