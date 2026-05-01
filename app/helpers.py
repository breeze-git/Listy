import datetime
import tkinter as tk
from calendar import monthcalendar
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
    matrix = monthcalendar(date.year, date.month)

    if len(matrix) <= 5:
        row = [0] * 7

        matrix.append(row)

    return matrix


def check_ismodified(app: "TodoApp") -> bool:
    return app.tasks_data.data != app.snapshot


def ask_to_save(app, window=None) -> bool:
    res = messagebox.askyesno(
        parent=window,
        title=app.lang["confirm_action"],
        message=app.lang["save_confirm"],
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


def show_isempty(app, parent: ctk.CTkScrollableFrame) -> None:
    empty_list = ttk.Label(
        parent, text=app.lang["empty_list"], style="Big.TLabel", anchor="center"
    )
    empty_list.pack(anchor="center", fill="both", expand=True, padx=(8, 13))


def ask_to_close(app: "TodoApp", window: None | tk.Toplevel = None) -> bool:
    res = messagebox.askyesno(
        parent=window,
        title=app.lang["confirm_action"],
        message=app.lang["close_confirm"],
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


def get_root_coords(app: "TodoApp", width: int, height: int) -> tuple[str, str]:

    if app.root_coords is not None:
        return app.root_coords[1], app.root_coords[2]

    v_x = app.root.winfo_vrootx()
    v_y = app.root.winfo_vrooty()
    v_w = app.root.winfo_vrootwidth()
    v_h = app.root.winfo_vrootheight()

    x = str(v_x + (v_w // 2) - (width // 2))
    y = str(v_y + (v_h // 2) - (height // 2))

    return x, y


def get_window_coords(
    root: tk.Tk, ind: int = 0, win_size: None | tuple[int, int] = None
) -> tuple[int, int]:
    win_x, win_y = 0, 0

    root_w = root.winfo_width()
    root_h = root.winfo_height()
    root_x = root.winfo_x()
    root_y = root.winfo_y()

    if win_size is not None:
        win_w, win_h = win_size

        win_x = root_x + (root_w // 2) - (win_w // 2)
        win_y = root_y + (root_h // 2) - (win_h // 2)
    else:
        win_x = root_x + root_w + ind
        win_y = root_y

    return win_x, win_y
