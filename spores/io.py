"""spores/io.py
This module handles the physical storage and retrieval of "Spores" (session states).
If genetics.py handles the biological blueprint, this file handles the amber
that preserves the DNA. It ensures that memory states are safely written to
disk without risking data corruption during sudden system crashes or power loss.
Classes:
    - LocalFileSporeLoader: The primary interface for reading, writing, and pruning
      dormant memory states on the local file system.
"""
import json
import os
import tempfile
from typing import List, Tuple
from core import BoneJSONEncoder
from struts import ux_format
from constants import Prisma


class LocalFileSporeLoader:
    """
    Manages the Input/Output lifecycle of Spore files.
    Acts as the physical substrate layer, translating active memory graphs into
    dormant JSON structures and storing them safely on the disk.
    """

    def __init__(self, directory="memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_spore(self, filename, data):
        """
        Preserves the active memory state to disk using an atomic write pattern.
        We NEVER write directly over an existing memory file.
        If the process dies halfway through a direct write, the JSON is corrupted,
        and the spore is dead. Instead, we write to a temporary file, flush the buffer,
        and then execute an atomic OS-level replacement.
        """
        temp_path = None
        if os.path.isabs(filename) or os.path.dirname(filename) == self.directory:
            final_path = filename
        else:
            final_path = os.path.join(self.directory, os.path.basename(filename))
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        try:
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(final_path), text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=BoneJSONEncoder)
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
        """
        Thaws a dormant Spore file back into active memory dictionaries.
        Validates the file existence and structural integrity (valid JSON) before returning.
        """
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
        """
        Surveys the memory directory and returns a chronologically sorted list
        of all valid session spores. Used for lineage tracking and cross-over selection.
        """
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
        """
        Prunes a specific spore from the disk permanently.
        """
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False
