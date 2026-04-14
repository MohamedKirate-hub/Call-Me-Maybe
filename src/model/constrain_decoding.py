import numpy as np
import json
import regex
from typing import Any, List


class RegexMask:
    start = 0

    def __init__(self, model, regex_model: regex.compile) -> None:
        self.__start = 0
        self.__model = model
        self.__regex = regex_model
        self.__vocab_path = self.__model.get_path_to_vocab_file()
        self.__vocab = self.read_json(self.__vocab_path)

    def read_json(self, path_file) -> Any:
        with open(path_file) as file:
            data = json.load(file)
        return data

    def __call__(self, input_ids, logits) -> List[float]:
        self.start_index = len(input_ids[0]) - 1
        if RegexMask.start == 0:
            partial_output_str = ''
        else:
            partial_output_str = self.__model.decode(
                input_ids[0, self.start_index]
            )

        allowed_tokens_ids = []
        for token_str, token_id in self.__vocab.items():
            if self.__regex.match(partial_output_str + token_str,
                                  partial=True):
                allowed_tokens_ids.append(token_id)

        if not allowed_tokens_ids:
            return logits
        mask = np.full_like(logits, -np.inf)
        for token_id in allowed_tokens_ids:
            mask[token_id] = 0.0

        logits = logits + mask
        RegexMask.start += 1
        return logits
