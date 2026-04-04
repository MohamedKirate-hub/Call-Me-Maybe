# import transformers
# from transformers import (AutoTokenizer)


# model_name = "Qwen/Qwen3-0.6B"

# tokenizer = AutoTokenizer.from_pretrained(model_name)

# text = "hello Ġworld !."
# text2 = "\n r b c d e f g h\n"

# ids = tokenizer.encode(text2)

# tokens = tokenizer.tokenize(text2)
# print(tokens)
# print(ids)

import json

file_name = "vocab.json"
with open(file_name, 'r') as file:
    data = json.load(file)

print(data)
