import logging
import tkinter as tk
import traceback
from tkinter import messagebox

from config import LOGS_DIR
from listy import TodoApp

# =========================
# WINDOWS DPI
# =========================

try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# =========================
# LOGGING
# =========================

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=LOGS_DIR / "app.log",
    filemode="a",
    encoding="utf-8",
)

logging.info("App is started.")


# =========================
# GLOBAL-HANDLER
# =========================


def tk_exception_handler(exc, val, tb) -> None:
    error = "".join(traceback.format_exception(exc, val, tb))

    logging.error(error)

    messagebox.showerror(
        "Error",
        "An unexpected error occurred.\nCheck the log for details.",
    )


# =========================
# ENTRY POINT
# =========================


def main() -> None:
    root = tk.Tk()
    root.report_callback_exception = tk_exception_handler

    app = TodoApp(root)

    app.configure()
    app.run_gui()
    app.register_hotkeys()

    root.mainloop()


if __name__ == "__main__":
    main()
