import numpy as np
import json
import regex
from typing import Any, Dict, List


class RegexMask:
    def __init__(self, model, regex_model: regex.compile, top_k: int = 128) -> None:
        self.__model = model
        self.__regex = regex_model
        self.__top_k = top_k
        self.__start_index = 0
        self.__vocab_path = self.__model.get_path_to_vocab_file()
        self.__vocab = self.read_json(self.__vocab_path)
        self.__id_to_token: Dict[int, str] = {
            token_id: token_str for token_str, token_id in self.__vocab.items()
        }
        self.__decoded_token_cache: Dict[int, str] = {}

    def read_json(self, path_file) -> Any:
        with open(path_file) as file:
            data = json.load(file)
        return data

    def reset(self, start_index: int) -> None:
        self.__start_index = start_index

    def __call__(self, input_ids, logits) -> np.ndarray | List[float]:
        partial_output_str = self.__model.decode(input_ids[self.__start_index:])

        logits_np = np.array(logits, dtype=np.float64)
        if logits_np.size == 0:
            return logits

        k = min(self.__top_k, logits_np.size)
        # argpartition gets top-k in O(n) average time without fully sorting.
        candidate_ids = np.argpartition(logits_np, -k)[-k:]

        allowed_tokens_ids = []
        for token_id in candidate_ids.tolist():
            token_str = self.__id_to_token.get(token_id)
            if token_str is None:
                token_str = self.__decoded_token_cache.get(token_id)
                if token_str is None:
                    token_str = self.__model.decode([token_id])
                    self.__decoded_token_cache[token_id] = token_str
            if self.__regex.match(partial_output_str + token_str,
                                  partial=True):
                allowed_tokens_ids.append(token_id)

        if not allowed_tokens_ids:
            return logits
        mask = np.full_like(logits_np, -np.inf)
        for token_id in allowed_tokens_ids:
            mask[token_id] = 0.0

        return logits_np + mask
