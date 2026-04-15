from src.utils import load_json_content
from pydantic import ValidationError
from src.parsing.parsing import Parser
from src.model.call_me import PredictorModel
from datetime import datetime


def main(model_name="Qwen/Qwen3-0.6B") -> None:
    parser = Parser()
    parser.start_parsing()
    predictor_model = PredictorModel(model_name, parser.functions_file,
                                     parser.output_file)
    prompts = load_json_content(parser.input_file)
    if not isinstance(prompts, list):
        prompts = [prompts]

    start_time = datetime.now()
    for prompt in prompts:
        predictor_model.execute(prompt)
    print(datetime.now() - start_time)


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(f"[ERROR]: {e.errors()[0]['msg'].strip('Value error, ')}")
    # except Exception as e:
    #     print(f"[ERROR]: {e}")
