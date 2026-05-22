"""spores/io.py"""

import json
import os
import tempfile
from typing import List, Tuple
from core import JSONEncoder
from struts import ux_format
from constants import Prisma

class LocalFileSporeLoader:
    def __init__(self, directory="memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_spore(self, filename, data):
        temp_path = None
        if os.path.isabs(filename) or os.path.dirname(filename) == self.directory:
            final_path = filename
        else:
            final_path = os.path.join(self.directory, os.path.basename(filename))
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        try:
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(final_path), text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=JSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, final_path)
            return final_path
        except (IOError, OSError, TypeError) as e:
            if msg := ux_format("spore_strings", "loader_save_err", e=e):
                print(f"{Prisma.RED}{msg}{Prisma.RST}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    @staticmethod
    def load_spore(filepath):
        if not os.path.exists(filepath):
            if msg := ux_format("spore_strings", "loader_not_found", filepath=filepath):
                print(f"{Prisma.RED}{msg}{Prisma.RST}")
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            err_type = "loader_corrupt" if isinstance(e, json.JSONDecodeError) else "loader_read_err"
            if msg := ux_format("spore_strings", err_type, filepath=filepath, e=e):
                print(f"{Prisma.RED}{msg}{Prisma.RST}")
            return None

    def list_spores(self) -> List[Tuple[str, float, str]]:
        if not os.path.exists(self.directory):
            return []
        try:
            files = []
            with os.scandir(self.directory) as it:
                for entry in it:
                    if entry.is_file() and entry.name.endswith(".json") and entry.name.startswith("session_"):
                        files.append((entry.path, entry.stat().st_mtime, entry.name))
            return sorted(files, key=lambda x: x[1], reverse=True)
        except OSError:
            return []

    @staticmethod
    def delete_spore(filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False
