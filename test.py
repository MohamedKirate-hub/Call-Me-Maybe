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

# import json

# file_name = "vocab.json"
# with open(file_name, 'r') as file:
#     data = json.load(file)

# print(data)


from enum import Enum


class D(Enum):

    R_BRC = "{"
    L_BRC = "}"
    Q ='"'
    

    [
        if token.decode() == R_BRC:
            output += token

        if output.endswith(R_BRC):
            output += Q
            output += fn_name
            output += Q
        if output.endswith(Q):
            output += :


            context = "from the given functions {functions} select the best one and return the result as a json format  "
            result
            if json.load(result):
                return result 
