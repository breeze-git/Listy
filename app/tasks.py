import json
import logging
import uuid
from pathlib import Path

# =========================
# TASKS
# =========================


class Tasks:
    data: dict[str, dict[str, str | bool]] | None
    filename: str
    path: Path

    def __init__(self, filename: str, path: Path):
        self.data = {}
        self.filename = filename
        self.path = path

        self.load_tasks()

    def add_task(self, title: str, description: str) -> str | None:
        id = str(uuid.uuid4())

        if self.data is None:
            return

        self.data[id] = {
            "title": title,
            "description": description,
            "done": False,
        }

        return id

    def edit_task(self, id: str, title: str, description: str) -> dict | None:

        if self.data is None:
            return

        self.data[id]["title"] = title
        self.data[id]["description"] = description

        return self.data[id]

    def toggle_task(self, id: str) -> bool | None:

        if self.data is None:
            return

        done = not self.data[id]["done"]
        self.data[id]["done"] = done

        return done

    def remove_task(self, id: str) -> dict | bool | None:

        if self.data is None:
            return

        task = self.data.pop(id, False)

        return task

    def sync_tasks_data(self) -> bool:
        try:
            if not self.data:
                return self.delete_tasks_file()

            return self.save_tasks()
        except OSError:
            logging.exception("Ошибка системы:")
            return False

    def load_tasks(self) -> None:
        fpath = self.path / self.filename

        try:
            with open(fpath, "r", encoding="UTF-8") as finp:
                data = json.load(finp)

                self.data = data["tasks"]
        except FileNotFoundError:
            logging.info("Файл не найден:")
            self.data = {}
        except (json.JSONDecodeError, KeyError):
            logging.exception("Ошибка чтения JSON:")

            try:
                fpath.rename(fpath.with_name(fpath.name + ".broken"))
            except OSError:
                logging.exception("Ошибка сохранения .broken файла:")

            self.data = None

    def save_tasks(self) -> bool:
        self.path.mkdir(parents=True, exist_ok=True)

        fpath = self.path / self.filename
        tpath = fpath.with_name(fpath.name + ".tmp")

        data = {"tasks": self.data}

        try:
            with open(tpath, "w", encoding="UTF-8") as fout:
                json.dump(data, fout, indent=4, ensure_ascii=False)
        except OSError:
            logging.exception("Ошибка системы:")
            return False

        tpath.replace(fpath)
        return True

    def delete_tasks_file(self) -> bool:
        fpath = self.path / self.filename

        try:
            fpath.unlink(missing_ok=True)
        except OSError:
            logging.exception("Ошибка системы:")
            return False

        return True
