"""spores/io.py"""

import json
import os
import tempfile
from typing import Any, List, Optional, Tuple

from constants import Prisma
from core import JSONEncoder
from struts import ux_format


class LocalFileSporeLoader:
    def __init__(self, directory: str = "memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_spore(self, filename: str, data: Any) -> Optional[str]:
        temp_path: Optional[str] = None
        base_dir = os.path.realpath(self.directory)
        if os.path.isabs(filename):
            final_path = os.path.realpath(filename)
        else:
            final_path = os.path.realpath(
                os.path.join(base_dir, os.path.basename(filename))
            )
        if os.path.commonpath([base_dir, final_path]) != base_dir:
            if msg := ux_format(
                "spore_strings", "loader_save_err", e="Path traversal violation"
            ):
                print(f"{Prisma.RED}{msg} ({filename}){Prisma.RST}")
            return None
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        try:
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(final_path), text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=JSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            if isinstance(temp_path, str):
                os.replace(temp_path, final_path)
            return final_path
        except (IOError, OSError, TypeError) as e:
            if msg := ux_format("spore_strings", "loader_save_err", e=e):
                print(f"{Prisma.RED}{msg}{Prisma.RST}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    def load_spore(self, filepath: str) -> Optional[Any]:
        base_dir = os.path.realpath(self.directory)
        final_path = os.path.realpath(
            os.path.join(base_dir, os.path.basename(filepath))
        )
        if not os.path.exists(final_path):
            if msg := ux_format(
                "spore_strings", "loader_not_found", filepath=final_path
            ):
                print(f"{Prisma.RED}{msg}{Prisma.RST}")
            return None
        try:
            with open(final_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            err_type = (
                "loader_corrupt"
                if isinstance(e, json.JSONDecodeError)
                else "loader_read_err"
            )
            if msg := ux_format("spore_strings", err_type, filepath=filepath, e=e):
                print(f"{Prisma.RED}{msg}{Prisma.RST}")
            return None

    def list_spores(self) -> List[Tuple[str, float, str]]:
        if not os.path.exists(self.directory):
            return []
        try:
            with os.scandir(self.directory) as it:
                files = [
                    (e.path, e.stat().st_mtime, e.name)
                    for e in it
                    if e.is_file()
                    and e.name.endswith(".json")
                    and e.name.startswith("session_")
                ]
            return sorted(files, key=lambda x: x[1], reverse=True)
        except OSError:
            return []

    def delete_spore(self, filepath: str):
        base_dir = os.path.realpath(self.directory)
        final_path = os.path.realpath(
            os.path.join(base_dir, os.path.basename(filepath))
        )
        try:
            os.remove(final_path)
            return True
        except OSError:
            return False
