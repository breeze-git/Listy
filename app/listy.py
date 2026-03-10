import logging
from gui import run_gui


def main():
    try:
        run_gui()
    except Exception:
        logging.exception("Необработанная ошибка:")
        raise


if __name__ == "__main__":
    main()
