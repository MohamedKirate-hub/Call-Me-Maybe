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
        self.__vocab_items = list(self.__vocab.items())
        self.__cach = {}

    def read_json(self, path_file) -> Any:
        with open(path_file) as file:
            data = json.load(file)
        return data

    def __call__(self, input_ids, logits) -> List[float]:
        self.start_index = len(input_ids) - 1
        if RegexMask.start == 0:
            partial_str = ''
        else:
            partial_str = self.__model.decode(
                input_ids[self.start_index:]
            )

        allowed_ids = self.__cach.get(partial_str, None)
        if allowed_ids is None:
            allowed_ids = []
            for token_str, token_id in self.__vocab_items:
                if self.__regex.match(partial_str + token_str,
                                      partial=True):
                    allowed_ids.append(token_id)
            allowed_ids = np.asarray(allowed_ids)
            self.__cach[partial_str] = allowed_ids

        if not allowed_ids.size == 0:
            return logits
        mask = np.full_like(logits, -np.inf)
        mask[allowed_ids] = 0.0

        logits = logits + mask
        RegexMask.start += 1
        return logits
