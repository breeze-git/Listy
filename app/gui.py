import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
from functools import partial
from copy import deepcopy
import logging

import customtkinter as ctk
from babel.dates import format_date, get_day_names
from dateutil.relativedelta import relativedelta

import tasks
from config import DATA_DIR, LOGS_DIR, ICONS_DIR, LIGHT_DIR, DARK_DIR, CONFIG_FILE
from styles import LIGHT_THEME, DARK_THEME, THEME_CONFIG
from debounce import debounce

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

logging.info("Приложение запущено.")

# =========================
# ASSETS
# =========================


def load_icons(icons_dir, theme_dir):
    return {
        "favicon": tk.PhotoImage(file=icons_dir / "favicon.png"),
        "prev": tk.PhotoImage(file=theme_dir / "prev32.png"),
        "next": tk.PhotoImage(file=theme_dir / "next32.png"),
        "calendar": tk.PhotoImage(file=theme_dir / "calendar48.png"),
        "unchecked": tk.PhotoImage(file=theme_dir / "unchecked.png"),
        "checked": tk.PhotoImage(file=theme_dir / "checked.png"),
        "manage32": tk.PhotoImage(file=theme_dir / "manage32.png"),
        "add": tk.PhotoImage(file=theme_dir / "add48.png"),
        "save": tk.PhotoImage(file=theme_dir / "save48.png"),
        "save32": tk.PhotoImage(file=theme_dir / "save32.png"),
        "delete": tk.PhotoImage(file=theme_dir / "delete48.png"),
        "delete32": tk.PhotoImage(file=theme_dir / "delete32.png"),
        "erase32": tk.PhotoImage(file=theme_dir / "erase32.png"),
        "copy32": tk.PhotoImage(file=theme_dir / "copy32.png"),
        "theme": tk.PhotoImage(file=theme_dir / "theme48.png"),
    }


# =========================
# THEME
# =========================


def configure_theme(root, th):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background=th["bg_main"], foreground=th["fg_main"])

    # LABELS

    style.configure(
        "Big.TLabel", padding=THEME_CONFIG["label_padd"], font=THEME_CONFIG["font_big"]
    )
    style.configure(
        "Bold.TLabel",
        padding=THEME_CONFIG["label_padd"],
        font=THEME_CONFIG["font_big_bold"],
    )
    style.configure(
        "Medium.TLabel",
        padding=THEME_CONFIG["label_padd"],
        font=THEME_CONFIG["font_medium"],
    )
    style.configure(
        "Small.TLabel",
        padding=THEME_CONFIG["label_padd"],
        font=THEME_CONFIG["font_small"],
    )

    style.configure(
        "Bordered.Medium.TLabel",
        borderwidth=1,
        relief="solid",
        bordercolor=th["bd_main"],
    )
    style.configure(
        "Bordered.Small.TLabel",
        borderwidth=1,
        relief="solid",
        bordercolor=th["bd_main"],
    )
    style.configure(
        "Weekday.Bordered.Small.TLabel",
        bordercolor=th["cal_bd"],
        font=THEME_CONFIG["font_small"],
    )

    # BUTTONS

    style.configure("Flat.TButton", padding=0, relief="flat", borderwidth=0)
    style.map(
        "Flat.TButton",
        background=[("active", th["bg_main"]), ("pressed", th["bg_main"])],
        foreground=[("active", th["bg_main"]), ("pressed", th["bg_main"])],
        bordercolor=[("focus", th["bg_main"])],
        padding=[("pressed", (1, 2, 0, 0))],
    )

    style.configure("Add.TButton", font=THEME_CONFIG["font_small"])

    style.configure(
        "Day.TButton",
        font=THEME_CONFIG["font_medium"],
        bordercolor=th["btn_bd"],
        lightcolor=th["btn_bd"],
        relief="solid",
    )
    style.map(
        "Day.TButton",
        background=[
            ("hover", th["day_btn_bg"]),
            ("pressed", th["day_btn_bg"]),
        ],
        bordercolor=[
            ("hover", th["day_btn_bd"]),
            ("pressed", th["day_btn_bd"]),
        ],
        foreground=[
            ("hover", th["day_btn_fg"]),
            ("pressed", th["day_btn_fg"]),
        ],
    )
    style.configure(
        "Current.Day.TButton",
        bordercolor=th["cal_blue"],
        foreground=th["cal_blue"],
    )
    style.configure(
        "Today.Day.TButton",
        bordercolor=th["cal_red"],
        foreground=th["cal_red"],
    )

    style.configure("Disabled.TButton", bordercolor=th["btn_bd"], relief="solid")
    style.map(
        "Disabled.TButton",
        background=[
            ("disabled", th["dis_btn_bg"]),
        ],
        lightcolor=[("disabled", th["btn_bd"])],
    )

    style.configure("Notempty.Day.TButton", background=th["btn_bg"])
    style.configure("Notempty.Current.Day.TButton", background=th["btn_bg"])
    style.configure("Notempty.Today.Day.TButton", background=th["btn_bg"])

    # OTHER

    style.configure("Bordered.TFrame", bordercolor=th["cal_bd"])
    style.configure(
        "Add.TEntry",
        padding=(7, 4),
        fieldbackground=th["bg_main"],
        foreground=th["fg_main"],
        insertcolor=th["fg_main"],
        bordercolor=th["fg_main"],
        lightcolor=th["fg_main"],
    )
    style.map(
        "Add.TEntry",
        bordercolor=[("focus", th["fg_main"])],
        lightcolor=[("focus", th["fg_main"])],
    )

    style.configure("Task.TFrame", bordercolor=th["task_bd"])

    root.configure(background=th["bg_main"])


