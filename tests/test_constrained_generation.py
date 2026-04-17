import json
import os
import sys
import tempfile
import types
import unittest

import numpy as np
import regex

from src.model.constrain_decoding import RegexMask


class _RecordingRegex:
    def __init__(self) -> None:
        self.calls = []

    def match(self, value, partial=True):
        self.calls.append(value)
        return value.endswith("c")


class _RegexMaskModel:
    def __init__(self, vocab_path: str) -> None:
        self._vocab_path = vocab_path

    def get_path_to_vocab_file(self):
        return self._vocab_path

    def decode(self, ids):
        if isinstance(ids, int):
            ids = [ids]
        token_map = {1: "x", 2: "y"}
        return "".join(token_map.get(token_id, "") for token_id in ids)


class _MaskReset:
    def reset(self, _index):
        return None


class _ModelNoOutput:
    def encode(self, _text):
        return np.array([[1, 2]], dtype=np.int64)


class TestConstrainedGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_llm_package = types.ModuleType("llm_sdk")
        fake_llm_module = types.ModuleType("llm_sdk.llm_sdk")

        class _FakeSmallModel:
            def __init__(self, *_args, **_kwargs):
                pass

        fake_llm_module.Small_LLM_Model = _FakeSmallModel
        fake_llm_package.llm_sdk = fake_llm_module
        sys.modules.setdefault("llm_sdk", fake_llm_package)
        sys.modules.setdefault("llm_sdk.llm_sdk", fake_llm_module)
        sys.modules.setdefault("pandas", types.ModuleType("pandas"))

        fake_utils_module = types.ModuleType("src.utils")

        def _validate_json(content):
            try:
                json.loads(content)
                return True
            except json.JSONDecodeError:
                return False

        fake_utils_module.validate_json = _validate_json
        fake_utils_module.save_content = lambda *_args, **_kwargs: None
        fake_utils_module.load_json_content = lambda *_args, **_kwargs: []
        sys.modules.setdefault("src.utils", fake_utils_module)

    def test_regex_mask_uses_full_prefix_and_top_k_candidates(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as vocab_file:
            json.dump({"a": 0, "b": 1, "c": 2, "d": 3}, vocab_file)
            vocab_path = vocab_file.name

        try:
            mask_regex = _RecordingRegex()
            model = _RegexMaskModel(vocab_path)
            mask = RegexMask(model, mask_regex, top_k=2)
            mask.reset(1)

            logits = [0.0, 0.1, 5.0, 6.0]
            masked = mask([99, 1, 2], logits)

            self.assertEqual(len(mask_regex.calls), 2)
            self.assertEqual(set(mask_regex.calls), {"xyc", "xyd"})
            self.assertTrue(np.isfinite(masked[2]))
            self.assertTrue(np.isneginf(masked[3]))
        finally:
            os.unlink(vocab_path)

    def test_generate_text_stops_after_max_new_tokens(self):
        from src.model.call_me import PredictorModel

        predictor = PredictorModel.__new__(PredictorModel)
        predictor._PredictorModel__model = _ModelNoOutput()
        predictor.mask = _MaskReset()
        predictor._PredictorModel__max_new_tokens = 3
        predictor._PredictorModel__regex = regex.compile(r"^$")
        predictor.init_prompt = lambda prompt: "seed"
        predictor.predict_next_token = lambda ids: 7
        predictor.decode_next_token = lambda token: "x"

        with self.assertRaisesRegex(
            ValueError, "Could not produce a valid JSON output within max_new_tokens."
        ):
            predictor.generate_text({"prompt": "hello"})


if __name__ == "__main__":
    unittest.main()
