from pydantic import ValidationError
from get_args import FindArgs
import os

os.environ['HF_HOME'] = './huggingface_cache'


def main() -> None:
    pass


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(f"[ERROR]: {e.errors[0]['msg']}")
    except Exception as e:
        print(f"[ERROR]: {e}")