def apply_theme(state):
    theme, theme_dir = get_theme(state["config"])

    state["icons"] = load_icons(ICONS_DIR, theme_dir)
    state["theme_use"] = theme

    configure_theme(state["root"], theme)

    ctk.set_appearance_mode(state["config"]["theme"])


# =========================
# VIEW
# =========================


def create_top(state):
    frame = ttk.Frame(state["root"], padding=5)

    frame.grid_columnconfigure(0, minsize=220)
    frame.columnconfigure(0, weight=0)
    frame.columnconfigure(1, weight=2)
    frame.columnconfigure(2, weight=1)

    frame.rowconfigure((0, 1), weight=1)

    state["date_info"] = {
        "date": datetime.date.today(),
        "weekday": tk.StringVar(),
        "day_month": tk.StringVar(),
        "date_str_ru": tk.StringVar(),
    }

    if state["date"] is not None:
        state["date_info"]["date"] = state["date"]
    else:
        state["date"] = state["date_info"]["date"]

    set_date_info(state)

    wday_label = ttk.Label(
        frame, textvariable=state["date_info"]["weekday"], style="Bold.TLabel"
    )
    wday_label.grid(row=0, column=0, sticky="nesw")

    date_text = ttk.Label(
        frame, textvariable=state["date_info"]["day_month"], style="Big.TLabel"
    )
    date_text.grid(row=1, column=0, sticky="nesw")

    dateframe = create_dateframe(state, frame)
    dateframe.grid(row=0, column=1, sticky="ne")

    theme_btn = ttk.Button(
        frame,
        image=state["icons"]["theme"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(toggle_theme_controller, state),
    )
    theme_btn.grid(row=0, column=2, sticky="ne")

    calendar_btn = ttk.Button(
        frame,
        image=state["icons"]["calendar"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(create_calendar_window, state),
    )

    calendar_btn.grid(row=1, column=2, sticky="se")

    return frame


def create_dateframe(state, parent):
    frame = ttk.Frame(parent)

    frame.columnconfigure((0, 1, 2), weight=1)
    frame.rowconfigure(0, weight=1)

    delta = datetime.timedelta(days=1)

    prev_btn = ttk.Button(
        frame,
        image=state["icons"]["prev"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=lambda: refresh_content_controller(
            state, state["date_info"]["date"] - delta
        ),
    )

    prev_btn.grid(row=0, column=0, sticky="nesw", padx=10)

    date = ttk.Label(
        frame,
        textvariable=state["date_info"]["date_str_ru"],
        style="Bordered.Medium.TLabel",
    )

    date.grid(row=0, column=1, sticky="nesw")

    next_btn = ttk.Button(
        frame,
        image=state["icons"]["next"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=lambda: refresh_content_controller(
            state, state["date_info"]["date"] + delta
        ),
    )

    next_btn.grid(row=0, column=2, sticky="nesw", padx=10)

    state["root"].bind("<Left>", lambda e: prev_btn.invoke())
    state["root"].bind("<Right>", lambda e: next_btn.invoke())

    return frame


def refresh_content(state):
    set_date_info(state)

    state["date"] = state["date_info"]["date"]
    state["tasks_data"] = tasks.reset_tasks_data(state["tasks_data"])

    update_tasks(state)


def set_date_info(state):
    date_info = state["date_info"]

    date = date_info["date"]

    date_info["weekday"].set(
        format_date(date, "EEEE", locale=state["config"]["lang"]).capitalize()
    )

    date_info["day_month"].set(
        format_date(date, "d MMMM", locale=state["config"]["lang"]).capitalize()
    )

    date_info["date_str_ru"].set(date.strftime("%d.%m.%Y"))

    return date_info


def create_body(state):
    frame = ttk.Frame(state["root"])

    state["body"] = frame

    update_tasks(state)

    tasks_frame = state["tasks_frame"]
    tasks_frame.pack(anchor="center", fill="both", expand=True)

    tasks_frame.bind_all("<Button-4>", partial(on_mousewheel, tasks_frame))
    tasks_frame.bind_all("<Button-5>", partial(on_mousewheel, tasks_frame))

    tasks_frame._parent_canvas.bind("<MouseWheel>", partial(limit_scroll, tasks_frame))
    tasks_frame._parent_canvas.bind("<Button-4>", partial(limit_scroll, tasks_frame))

    return frame


def update_tasks(state):

    if state["tasks_data"] is None:
        reload_data(state)

    frame = refresh_tasks_list(state)

    state["tasks_frame"] = frame

    if state["btns"]:
        configure_delete_btn_state(state)
        configure_save_btn_state(state, "disable")

    bind_recursive(frame, lambda e: limit_scroll(frame, e))


def refresh_tasks_list(state):
    tasks_data = state["tasks_data"]

    frame = state["tasks_frame"]

    if frame is None:
        frame = ctk.CTkScrollableFrame(
            state["body"],
            fg_color=(
                "#ffffff",
                "#1A1A1A",
            ),
            label_anchor="w",
        )
        frame._scrollbar.configure(width=0, height=0)

    frame._parent_canvas.yview_moveto(0)

    if not tasks_data:
        show_isempty(frame)

    for id in tasks_data:
        task_frame = create_task_widget(state, id, frame)

        task_frame.pack(anchor="nw", fill="x", pady=5, padx=(8, 16))

        state["tasks_widgets"][id] = task_frame

    return frame


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.update_idletasks()


def show_isempty(parent):
    empty_list = ttk.Label(
        parent, text="Задач нет", style="Big.TLabel", anchor="center"
    )
    empty_list.pack(anchor="center", fill="both", expand=True)


def create_task_widget(state, id, parent):
    task_frame = ttk.Frame(
        parent, padding=5, borderwidth=1, relief="solid", style="Task.TFrame"
    )

    title = state["tasks_data"][id]["title"]

    task_frame.task_title = tk.StringVar(value=title)

    task_frame.columnconfigure((0, 2), weight=0)
    task_frame.columnconfigure(1, weight=4)
    task_frame.rowconfigure(0, weight=1)

    check_image = get_check_icon(state["tasks_data"][id]["done"], state["icons"])

    check_btn = ttk.Button(
        task_frame,
        image=check_image,
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
    )
    check_btn.config(command=partial(toggle_task_controller, state, id, check_btn))
    check_btn.grid(row=0, column=0, sticky="w")

    task_text = ttk.Label(
        task_frame, textvariable=task_frame.task_title, style="Medium.TLabel"
    )
    task_text.grid(row=0, column=1, sticky="w")

    manage_btn = ttk.Button(
        task_frame,
        image=state["icons"]["manage32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(manage_task_controller, state, id),
    )
    manage_btn.grid(row=0, column=2, sticky="e")

    bind_recursive(task_frame, lambda e: limit_scroll(parent, e))

    return task_frame


def bind_recursive(widget, callback):
    widget.bind("<MouseWheel>", callback)
    widget.bind("<Button-4>", callback)
    for child in widget.winfo_children():
        bind_recursive(child, callback)


def create_task_window(state, id):
    window = tk.Toplevel()
    window.title("Просмотр и изменение задачи")
    window.geometry("500x400")
    window.resizable(False, False)

    manage_panel = create_manage_panel(window, state, id)
    manage_panel.pack(fill="both", expand=True)

    window.grab_set()


def create_manage_panel(window, state, id):
    frame = ttk.Frame(window)

    frame.rowconfigure(0, weight=6)
    frame.rowconfigure(1, weight=0)
    frame.columnconfigure(0, weight=20)
    frame.columnconfigure((1, 2, 3, 4), weight=1)

    editor = tk.Text(
        frame,
        wrap="word",
        font=THEME_CONFIG["font_small"],
        padx=7,
        pady=4,
        bg=state["theme_use"]["bg_main"],
        fg=state["theme_use"]["fg_main"],
        insertbackground=state["theme_use"]["fg_main"],
    )
    editor.insert(1.0, state["tasks_data"][id]["title"] + "\n")
    editor.insert(2.0, state["tasks_data"][id]["description"])
    editor.grid(row=0, column=0, columnspan=5)

    save_btn = ttk.Button(
        frame,
        image=state["icons"]["save32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(save_task_controller, state, id, editor, window),
    )
    save_btn.grid(row=1, column=1, pady=5)

    copy_btn = ttk.Button(
        frame,
        image=state["icons"]["copy32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(copy_controller, state, editor),
    )
    copy_btn.grid(row=1, column=2, pady=5)

    erase_btn = ttk.Button(
        frame,
        image=state["icons"]["erase32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(erase_editor, editor),
    )
    erase_btn.grid(row=1, column=3, pady=5)

    delete_btn = ttk.Button(
        frame,
        image=state["icons"]["delete32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(delete_task_controller, state, id, window),
    )
    delete_btn.grid(row=1, column=4, pady=5)

    editor.focus()

    editor.bind("<Control-s>", lambda e: save_btn.invoke())

    editor.bind("<Control-c>", lambda e: copy_btn.invoke())

    editor.bind("<Control-e>", lambda e: erase_btn.invoke())

    editor.bind("<Delete>", lambda e: delete_btn.invoke())

    snap_data = get_data_from_form(editor)

    window.protocol(
        "WM_DELETE_WINDOW",
        partial(close_window_controller, window, snap_data, editor),
    )

    window.bind(
        "<Escape>",
        partial(close_window_controller, window, snap_data, editor, None),
    )

    return frame


def create_footer(state):
    frame = ttk.Frame(state["root"], padding=5)

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=5)

    add_btn = ttk.Button(
        frame,
        image=state["icons"]["add"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(create_add_task_window, state),
    )
    add_btn.grid(row=0, column=0, sticky="w")

    btns_frame = ttk.Frame(frame)
    btns_frame.rowconfigure(0, weight=1)
    btns_frame.columnconfigure((0, 1), weight=1)

    save_btn = ttk.Button(
        btns_frame,
        image=state["icons"]["save"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(save_file_controller, state),
    )
    save_btn.grid(row=0, column=0, sticky="e", padx=5)

    delete_btn = ttk.Button(
        btns_frame,
        image=state["icons"]["delete"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        state="disable",
        command=partial(delete_file_controller, state),
    )
    delete_btn.grid(row=0, column=1, sticky="e", padx=5)

    btns_frame.grid(row=0, column=1, sticky="e")

    state["btns"]["del_btn"] = delete_btn
    state["btns"]["save_btn"] = save_btn

    configure_delete_btn_state(state)

    ismodified = check_ismodified(state)

    if not ismodified:
        configure_save_btn_state(state, "disable")

    return frame


def create_add_task_window(state, event=None):
    window = tk.Toplevel()
    window.title("Добавить задачу")
    window.geometry("400x400")
    window.resizable(False, False)

    add_frame = create_add_frame(window, state)
    add_frame.pack(fill="both", expand=True)

    window.grab_set()


def create_add_frame(window, state):
    frame = ttk.Frame(window, padding=10)

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure((0, 1, 2, 4), weight=0)
    frame.rowconfigure(3, weight=5)

    title_label = ttk.Label(frame, text="Заголовок", style="Small.TLabel")
    title_label.grid(row=0, column=0, sticky="new")

    task_entry = ttk.Entry(
        frame,
        font=THEME_CONFIG["font_small"],
        style="Add.TEntry",
        background=state["theme_use"]["bg_main"],
        foreground=state["theme_use"]["fg_main"],
    )
    task_entry.grid(row=1, column=0, sticky="new", pady=5)

    description_label = ttk.Label(frame, text="Описание", style="Small.TLabel")
    description_label.grid(row=2, column=0, sticky="new")

    task_description = tk.Text(
        frame,
        wrap="word",
        font=THEME_CONFIG["font_small"],
        padx=7,
        pady=4,
        bg=state["theme_use"]["bg_main"],
        fg=state["theme_use"]["fg_main"],
        insertbackground=state["theme_use"]["fg_main"],
        highlightbackground=state["theme_use"]["fg_main"],
        highlightcolor=state["theme_use"]["fg_main"],
    )
    task_description.grid(row=3, column=0, sticky="new", pady=10)

    add_btn = ttk.Button(
        frame,
        text="Добавить",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        style="Add.TButton",
        command=partial(
            add_task_controller, state, task_entry, task_description, window
        ),
    )
    add_btn.grid(row=4, column=0, sticky="ne")

    task_entry.focus()

    task_entry.bind("<Return>", lambda x: task_description.focus())

    task_description.bind(
        "<Return>",
        partial(on_text_enter, add_btn),
    )

    snap_data = get_data_from_form(task_description, task_entry)

    window.protocol(
        "WM_DELETE_WINDOW",
        partial(
            close_window_controller, window, snap_data, task_description, task_entry
        ),
    )

    window.bind(
        "<Escape>",
        partial(
            close_window_controller, window, snap_data, task_description, task_entry
        ),
    )

    return frame


def add_task_widget(state, id):
    task_widget = create_task_widget(state, id, state["tasks_frame"])

    task_widget.pack(anchor="nw", fill="x", pady=5, padx=(8, 16))

    state["tasks_widgets"][id] = task_widget


def create_calendar_window(state):
    if state["calendar_window"] is not None:
        return

    window = tk.Toplevel()
    window.title("Календарь")
    window.geometry("550x450")
    window.resizable(False, False)
    state["calendar_window"] = window

    window.rowconfigure(0, weight=0)
    window.rowconfigure(1, weight=7)
    window.columnconfigure(0, weight=9)
    window.columnconfigure(1, weight=0)
    window.protocol(
        "WM_DELETE_WINDOW", partial(callendar_window_controller, state, window)
    )

    calendar_top = create_calendar_top(window, state)
    calendar_top.grid(row=0, column=0, sticky="nesw")

    calendar_body = create_calendar_body(window, state)
    calendar_body.grid(row=1, column=0, sticky="nesw")

    calendar_btn_panel = create_calendar_btn_panel(window, state)
    calendar_btn_panel.grid(row=0, column=1, sticky="nesw", rowspan=2)

    window.bind("<Escape>", partial(callendar_window_controller, state, window))


def create_calendar_top(window, state):
    frame = ttk.Frame(window, padding=5)

    month_frame = create_month_frame(frame, state)
    month_frame.pack(anchor="center", pady=[10, 15])

    border = tk.Frame(frame, height=3, bg=state["theme_use"]["cal_bd"])
    border.pack(fill="x", side="bottom")

    return frame


def create_month_frame(parent, state):
    frame = ttk.Frame(parent)

    frame.columnconfigure(1, minsize=220)
    frame.columnconfigure((0, 2), weight=1)
    frame.rowconfigure(0, weight=1)

    date = state["date"].replace(day=1)
    month_year = format_date(
        state["date"], "LLLL y", locale=state["config"]["lang"]
    ).capitalize()

    state["calendar_info"] = {
        "date": date,
        "month_year": tk.StringVar(value=month_year),
    }

    prev_btn = ttk.Button(
        frame,
        image=state["icons"]["prev"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(calendar_month_frame_controller, state, False),
    )

    prev_btn.grid(row=0, column=0, sticky="nesw")

    month_label = ttk.Label(
        frame,
        textvariable=state["calendar_info"]["month_year"],
        style="Bordered.Medium.TLabel",
        anchor="center",
    )
    month_label.grid(row=0, column=1, sticky="nesw", padx=10)

    next_btn = ttk.Button(
        frame,
        image=state["icons"]["next"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(calendar_month_frame_controller, state, True),
    )

    next_btn.grid(row=0, column=2, sticky="nesw")

    return frame


def create_calendar_body(window, state):
    frame = ttk.Frame(window, padding=[10, 5])

    frame.rowconfigure(0, weight=0)
    frame.rowconfigure(1, weight=7)
    frame.columnconfigure(0, weight=1)

    week_frame = create_week_frame(state, frame)
    week_frame.grid(row=0, column=0, sticky="nesw", pady=5)

    content_frame = create_content_frame(frame, state)
    content_frame.grid(row=1, column=0, sticky="nesw")

    return frame


def create_week_frame(state, parent):
    frame = ttk.Frame(parent, borderwidth=1, relief="solid", style="Bordered.TFrame")

    days_dict = get_day_names("abbreviated", locale=state["config"]["lang"])

    weekdays = [days_dict[i].capitalize() for i in range(7)]

    for day in weekdays:
        day_label = ttk.Label(
            frame, text=day, anchor="center", style="Weekday.Bordered.Small.TLabel"
        )
        day_label.pack(side="left", fill="both", expand=True, ipady=3)

    return frame


def create_content_frame(parent, state):
    frame = ttk.Frame(parent, padding=[0, 10])

    frame.columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
    frame.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

    state["calendar_info"]["content_frame"] = frame

    calendar_content(state)

    return frame


def calendar_content(state):

    date = state["calendar_info"]["date"]

    matrix = get_month_matrix(date)

    for row in range(6):
        for col in range(7):
            value = matrix[row][col]

            btn = ttk.Button(
                state["calendar_info"]["content_frame"],
                takefocus=False,
                style="Disabled.TButton",
            )

            if value is not None:
                date = date.replace(day=value)

                hasfile = check_file(date)

                btn_style = get_btn_style(state, date, hasfile)

                btn.config(
                    text=value,
                    state="normal",
                    style=btn_style,
                    command=partial(refresh_content_controller, state, date),
                )

            else:
                btn.config(state="disable")

            btn.grid(row=row, column=col, sticky="nesw")


def create_calendar_btn_panel(window, state):
    frame = ttk.Frame(window)

    return frame


def refresh_app(state):
    for key in ["<Button-4>", "<Button-5>", "<MouseWheel>"]:
        state["root"].unbind_all(key)

    for widget in state["root"].winfo_children():
        widget.destroy()

    state = configure_state(state)

    apply_theme(state)

    create_layout(state["root"], state)


# =========================
# CONTROLLERS
# =========================


def refresh_content_controller(state, date):

    ismodified = check_ismodified(state)

    if ismodified:
        save = ask_to_save()

        if save:
            save_file_controller(state)

    state["date_info"]["date"] = date
    state["date_info"]["date_str_ru"].set(date.strftime("%d.%m.%Y"))

    state["deb_refresh_content"](state)

    if state["calendar_window"] is not None:
        state["deb_calendar_content"](state)


def toggle_theme_controller(state):
    theme = state["config"]["theme"]

    theme = "light" if theme == "dark" else "dark"

    state["config"]["theme"] = theme

    tasks.write_config(DATA_DIR, state["config"])

    refresh_app(state)


def toggle_task_controller(state, id, btn):
    done = tasks.toggle_task(state["tasks_data"], id)

    btn.config(image=get_check_icon(done, state["icons"]))

    configure_save_btn_state(state, "normal")


def save_task_controller(state, id, editor, window):
    title, description = get_data_for_manage(editor)

    title = trim_title(title)

    isvalid = validate_title(title)

    if not isvalid:
        messagebox.showinfo(
            parent=window,
            title="Валидация данных",
            message="Длина заголовка должна быть не менее 3 символов!",
        )
        return

    task = tasks.edit_task(state["tasks_data"], id, title, description)

    state["tasks_widgets"][id].task_title.set(title)

    configure_save_btn_state(state, "normal")

    window.grab_release()
    window.destroy()


def copy_controller(state, editor):
    data = editor.get("1.0", "end-1c")

    copy_to_clipboard(state["root"], data)


def delete_task_controller(state, id, window):
    close = messagebox.askyesno(
        parent=window,
        title="Подтвержение действия",
        message="Вы уверены что хотите удалить задачу?",
    )

    if not close:
        return

    if id in state["tasks_data"]:
        task = tasks.remove_task(state["tasks_data"], id)

    window.grab_release()
    window.destroy()

    state["tasks_widgets"][id].destroy()
    state["tasks_widgets"].pop(id)

    if not state["tasks_widgets"]:
        show_isempty(state["tasks_frame"])

    configure_save_btn_state(state, "normal")


def manage_task_controller(state, id):
    create_task_window(state, id)


def on_text_enter(btn, event):
    if event.state & 0x0001:
        return

    btn.invoke()
    return "break"


def add_task_controller(state, task_entry, task_description, window, event=None):

    title, description = get_data_for_add(task_entry, task_description)

    title = trim_title(title)

    isvalid = validate_title(title)

    if not isvalid:
        messagebox.showinfo(
            parent=window,
            title="Валидация данных",
            message="Длина заголовка должна быть не менее 3 символов!",
        )
        return

    id = tasks.add_task(state["tasks_data"], title, description)

    if not state["tasks_widgets"]:
        clear_frame(state["tasks_frame"])

    add_task_widget(state, id)

    configure_save_btn_state(state, "normal")

    window.grab_release()
    window.destroy()


def save_file_controller(state, event=None):
    save_tasks_ui(state)

    if state["calendar_window"] is not None:
        calendar_content(state)


def delete_file_controller(state, event=None):
    delete = messagebox.askyesno(
        title="Подтверждение действия",
        message="Вы уверены что хотите удалить список? Восстановить удаленные данные будет невозможно!",
    )

    if not delete:
        return

    res = tasks.delete_tasks_file(state["filename"], DATA_DIR)

    if not res:
        messagebox.showerror(
            title="Удаление данных",
            message="Произошла ошибка удаления! Попробуйте еще раз.",
        )

    state["tasks_data"] = tasks.reset_tasks_data(state["tasks_data"])
    update_tasks(state)


def calendar_month_frame_controller(state, isnext):

    date = state["calendar_info"]["date"].replace(day=1)
    delta = relativedelta(months=1)

    date = date + delta if isnext else date - delta

    month_year = format_date(
        date, "LLLL y", locale=state["config"]["lang"]
    ).capitalize()

    state["calendar_info"]["date"] = date
    state["calendar_info"]["month_year"].set(month_year)

    state["deb_calendar_content"](state)


def callendar_window_controller(state, window, event=None):
    window.destroy()

    state["calendar_window"] = None


def close_window_controller(window, snap_data, editor, entry=None, event=None):
    data = get_data_from_form(editor, entry)

    if snap_data != data:
        close = ask_to_close(window)

        if not close:
            return

    window.grab_release()
    window.destroy()


def app_exit_controller(state, event=None):

    ismodified = check_ismodified(state)

    if ismodified:
        save = ask_to_save()

        if save:
            save_file_controller(state)

    state["root"].destroy()


# =========================
# MODEL ADAPTERS
# =========================


def on_mousewheel(scroll_frame, event):
    if event.num == 4:
        scroll_frame._parent_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        scroll_frame._parent_canvas.yview_scroll(1, "units")
    else:
        scroll_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def limit_scroll(frame, event):
    y_pos = frame._parent_canvas.yview()[0]
    if y_pos <= 0:
        if (event.delta and event.delta > 0) or (event.num == 4):
            return "break"


def reload_data(state):
    frame = state.get("tasks_frame")
    if frame is not None:
        clear_frame(frame)

        state["tasks_widgets"].clear()

    state["filename"] = get_filename_from_date(state["date"])

    state["tasks_data"] = load_tasks_ui(state["filename"])
    state["snapshot"] = deepcopy(state["tasks_data"])


def load_tasks_ui(filename):
    tasks_data = tasks.load_tasks(filename, DATA_DIR)

    if tasks_data is None:
        messagebox.showerror(
            title="Ошибка чтения данных",
            message="Файл поврежден! Сохранена резервная копия файла.",
        )
        tasks_data = {}

    return tasks_data


def save_tasks_ui(state):

    res = tasks.sync_tasks_data(state["tasks_data"], state["filename"], DATA_DIR)

    if res:
        state["snapshot"] = deepcopy(state["tasks_data"])

        configure_delete_btn_state(state)
        configure_save_btn_state(state, "disable")

    else:
        messagebox.showerror(
            title="Сохранение данных",
            message="Не удалось сохранить изменения! Попробуйте еще раз.",
        )


def check_file(date):
    filename = get_filename_from_date(date)
    path = DATA_DIR / filename

    return path.exists()


def copy_to_clipboard(root, data):
    root.clipboard_clear()
    root.clipboard_append(data)
    root.update()


# =========================
# HELPERS
# =========================


def get_theme(config):
    if config["theme"] == "dark":
        return DARK_THEME, DARK_DIR
    else:
        return LIGHT_THEME, LIGHT_DIR


def get_filename_from_date(date):
    return date.strftime("%Y_%m_%d") + ".json"


def get_check_icon(isdone, icons):
    return icons["checked"] if isdone else icons["unchecked"]


def validate_title(title):
    return len(title) >= 3 and not title.isspace()


def get_data_for_manage(editor):
    title = editor.get("1.0", "1.end")
    description = editor.get("2.0", "end-1c")

    return title, description


def get_data_for_add(entry, text):
    title = entry.get()
    description = text.get("1.0", "end-1c")

    return title, description


def get_data_from_form(editor, entry=None):
    data = {}

    if entry is not None:
        data["title"], data["description"] = get_data_for_add(entry, editor)

    else:
        data["title"], data["description"] = get_data_for_manage(editor)

    return data


def trim_title(title):
    return title.strip()


def erase_editor(editor):
    editor.delete("1.0", "end")


def check_ismodified(state):
    return state["tasks_data"] != state["snapshot"]


def get_btn_style(state, date, isnotempty):
    tday = datetime.date.today()

    if tday == date:
        btn_style = "Today.Day.TButton"
    elif state["date"] == date:
        btn_style = "Current.Day.TButton"
    else:
        btn_style = "Day.TButton"

    if isnotempty:
        btn_style = "Notempty." + btn_style

    return btn_style


def configure_delete_btn_state(state):
    hasfile = check_file(state["date"])

    if hasfile:
        state["btns"]["del_btn"].config(state="normal")
    else:
        state["btns"]["del_btn"].config(state="disable")


def configure_save_btn_state(state, btn_state):
    state["btns"]["save_btn"].config(state=btn_state)


def get_month_matrix(date):
    delta = datetime.timedelta(days=1)

    matrix = [[None for _ in range(7)] for _ in range(6)]

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


def ask_to_save(window=None):
    res = messagebox.askyesno(
        parent=window,
        title="Подтверждение действия",
        message="У вас есть несохраненные изменения.\nВыполнить сохранение?",
    )

    return res


def ask_to_close(window=None):
    res = messagebox.askyesno(
        parent=window,
        title="Подтверждение действия",
        message="Вы уверены что хотите закрыть окно? Все несохранненые изменения будут утеряны.",
    )

    return res


# =========================
# HOTKEYS
# =========================


def register_hotkeys(root, state, hotkeys):

    for key, handler in hotkeys.items():
        root.bind(key, partial(handler, state))


# =========================
# LAYOUT
# =========================


def create_layout(root, state):
    root.title("Listy v0.3")
    root.iconphoto(True, state["icons"]["favicon"])
    root.geometry("550x750")
    root.resizable(False, False)

    root.protocol("WM_DELETE_WINDOW", partial(app_exit_controller, state))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=0)
    root.rowconfigure(1, weight=5)
    root.rowconfigure(2, weight=0)

    top = create_top(state)
    top.grid(row=0, column=0, sticky="nsew")

    body = create_body(state)
    body.grid(row=1, column=0, sticky="nsew")

    footer = create_footer(state)
    footer.grid(row=2, column=0, sticky="nsew")


# =========================
# APP STATE
# =========================


def configure_state(state):
    state["body"] = None
    state["tasks_frame"] = None
    state["tasks_widgets"] = {}
    state["btns"] = {}
    state["calendar_window"] = None

    state["config"] = tasks.load_config(CONFIG_FILE)

    return state


# =========================
# ENTRY POINT
# =========================


def run_gui():
    root = tk.Tk()

    state = {
        "date": None,
        "root": root,
        "tasks_data": None,
        "snapshot": {},
        "calendar_info": None,
        "filename": None,
    }

    configure_state(state)

    state["deb_refresh_content"] = debounce(state["root"], refresh_content, 700)

    state["deb_calendar_content"] = debounce(state["root"], calendar_content, 700)

    apply_theme(state)

    create_layout(root, state)

    hotkeys = {
        "<Control-s>": save_file_controller,
        "<Control-n>": create_add_task_window,
        "<Delete>": delete_file_controller,
        "<Escape>": app_exit_controller,
    }

    register_hotkeys(root, state, hotkeys)

    root.mainloop()
