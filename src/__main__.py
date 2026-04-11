from pydantic import ValidationError


def main() -> None:
    pass


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(f"[ERROR]: {e.errors[0]['msg']}")
    except Exception as e:
        print(f"[ERROR]: {e}")
