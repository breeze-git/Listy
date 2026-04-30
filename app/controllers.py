import datetime
import json
import logging
import os
import platform
import subprocess
import tkinter as tk
from copy import deepcopy
from pathlib import Path
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

from babel.dates import format_date
from dateutil.relativedelta import relativedelta

import helpers
import tasks
from config import DATA_DIR, DEFAULT_SETTINGS, LOCALES_DIR

if TYPE_CHECKING:
    from listy import TodoApp

# =========================
# CONTROLLERS
# =========================


def refresh_content_controller(app: "TodoApp", date: datetime.date) -> None:

    ismodified = helpers.check_ismodified(app)

    if ismodified:
        save = helpers.ask_to_save(app)

        if save:
            save_file_controller(app)

    app.date_info.date = date
    app.date_info.date_str_ru.set(date.strftime("%d.%m.%Y"))

    app.refresh_content()

    if app.calendar_window is not None:
        app.calendar_content()


def save_file_controller(app: "TodoApp", event: None | tk.Event = None) -> None:
    save_tasks_ui_controller(app)

    if app.calendar_window is not None:
        app.calendar_content()


def save_tasks_ui_controller(app: "TodoApp") -> None:

    res = app.tasks_data.sync_tasks_data()

    if res:
        app.snapshot = deepcopy(app.tasks_data.data)

        helpers.configure_delete_btn_state(app)
        helpers.configure_save_btn_state(app, "disable")

    else:
        messagebox.showerror(
            title=app.lang["saving"],
            message=app.lang["save_error"],
        )


def load_tasks_ui(app, filename: str) -> tasks.Tasks:
    tasks_data = tasks.Tasks(filename, DATA_DIR)

    if tasks_data.data is None:
        messagebox.showerror(
            title=app.lang["read_error"],
            message=app.lang["backup"],
        )
        tasks_data.data = {}

    return tasks_data


def toggle_theme_controller(app: "TodoApp") -> None:
    theme = app.config["theme"]

    theme = "light" if theme == "dark" else "dark"

    app.config["theme"] = theme

    write_config(DATA_DIR, app.config)

    app.refresh_app()


def change_language_controller(app: "TodoApp") -> None:
    lang = app.config["lang"]

    lang = "en_US" if lang == "ru_RU" else "ru_RU"

    app.config["lang"] = lang

    write_config(DATA_DIR, app.config)

    app.refresh_app()


def open_data_folder(app: "TodoApp") -> None:

    kwargs = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.STDOUT,
    }

    if platform.system() == "Windows":
        os.startfile(DATA_DIR)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", DATA_DIR], **kwargs)
    else:
        subprocess.Popen(["xdg-open", DATA_DIR], **kwargs)


def toggle_task_controller(app: "TodoApp", id: str, btn: ttk.Button) -> None:
    done = app.tasks_data.toggle_task(id)

    btn.config(image=helpers.get_check_icon(done, app.icons))

    helpers.configure_save_btn_state(app, "normal")


def save_task_controller(
    app: "TodoApp", id: str, editor: tk.Text, window: tk.Toplevel
) -> None:
    title, description = helpers.get_data_for_manage(editor)

    title = helpers.trim_title(title)

    isvalid = helpers.validate_title(title)

    if not isvalid:
        messagebox.showinfo(
            parent=window,
            title=app.lang["validation"],
            message=app.lang["title_validation_error"],
        )
        return

    task = app.tasks_data.edit_task(id, title, description)

    app.tasks_widgets[id].task_title.set(title)

    helpers.configure_save_btn_state(app, "normal")

    window.grab_release()
    window.destroy()


def copy_controller(app: "TodoApp", editor: tk.Text) -> None:
    data = editor.get("1.0", "end-1c")

    helpers.copy_to_clipboard(app.root, data)


def delete_task_controller(app: "TodoApp", id: str, window: tk.Toplevel) -> None:
    close = messagebox.askyesno(
        parent=window,
        title=app.lang["confirm_action"],
        message=app.lang["delete_task_confirm"],
    )

    if not close:
        return

    if id in app.tasks_data.data:
        task = app.tasks_data.remove_task(id)

    window.grab_release()
    window.destroy()

    app.tasks_widgets[id].destroy()
    app.tasks_widgets.pop(id)

    if not app.tasks_widgets:
        helpers.show_isempty(app, app.tasks_frame)

    helpers.configure_save_btn_state(app, "normal")


def delete_file_controller(app: "TodoApp", event: None | tk.Event = None) -> None:
    delete = messagebox.askyesno(
        title=app.lang["confirm_action"],
        message=app.lang["delete_list_confirm"],
    )

    if not delete:
        return

    res = app.tasks_data.delete_tasks_file()

    if not res:
        messagebox.showerror(
            title=app.lang["error"],
            message=app.lang["delete_error"],
        )

    app.tasks_data = None
    app.update_tasks()


def calendar_month_frame_controller(app: "TodoApp", isnext: bool) -> None:

    date = app.calendar_info.date.replace(day=1)
    delta = relativedelta(months=1)

    date = date + delta if isnext else date - delta

    month_year = format_date(date, "LLLL y", locale=app.config["lang"]).capitalize()

    app.calendar_info.date = date
    app.calendar_info.month_year.set(month_year)

    app.calendar_content()


def calendar_window_controller(
    app: "TodoApp", window: tk.Toplevel, event: None | tk.Event = None
) -> None:
    window.destroy()

    app.calendar_window = None


def close_window_controller(
    app: "TodoApp",
    window: tk.Toplevel,
    snap_data: dict,
    editor: tk.Text,
    entry: None | ttk.Entry = None,
    event: None | tk.Event = None,
) -> None:
    data = helpers.get_data_from_form(editor, entry)

    if snap_data != data:
        close = helpers.ask_to_close(app, window)

        if not close:
            return

    window.grab_release()
    window.destroy()


def app_exit_controller(app: "TodoApp", event: None | tk.Event = None) -> None:

    ismodified = helpers.check_ismodified(app)

    if ismodified:
        save = helpers.ask_to_save(app)

        if save:
            save_file_controller(app)

    app.root.destroy()


# =========================
# LOCALE
# =========================


def load_lang(locale: str):
    path = LOCALES_DIR / f"{locale}.json"

    try:
        with open(path, "r", encoding="UTF-8") as finp:
            return json.load(finp)
    except FileNotFoundError:
        logging.info("File not found:")
        return None
    except json.JSONDecodeError:
        logging.exception("JSON reading error:")
        return None


# =========================
# CONFIG
# =========================


def load_config(path: Path) -> dict:
    try:
        with open(path, "r", encoding="UTF-8") as finp:
            return json.load(finp)
    except FileNotFoundError:
        logging.info("File not found:")
        return DEFAULT_SETTINGS
    except json.JSONDecodeError:
        logging.exception("JSON reading error:")
        return DEFAULT_SETTINGS


def write_config(path: Path, config: dict) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    fpath = path / "config.json"

    try:
        with open(fpath, "w", encoding="UTF-8") as fout:
            json.dump(config, fout, indent=4, ensure_ascii=False)
    except OSError:
        logging.exception("System error:")
        return False

    return True
