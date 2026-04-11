from typing import List
from llm_sdk.llm_sdk import Small_LLM_Model
from utils import (softmax, save_content, read_file, validate_json)
from constrain_decoding import RegexMask
import numpy as np
import regex


class Predictor:
    def __init__(self, model_name, file_definition, file_output) -> None:
        self.__model = Small_LLM_Model(model_name)
        self.file_definition = file_definition
        self.file_output = file_output

        self.__re_format = r'^\{\s*"prompt"\s*:\s*"[^"]*"\s*,\s*"name"\s*:\s*'
        self.__re_format += r'"[^"]*"\s*,\s*"parameters"\s*:\s*(?P<args>'
        self.__re_format += r'\{[^{}]*\})\s*\}$'

        self.__regex = regex.compile(self.__re_format)
        self.__expected_output = """
        {
        "prompt": "string",
        "name": "string",
        "parameters": "dictionary"
        }"""

        self.__rules = """
        - Always include "name", "parameters" and "prompt" as keys.
        - and "name" must be in function definition.
        - Do NOT add extra fields.
        - Do NOT remove required fields.
        - Use null if a value is missing
        - If a user request cannot be fulfilled by the provided functions,
        you MUST set "name" to null and "parameters" to null.
        - Do NOT try to force a function call if the intent does not match.
        - "name" must be a function name from the definition or null.
        - "parameters" must be a dictionary or null.
        - STRICT RULE: If the user asks for a calculation
        (like 2-2, 5*5, 2**3,etc.) and there is no EXACT function for
        that specific math operation, you MUST return "name": null.
        - Do NOT use 'fn_add_numbers' for subtraction, multiplication,
        or division.
        - If a value is missing or no function matches, use null.
        - Argument types must match the function definition.
        - Numbers must be numeric (not strings)
        - Argument types must match the function definition (number, string,
        boolean, etc.)
        - Use double quotes for all keys and strings
        - No trailing commas
        - Output must start with '{' and end with '}'
        """

    def encode(self, prompt) -> List:
        return self.__model.encode(prompt)

    def decode(self, ids: List) -> str:
        return self.__model.decode(ids)

    def predict_next_token(self, prompt) -> float:
        self.next_token = 0
        ids = self.__model.encode(prompt)
        logits = self.__model.get_logits_from_input_ids(ids.tolist()[0])

        mask = RegexMask(self.__model, self.__regex)
        masked_logits = mask(ids, logits)

        sotmax_logits = softmax(masked_logits)
        self.next_token = np.argmax(sotmax_logits)
        return self.next_token

    def decode_next_token(self, next_token) -> str:
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
        if not prompt:
            pass

        model_prompt = f"""
      You are a function-calling JSON generator.

Your task:
- Read the input carefully
- Select the correct function
- Extract the required parameters
- Return ONLY valid JSON

Do NOT output:
- explanations
- text
- comments
- markdown
- code blocks

If you output anything other than JSON, it is incorrect.

Function definition:
{read_file(self.file_definition)}

Input:
{prompt}

Output schema (MUST match exactly):
{self.__expected_output}

Rules:
{self.__rules}

Example:

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

prompt: What is 2 divide 2?
Output:
{{
  "prompt": "what is 2 devide 2?",
  "name": null,
  "parameters": null
}}

Now process this input:

{{your_input_here}}
      """
        return model_prompt
