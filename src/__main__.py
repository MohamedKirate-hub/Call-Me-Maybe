from pydantic import ValidationError
from src.parsing.get_args import FindArgs
# from src.call_me import PredictorModel
from src.parsing.parsing import Parser
import os

# os.environ['HF_HOME'] = './huggingface_cache'


def main() -> None:
    parser = Parser()
    parser.start_parsing()
    print(f"Function file: {parser.functions_file}")
    print(f"input file: {parser.input_file}")
    print(f"output file: {parser.output_file}")
    print("\nEavrything is good.")


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(f"[ERROR]: {e.errors()[0]['msg'].strip('Value error, ')}")
    except Exception as e:
        print(f"[ERROR]: {e}")
