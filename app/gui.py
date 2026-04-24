import datetime
import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

import customtkinter as ctk
from babel.dates import format_date, get_day_names

import controllers
import helpers
from config import ICONS_DIR
from styles import THEME_CONFIG

if TYPE_CHECKING:
    from listy import TodoApp


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


def apply_theme(app: "TodoApp") -> None:
    theme, theme_dir = helpers.get_theme(app.config)

    app.icons = load_icons(ICONS_DIR, theme_dir)
    app.theme_use = theme

    configure_theme(app.root, theme)

    ctk.set_appearance_mode(app.config["theme"])


# =========================
# VIEW
# =========================


def create_top(app: "TodoApp") -> ttk.Frame:
    frame = ttk.Frame(app.root, padding=5)

    frame.grid_columnconfigure(0, minsize=220)
    frame.columnconfigure(0, weight=0)
    frame.columnconfigure(1, weight=2)
    frame.columnconfigure(2, weight=1)

    frame.rowconfigure((0, 1), weight=1)

    if app.date is not None:
        app.date_info.date = app.date
    else:
        app.date = app.date_info.date

    app.set_date_info()

    wday_label = ttk.Label(
        frame, textvariable=app.date_info.weekday, style="Bold.TLabel"
    )
    wday_label.grid(row=0, column=0, sticky="nesw")

    date_text = ttk.Label(
        frame, textvariable=app.date_info.day_month, style="Big.TLabel"
    )
    date_text.grid(row=1, column=0, sticky="nesw")

    dateframe = create_dateframe(app, frame)
    dateframe.grid(row=0, column=1, sticky="ne")

    theme_btn = ttk.Button(
        frame,
        image=app.icons["theme"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(controllers.toggle_theme_controller, app),
    )
    theme_btn.grid(row=0, column=2, sticky="ne")

    calendar_btn = ttk.Button(
        frame,
        image=app.icons["calendar"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(create_calendar_window, app),
    )

    calendar_btn.grid(row=1, column=2, sticky="se")

    return frame


def create_dateframe(app: "TodoApp", parent: ttk.Frame) -> ttk.Frame:
    frame = ttk.Frame(parent)

    frame.columnconfigure((0, 1, 2), weight=1)
    frame.rowconfigure(0, weight=1)

    delta = datetime.timedelta(days=1)

    prev_btn = ttk.Button(
        frame,
        image=app.icons["prev"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=lambda: controllers.refresh_content_controller(
            app, app.date_info.date - delta
        ),
    )

    prev_btn.grid(row=0, column=0, sticky="nesw", padx=10)

    date = ttk.Label(
        frame,
        textvariable=app.date_info.date_str_ru,
        style="Bordered.Medium.TLabel",
    )

    date.grid(row=0, column=1, sticky="nesw")

    next_btn = ttk.Button(
        frame,
        image=app.icons["next"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=lambda: controllers.refresh_content_controller(
            app, app.date_info.date + delta
        ),
    )

    next_btn.grid(row=0, column=2, sticky="nesw", padx=10)

    app.root.bind("<Left>", lambda e: prev_btn.invoke())
    app.root.bind("<Right>", lambda e: next_btn.invoke())

    return frame


def create_body(app: "TodoApp") -> ttk.Frame:
    frame = ttk.Frame(app.root)

    app.body = frame

    app.update_tasks()

    tasks_frame = app.tasks_frame
    tasks_frame.pack(anchor="center", fill="both", expand=True)

    tasks_frame.bind_all("<Button-4>", partial(on_mousewheel, tasks_frame))
    tasks_frame.bind_all("<Button-5>", partial(on_mousewheel, tasks_frame))

    tasks_frame._parent_canvas.bind("<MouseWheel>", partial(limit_scroll, tasks_frame))
    tasks_frame._parent_canvas.bind("<Button-4>", partial(limit_scroll, tasks_frame))

    return frame


def refresh_tasks_list(app: "TodoApp") -> ctk.CTkScrollableFrame:
    tasks_data = app.tasks_data.data

    frame = app.tasks_frame

    if frame is None:
        frame = ctk.CTkScrollableFrame(
            app.body,
            fg_color=(
                "#ffffff",
                "#1A1A1A",
            ),
            label_anchor="w",
        )
        frame._scrollbar.configure(width=0, height=0)

    frame._parent_canvas.yview_moveto(0)

    if not tasks_data:
        helpers.show_isempty(frame)

    for id in tasks_data:
        task_frame = create_task_widget(app, id, frame)

        task_frame.pack(anchor="nw", fill="x", pady=5, padx=(8, 16))

        app.tasks_widgets[id] = task_frame

    return frame


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.update_idletasks()


def create_task_widget(
    app: "TodoApp", id: str, parent: ctk.CTkScrollableFrame
) -> ttk.Frame:
    task_frame = ttk.Frame(
        parent, padding=5, borderwidth=1, relief="solid", style="Task.TFrame"
    )

    title = app.tasks_data.data[id]["title"]

    task_frame.task_title = tk.StringVar(value=title)

    task_frame.columnconfigure((0, 2), weight=0)
    task_frame.columnconfigure(1, weight=4)
    task_frame.rowconfigure(0, weight=1)

    check_image = helpers.get_check_icon(app.tasks_data.data[id]["done"], app.icons)

    check_btn = ttk.Button(
        task_frame,
        image=check_image,
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
    )
    check_btn.config(
        command=partial(controllers.toggle_task_controller, app, id, check_btn)
    )
    check_btn.grid(row=0, column=0, sticky="w")

    task_text = ttk.Label(
        task_frame, textvariable=task_frame.task_title, style="Medium.TLabel"
    )
    task_text.grid(row=0, column=1, sticky="w")

    manage_btn = ttk.Button(
        task_frame,
        image=app.icons["manage32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(manage_task_controller, app, id),
    )
    manage_btn.grid(row=0, column=2, sticky="e")

    bind_recursive(task_frame, lambda e: limit_scroll(parent, e))

    return task_frame


def bind_recursive(widget, callback):
    widget.bind("<MouseWheel>", callback)
    widget.bind("<Button-4>", callback)
    for child in widget.winfo_children():
        bind_recursive(child, callback)


def create_task_window(app: "TodoApp", id: str) -> None:
    window = tk.Toplevel()
    window.title("Просмотр и изменение задачи")
    window.geometry("500x400")
    window.resizable(False, False)

    manage_panel = create_manage_panel(window, app, id)
    manage_panel.pack(fill="both", expand=True)

    window.grab_set()


def create_manage_panel(window: tk.Toplevel, app: "TodoApp", id: str) -> ttk.Frame:
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
        bg=app.theme_use["bg_main"],
        fg=app.theme_use["fg_main"],
        insertbackground=app.theme_use["fg_main"],
    )
    editor.insert(1.0, app.tasks_data.data[id]["title"] + "\n")
    editor.insert(2.0, app.tasks_data.data[id]["description"])
    editor.grid(row=0, column=0, columnspan=5)

    save_btn = ttk.Button(
        frame,
        image=app.icons["save32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(controllers.save_task_controller, app, id, editor, window),
    )
    save_btn.grid(row=1, column=1, pady=5)

    copy_btn = ttk.Button(
        frame,
        image=app.icons["copy32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(controllers.copy_controller, app, editor),
    )
    copy_btn.grid(row=1, column=2, pady=5)

    erase_btn = ttk.Button(
        frame,
        image=app.icons["erase32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(helpers.erase_editor, editor),
    )
    erase_btn.grid(row=1, column=3, pady=5)

    delete_btn = ttk.Button(
        frame,
        image=app.icons["delete32"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(controllers.delete_task_controller, app, id, window),
    )
    delete_btn.grid(row=1, column=4, pady=5)

    editor.focus()

    editor.bind("<Control-s>", lambda e: save_btn.invoke())

    editor.bind("<Control-c>", lambda e: copy_btn.invoke())

    editor.bind("<Control-e>", lambda e: erase_btn.invoke())

    editor.bind("<Delete>", lambda e: delete_btn.invoke())

    snap_data = helpers.get_data_from_form(editor)

    window.protocol(
        "WM_DELETE_WINDOW",
        partial(controllers.close_window_controller, window, snap_data, editor),
    )

    window.bind(
        "<Escape>",
        partial(controllers.close_window_controller, window, snap_data, editor, None),
    )

    return frame


def create_footer(app: "TodoApp") -> ttk.Frame:
    frame = ttk.Frame(app.root, padding=5)

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=5)

    add_btn = ttk.Button(
        frame,
        image=app.icons["add"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(create_add_task_window, app),
    )
    add_btn.grid(row=0, column=0, sticky="w")

    btns_frame = ttk.Frame(frame)
    btns_frame.rowconfigure(0, weight=1)
    btns_frame.columnconfigure((0, 1), weight=1)

    save_btn = ttk.Button(
        btns_frame,
        image=app.icons["save"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(controllers.save_file_controller, app),
    )
    save_btn.grid(row=0, column=0, sticky="e", padx=5)

    delete_btn = ttk.Button(
        btns_frame,
        image=app.icons["delete"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        state="disable",
        command=partial(controllers.delete_file_controller, app),
    )
    delete_btn.grid(row=0, column=1, sticky="e", padx=5)

    btns_frame.grid(row=0, column=1, sticky="e")

    app.btns["del_btn"] = delete_btn
    app.btns["save_btn"] = save_btn

    helpers.configure_delete_btn_state(app)

    ismodified = helpers.check_ismodified(app)

    if not ismodified:
        helpers.configure_save_btn_state(app, "disable")

    return frame


def create_add_task_window(app: "TodoApp", event: None | tk.Event = None) -> None:
    window = tk.Toplevel()
    window.title("Добавить задачу")
    window.geometry("400x400")
    window.resizable(False, False)

    add_frame = create_add_frame(window, app)
    add_frame.pack(fill="both", expand=True)

    window.grab_set()


def create_add_frame(window: tk.Toplevel, app: "TodoApp") -> ttk.Frame:
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
        background=app.theme_use["bg_main"],
        foreground=app.theme_use["fg_main"],
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
        bg=app.theme_use["bg_main"],
        fg=app.theme_use["fg_main"],
        insertbackground=app.theme_use["fg_main"],
        highlightbackground=app.theme_use["fg_main"],
        highlightcolor=app.theme_use["fg_main"],
    )
    task_description.grid(row=3, column=0, sticky="new", pady=10)

    add_btn = ttk.Button(
        frame,
        text="Добавить",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        style="Add.TButton",
        command=partial(add_task_controller, app, task_entry, task_description, window),
    )
    add_btn.grid(row=4, column=0, sticky="ne")

    task_entry.focus()

    task_entry.bind("<Return>", lambda x: task_description.focus())

    task_description.bind(
        "<Return>",
        partial(on_text_enter, add_btn),
    )

    snap_data = helpers.get_data_from_form(task_description, task_entry)

    window.protocol(
        "WM_DELETE_WINDOW",
        partial(
            controllers.close_window_controller,
            window,
            snap_data,
            task_description,
            task_entry,
        ),
    )

    window.bind(
        "<Escape>",
        partial(
            controllers.close_window_controller,
            window,
            snap_data,
            task_description,
            task_entry,
        ),
    )

    return frame


def add_task_widget(app: "TodoApp", id: str) -> None:
    task_widget = create_task_widget(app, id, app.tasks_frame)

    task_widget.pack(anchor="nw", fill="x", pady=5, padx=(8, 16))

    app.tasks_widgets[id] = task_widget


def create_calendar_window(app: "TodoApp") -> None:
    if app.calendar_window is not None:
        return

    window = tk.Toplevel()
    window.title("Календарь")
    window.geometry("550x450")
    window.resizable(False, False)
    app.calendar_window = window

    window.rowconfigure(0, weight=0)
    window.rowconfigure(1, weight=7)
    window.columnconfigure(0, weight=9)
    window.columnconfigure(1, weight=0)
    window.protocol(
        "WM_DELETE_WINDOW", partial(controllers.calendar_window_controller, app, window)
    )

    calendar_top = create_calendar_top(window, app)
    calendar_top.grid(row=0, column=0, sticky="nesw")

    calendar_body = create_calendar_body(window, app)
    calendar_body.grid(row=1, column=0, sticky="nesw")

    window.bind(
        "<Escape>", partial(controllers.calendar_window_controller, app, window)
    )


def create_calendar_top(window: tk.Toplevel, app: "TodoApp") -> ttk.Frame:
    frame = ttk.Frame(window, padding=5)

    month_frame = create_month_frame(frame, app)
    month_frame.pack(anchor="center", pady=[10, 15])

    border = tk.Frame(frame, height=3, bg=app.theme_use["cal_bd"])
    border.pack(fill="x", side="bottom")

    return frame


def create_month_frame(parent: ttk.Frame, app: "TodoApp") -> ttk.Frame:
    frame = ttk.Frame(parent)

    frame.columnconfigure(1, minsize=220)
    frame.columnconfigure((0, 2), weight=1)
    frame.rowconfigure(0, weight=1)

    date = app.date.replace(day=1)
    month_year = format_date(app.date, "LLLL y", locale=app.config["lang"]).capitalize()

    app.calendar_info.date = date
    app.calendar_info.month_year.set(month_year)

    prev_btn = ttk.Button(
        frame,
        image=app.icons["prev"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(controllers.calendar_month_frame_controller, app, False),
    )

    prev_btn.grid(row=0, column=0, sticky="nesw")

    month_label = ttk.Label(
        frame,
        textvariable=app.calendar_info.month_year,
        style="Bordered.Medium.TLabel",
        anchor="center",
    )
    month_label.grid(row=0, column=1, sticky="nesw", padx=10)

    next_btn = ttk.Button(
        frame,
        image=app.icons["next"],
        style="Flat.TButton",
        takefocus=THEME_CONFIG["btn_focus"],
        cursor=THEME_CONFIG["btn_cursor"],
        command=partial(controllers.calendar_month_frame_controller, app, True),
    )

    next_btn.grid(row=0, column=2, sticky="nesw")

    return frame


def create_calendar_body(window: tk.Toplevel, app: "TodoApp") -> ttk.Frame:
    frame = ttk.Frame(window, padding=[10, 5])

    frame.rowconfigure(0, weight=0)
    frame.rowconfigure(1, weight=7)
    frame.columnconfigure(0, weight=1)

    week_frame = create_week_frame(app, frame)
    week_frame.grid(row=0, column=0, sticky="nesw", pady=5)

    content_frame = create_content_frame(frame, app)
    content_frame.grid(row=1, column=0, sticky="nesw")

    return frame


def create_week_frame(app: "TodoApp", parent: ttk.Frame) -> ttk.Frame:
    frame = ttk.Frame(parent, borderwidth=1, relief="solid", style="Bordered.TFrame")

    days_dict = get_day_names("abbreviated", locale=app.config["lang"])

    weekdays = [days_dict[i].capitalize() for i in range(7)]

    for day in weekdays:
        day_label = ttk.Label(
            frame, text=day, anchor="center", style="Weekday.Bordered.Small.TLabel"
        )
        day_label.pack(side="left", fill="both", expand=True, ipady=3)

    return frame


def create_content_frame(parent: ttk.Frame, app: "TodoApp") -> ttk.Frame:
    frame = ttk.Frame(parent, padding=[0, 10])

    frame.columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
    frame.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

    app.calendar_info.content_frame = frame

    app.calendar_content()

    return frame


def create_calendar_content(app: "TodoApp", matrix: list, date: datetime.date) -> None:
    for row in range(6):
        for col in range(7):
            value = matrix[row][col]

            btn = ttk.Button(
                app.calendar_info.content_frame,
                takefocus=False,
                style="Disabled.TButton",
            )

            if value != 0:
                date = date.replace(day=value)

                hasfile = helpers.check_file(date)

                btn_style = helpers.get_btn_style(app, date, hasfile)

                btn.config(
                    text=value,
                    state="normal",
                    style=btn_style,
                    command=partial(controllers.refresh_content_controller, app, date),
                )

            else:
                btn.config(state="disable")

            btn.grid(row=row, column=col, sticky="nesw")


# =========================
# CONTROLLERS / MODEL ADAPTERS
# =========================


def manage_task_controller(app: "TodoApp", id: str) -> None:
    create_task_window(app, id)


def on_text_enter(btn: ttk.Button, event: tk.Event) -> None | str:
    if event.state & 0x0001:
        return

    btn.invoke()
    return "break"


def add_task_controller(
    app: "TodoApp",
    task_entry: ttk.Entry,
    task_description: tk.Text,
    window: tk.Toplevel,
    event: None | tk.Event = None,
) -> None:

    title, description = helpers.get_data_for_add(task_entry, task_description)

    title = helpers.trim_title(title)

    isvalid = helpers.validate_title(title)

    if not isvalid:
        messagebox.showinfo(
            parent=window,
            title="Валидация данных",
            message="Длина заголовка должна быть не менее 3 символов!",
        )
        return

    id = app.tasks_data.add_task(title, description)

    if not app.tasks_widgets:
        clear_frame(app.tasks_frame)

    add_task_widget(app, id)

    helpers.configure_save_btn_state(app, "normal")

    window.grab_release()
    window.destroy()


def on_mousewheel(scroll_frame: ctk.CTkScrollableFrame, event: tk.Event) -> None:
    if event.num == 4:
        scroll_frame._parent_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        scroll_frame._parent_canvas.yview_scroll(1, "units")
    else:
        scroll_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def limit_scroll(frame: ctk.CTkScrollableFrame, event: tk.Event) -> None | str:
    y_pos = frame._parent_canvas.yview()[0]
    if y_pos <= 0:
        if (event.delta and event.delta > 0) or (event.num == 4):
            return "break"


# =========================
# LAYOUT
# =========================


def create_layout(root: tk.Tk, app: "TodoApp") -> None:
    root.title("Listy v0.3")
    root.iconphoto(True, app.icons["favicon"])
    root.geometry("550x750")
    root.resizable(False, False)

    root.protocol("WM_DELETE_WINDOW", partial(controllers.app_exit_controller, app))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=0)
    root.rowconfigure(1, weight=5)
    root.rowconfigure(2, weight=0)

    top = create_top(app)
    top.grid(row=0, column=0, sticky="nsew")

    body = create_body(app)
    body.grid(row=1, column=0, sticky="nsew")

    footer = create_footer(app)
    footer.grid(row=2, column=0, sticky="nsew")
