from typing import Any
from llm_sdk.llm_sdk import Small_LLM_Model
import numpy as np


class Predictor:
    def __init__(self, model_name, file_definition, file_output) -> None:
        self.model = Small_LLM_Model(model_name)
        self.file_definition = file_definition
        self.file_output = file_output
        self.expected_output = """
        {
        "prompt": "string",
        "name": "string",
        "parameters": {
          "a": "number",
          "b": "number"
                      }
        }"""
        self.rules = """
        - Always include "name", "parameters" and "prompt" as keys.
        - and "name" must be in function definition.
        - Do NOT add extra fields.
        - Do NOT remove required fields.
        - Use null if a value is missing
        - Numbers must be numeric (not strings)
        - Argument types must match the function definition (number, string,
        boolean, etc.)
        - Use double quotes for all keys and strings
        - No trailing commas
        - Output must start with '{' and end with '}'
        """
        self.result = ""

    def read_file(self) -> Any:
        if not self.file_definition:
            pass

        with open(self.file_definition, 'r') as file:
            data = file.read()
        return data

    def write_file(self, data=None) -> None:
        if not self.file_output:
            pass

        if not data:
            pass

        if not self.file_output.endswith('.json'):
            pass

        try:
            with (self.file_output, 'w') as file:
                file.write(data)
        except Exception:
            pass

    def softmax(self, data: list) -> list:
        exp_value = np.exp(data)
        exp_sum = np.sum(exp_value)
        return exp_value / exp_sum

    def predict_next_token(self, prompt) -> float:
        self.next_token = 0
        ids = self.model.encode(prompt)
        logits = self.model.get_logits_from_input_ids(ids)
        logits = self.softmax(logits)
        self.next_token = np.argmax(logits)
        return self.next_token

    def decode_next_token(self) -> str:
        return self.model.decode([self.next_token])

    def generate_text(self, prompt) -> None:
        text = self.init_prompt(prompt)
        close_bracket = False
        self.output_text = ""
        while not close_bracket:
            next_token = self.predict_next_token(text)
            next_word = self.decode_next_token(next_token)
            text += next_word

            if next_word == '{':
                self.output_text += next_word

            elif next_word == '}':
                self.output_text += next_word
                close_bracket = True

    def save_output(self) -> None:
        self.write_file(self.output_text)

    def init_prompt(self, prompt):
        llm_prompt = f"""
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
{self.read_file(self.file_definition)}

Input:
{prompt}

Output schema (MUST match exactly):
{self.expected_output}

Rules:
{self.rules}

Example:

prompt:
What is the sum of 2 and 3?

Output:
{{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {{
    "a": 2,
    "b": 3
  }}
}}

Now process this input:

{{your_input_here}}
      """
        return llm_prompt
