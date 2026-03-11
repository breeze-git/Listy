import json
import uuid
import logging
from pathlib import Path

from config import DEFAULT_SETTINGS


def load_tasks(filename, path):
    fpath = path / filename

    try:
        with open(fpath, "r", encoding="UTF-8") as finp:
            data = json.load(finp)

            return data["tasks"]
    except FileNotFoundError:
        logging.info("Файл не найден:")
        return {}
    except (json.JSONDecodeError, KeyError):
        logging.exception("Ошибка чтения JSON:")

        try:
            fpath.rename(fpath.with_name(fpath.name + ".broken"))
        except OSError:
            logging.exception("Ошибка сохранения .broken файла:")

        return None


def add_task(tasks_data, title, description):
    id = str(uuid.uuid4())

    tasks_data[id] = {
        "title": title,
        "description": description,
        "done": False,
    }

    return id


def edit_task(tasks_data, id, title, description):
    tasks_data[id]["title"] = title
    tasks_data[id]["description"] = description

    return tasks_data[id]


def toggle_task(tasks_data, id):
    done = not tasks_data[id]["done"]
    tasks_data[id]["done"] = done

    return done


def remove_task(tasks_data, id):
    task = tasks_data.pop(id, False)

    return task


def save_tasks(tasks_data, filename, path):
    path.mkdir(parents=True, exist_ok=True)

    fpath = path / filename
    tpath = fpath.with_name(fpath.name + ".tmp")

    data = {"tasks": tasks_data}

    try:
        with open(tpath, "w", encoding="UTF-8") as fout:
            json.dump(data, fout, indent=4, ensure_ascii=False)
    except OSError:
        logging.exception("Ошибка системы:")
        return False

    tpath.replace(fpath)
    return True


def delete_tasks_file(filename, path):
    fpath = path / filename

    try:
        fpath.unlink(missing_ok=True)
    except OSError:
        logging.exception("Ошибка системы:")
        return False

    return True


def sync_tasks_data(tasks_data, filename, path):
    try:
        if not tasks_data:
            return delete_tasks_file(filename, path)

        return save_tasks(tasks_data, filename, path)
    except OSError:
        logging.exception("Ошибка системы:")
        return False


def load_config(path):
    try:
        with open(path, "r", encoding="UTF-8") as finp:
            return json.load(finp)
    except FileNotFoundError:
        logging.info("Файл не найден:")
        return DEFAULT_SETTINGS
    except json.JSONDecodeError:
        logging.exception("Ошибка чтения JSON:")
        return DEFAULT_SETTINGS


def write_config(path, config):
    path.mkdir(parents=True, exist_ok=True)
    fpath = path / "config.json"

    try:
        with open(fpath, "w", encoding="UTF-8") as fout:
            json.dump(config, fout, indent=4, ensure_ascii=False)
    except OSError:
        logging.exception("Ошибка системы:")
        return False

    return True
