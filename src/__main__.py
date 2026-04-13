from pydantic import ValidationError
from src.model.call_me import PredictorModel
from src.parsing.parsing import Parser
from src.utils import load_json_content
import os

os.environ['HF_HOME'] = '/goinfre/mkirate/huggingface_cache'


def main(model_name="Qwen/Qwen3-0.6B") -> None:
    parser = Parser()
    parser.start_parsing()
    print(f"Function file: {parser.functions_file}")
    print(f"input file: {parser.input_file}")
    print(f"output file: {parser.output_file}")
    predictor_model = PredictorModel(model_name, parser.functions_file,
                                     parser.output_file)
    prompts = load_json_content(parser.input_file)
    if not isinstance(prompts, list):
        prompts = [prompts]
    for prompt in prompts:
        predictor_model.execute(prompt)
        print(predictor_model.get_output())


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(f"[ERROR]: {e.errors()[0]['msg'].strip('Value error, ')}")
    # except Exception as e:
    #     print(f"[ERROR]: {e}")
