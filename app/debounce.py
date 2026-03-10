import tkinter as tk


def debounce(root, func, ms):
    timeout = None

    def wrapper(*args, **kwargs):
        nonlocal timeout
        if timeout:
            root.after_cancel(timeout)
        timeout = root.after(ms, lambda: func(*args, **kwargs))

    return wrapper
