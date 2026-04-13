uv run python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calls.json

links :
llm: https://martinfowler.com/articles/function-call-LLM.html
uv: https://medium.com/tr-labs-ml-engineering-blog/using-uv-for-python-development-part-1-making-your-python-dev-experience-much-faster-da4928704097


embeding:
-> bag-of-words: https://builtin.com/machine-learning/bag-of-words
-> tf-idf: https://builtin.com/articles/tf-idf


Neural Network: https://www.youtube.com/watch?v=aircAruvnKk

AI (neural network):https://medium.com/data-science/introducing-deep-learning-and-neural-networks-deep-learning-for-rookies-1-bd68f9cf5883

creating small NN with transform: https://www.tensorflow.org/tutorials/quickstart/beginner

gradent=descent (the way model optimize weight and bias): https://www.youtube.com/watch?v=QoK1nNAURw4
and https://medium.com/@abhaysingh71711/gradient-descent-explained-the-engine-behind-ai-training-2d8ef6ecad6f


NLP: -> towardsdatascience.com/nlp-illustrated-part-1-text-encoding-41ba06c0f512/?source=post_page-----6d718ac40b7d---------------------------------------

-> https://towardsdatascience.com/nlp-illustrated-part-3-word2vec-5b2e12b6a63b/


-> Function-Calling with constrained decoding https://www.salmanq.com/blog/llm-constrained-sampling/#

-> mask: https://medium.com/@docherty/controlling-your-llm-deep-dive-into-constrained-generation-1e561c736a20

-> Books: https://drive.google.com/drive/folders/1jIJMyBOeWiVxLCUUtLvEFEFCnWxbh6cs


other models:
1: Qwen/Qwen2.5-0.5B-Instruct
2: HuggingFaceTB/SmolLM2-360M-Instruct
3: stabilityai/stablelm-2-zephyr-1_6b


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