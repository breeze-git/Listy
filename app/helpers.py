import datetime
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

import customtkinter as ctk

from config import DARK_DIR, DATA_DIR, LIGHT_DIR
from styles import DARK_THEME, LIGHT_THEME

if TYPE_CHECKING:
    from listy import TodoApp


def get_filename_from_date(date: datetime.date) -> str:
    return date.strftime("%Y_%m_%d") + ".json"


def get_check_icon(isdone: bool, icons: dict) -> tk.PhotoImage:
    return icons["checked"] if isdone else icons["unchecked"]


def validate_title(title: str) -> bool:
    return len(title) >= 3 and not title.isspace()


def get_data_for_manage(editor: tk.Text) -> tuple[str, str]:
    title = editor.get("1.0", "1.end")
    description = editor.get("2.0", "end-1c")

    return title, description


def get_data_for_add(entry: ttk.Entry, text: tk.Text) -> tuple[str, str]:
    title = entry.get()
    description = text.get("1.0", "end-1c")

    return title, description


def get_data_from_form(
    editor: tk.Text, entry: None | ttk.Entry = None
) -> dict[str, str]:
    data = {}

    if entry is not None:
        data["title"], data["description"] = get_data_for_add(entry, editor)

    else:
        data["title"], data["description"] = get_data_for_manage(editor)

    return data


def trim_title(title: str) -> str:
    return title.strip()


def get_month_matrix(date: datetime.date) -> list:
    delta = datetime.timedelta(days=1)

    matrix = [[0 for _ in range(7)] for _ in range(6)]

    wday = date.weekday()

    for col in range(wday, 7):
        matrix[0][col] = date.day
        date += delta

    for row in range(1, 6):
        for col in range(7):
            matrix[row][col] = date.day
            date += delta

            if date.day == 1:
                return matrix

    return matrix


def check_ismodified(app: "TodoApp") -> bool:
    return app.tasks_data.data != app.snapshot


def ask_to_save(window=None) -> bool:
    res = messagebox.askyesno(
        parent=window,
        title="Подтверждение действия",
        message="У вас есть несохраненные изменения.\nВыполнить сохранение?",
    )

    return res


def configure_delete_btn_state(app: "TodoApp") -> None:
    hasfile = check_file(app.date)

    if hasfile:
        app.btns["del_btn"].config(state="normal")
    else:
        app.btns["del_btn"].config(state="disable")


def configure_save_btn_state(app: "TodoApp", btn_state) -> None:
    app.btns["save_btn"].config(state=btn_state)


def check_file(date: datetime.date) -> bool:
    filename = get_filename_from_date(date)
    path = DATA_DIR / filename

    return path.exists()


def copy_to_clipboard(root: tk.Tk, data: str):
    root.clipboard_clear()
    root.clipboard_append(data)
    root.update()


def show_isempty(parent: ctk.CTkScrollableFrame) -> None:
    empty_list = ttk.Label(
        parent, text="Задач нет", style="Big.TLabel", anchor="center"
    )
    empty_list.pack(anchor="center", fill="both", expand=True)


def ask_to_close(window: None | tk.Toplevel = None) -> bool:
    res = messagebox.askyesno(
        parent=window,
        title="Подтверждение действия",
        message="Вы уверены что хотите закрыть окно? Все несохранненые изменения будут утеряны.",
    )

    return res


def get_theme(config: dict) -> tuple[dict, Path]:
    if config["theme"] == "dark":
        return DARK_THEME, DARK_DIR
    else:
        return LIGHT_THEME, LIGHT_DIR


def erase_editor(editor: tk.Text) -> None:
    editor.delete("1.0", "end")


def get_btn_style(app: "TodoApp", date: datetime.date, isnotempty: bool) -> str:
    tday = datetime.date.today()

    if tday == date:
        btn_style = "Today.Day.TButton"
    elif app.date == date:
        btn_style = "Current.Day.TButton"
    else:
        btn_style = "Day.TButton"

    if isnotempty:
        btn_style = "Notempty." + btn_style

    return btn_style
