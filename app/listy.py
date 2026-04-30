import datetime
import tkinter as tk
from copy import deepcopy
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from babel.dates import format_date

import controllers
import gui
import helpers
import tasks
from config import CONFIG_FILE


class DateInfo:
    date: datetime.date
    weekday: tk.StringVar
    day_month: tk.StringVar
    date_str_ru: tk.StringVar

    def __init__(self):
        self.date = datetime.date.today()
        self.weekday = tk.StringVar()
        self.day_month = tk.StringVar()
        self.date_str_ru = tk.StringVar()


class CalendarInfo:
    date: datetime.date | None
    month_year: tk.StringVar
    content_frame: ttk.Frame | None

    def __init__(self):
        self.date = None
        self.month_year = tk.StringVar()
        self.content_frame = None


class TodoApp:
    root: tk.Tk
    root_size: None | tuple[int, int]
    root_coords: None | list[str]
    date: datetime.date | None
    date_info: DateInfo
    filename: str | None
    tasks_data: tasks.Tasks | None
    snapshot: dict | None
    calendar_info: CalendarInfo
    hotkeys: dict | None
    body: tk.Frame | None
    tasks_frame: ctk.CTkScrollableFrame | None
    calendar_window: tk.Toplevel | None
    menu_frame: ttk.Frame | None
    icons: None | dict
    theme_use: None | dict
    tasks_widgets: dict
    btns: dict
    config: dict

    def __init__(self, root):
        self.root = root
        self.root_size = None
        self.root_coords = None
        self.date = None
        self.date_info = DateInfo()
        self.filename = None
        self.tasks_data = None
        self.snapshot = None
        self.calendar_info = CalendarInfo()
        self.theme_use = None
        self.icons = None
        self.hotkeys = None

    def configure(self) -> None:
        self.body = None
        self.tasks_frame = None
        self.calendar_window = None
        self.menu_frame = None
        self.tasks_widgets = {}
        self.btns = {}

        self.config = controllers.load_config(CONFIG_FILE)

    def refresh_content(self) -> None:

        self.set_date_info()

        if self.date_info is None:
            return

        self.date = self.date_info.date
        self.tasks_data = None

        self.update_tasks()

    def update_tasks(self) -> None:
        if self.tasks_data is None:
            self.reload_data()

        self.tasks_frame = gui.refresh_tasks_list(self)

        if self.btns:
            helpers.configure_delete_btn_state(self)
            helpers.configure_save_btn_state(self, "disable")

        gui.bind_recursive(
            self.tasks_frame, lambda e: gui.limit_scroll(self.tasks_frame, e)
        )

    def reload_data(self) -> None:
        if self.tasks_frame is not None:
            gui.clear_frame(self.tasks_frame)

            self.tasks_widgets.clear()

        filename = helpers.get_filename_from_date(self.date)

        self.tasks_data = controllers.load_tasks_ui(self, filename)
        self.snapshot = deepcopy(self.tasks_data.data)

    def set_date_info(self) -> None:

        if self.date_info is None:
            return

        self.date_info.weekday.set(
            format_date(
                self.date_info.date, "EEEE", locale=self.config["lang"]
            ).capitalize()
        )

        self.date_info.day_month.set(
            format_date(
                self.date_info.date, "d MMMM", locale=self.config["lang"]
            ).capitalize()
        )

        self.date_info.date_str_ru.set(self.date_info.date.strftime("%d.%m.%Y"))

    def calendar_content(self) -> None:
        date = self.calendar_info.date

        matrix = helpers.get_month_matrix(date)

        gui.create_calendar_content(self, matrix, date)

    def register_hotkeys(self) -> None:
        self.hotkeys = {
            "<Control-s>": controllers.save_file_controller,
            "<Control-n>": gui.create_add_task_window,
            "<Delete>": controllers.delete_file_controller,
            "<Escape>": controllers.app_exit_controller,
        }

        for key, handler in self.hotkeys.items():
            self.root.bind(key, partial(handler, self))

    def run_gui(self) -> None:
        gui.apply_lang(self)
        gui.apply_theme(self)

        gui.create_layout(self.root, self)

    def refresh_app(self) -> None:
        self.root_coords = self.root.geometry().split("+")

        for key in ["<Button-4>", "<Button-5>", "<MouseWheel>"]:
            self.root.unbind_all(key)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.configure()
        self.run_gui()
