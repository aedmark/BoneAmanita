""" bone_data.py - The Living Mythology (Lazy Loaded) """
import json, os, random
from enum import Enum
from typing import Dict, Any, Tuple, cast, List, Optional
from bone_bus import Prisma

class LoreCategory(Enum):
    LEXICON = "LEXICON"
    SCENARIOS = "scenarios"
    GORDON = "gordon"
    GENETICS = "genetics"
    DEATH = "death"

class LoreManifest:
    _INSTANCE = None
    DATA_DIR = "lore"

    def __init__(self):
        self._cache = {}
        self._overlays = {}

    @classmethod
    def get_instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = LoreManifest()
        return cls._INSTANCE

    def _load_from_disk(self, category: str) -> Optional[Dict]:
        filename = f"{category.lower()}.json"
        filepath = os.path.join(self.DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"{Prisma.RED}[LORE]: Missing data file for '{category}' at {filepath}{Prisma.RST}")
            return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"{Prisma.GRY}[LORE]: Lazy-loaded '{category}' from disk.{Prisma.RST}")
            return data
        except Exception as e:
            print(f"{Prisma.RED}[LORE]: Corrupt JSON in '{category}': {e}{Prisma.RST}")
            return None

    def get(self, category: str, sub_key: str = None) -> Any:
        if category in self._overlays:
            data = self._overlays[category]
        elif category in self._cache:
            data = self._cache[category]
        else:
            data = self._load_from_disk(category)
            if data is not None:
                self._cache[category] = data
            else:
                data = {}
        if sub_key and isinstance(data, dict):
            return data.get(sub_key, None)
        return data

    def inject(self, category: str, data: Any):
        if category not in self._overlays:
            self._overlays[category] = {}
        if isinstance(self._overlays[category], dict) and isinstance(data, dict):
            self._overlays[category].update(data)
        else:
            self._overlays[category] = data

    def flush_cache(self, category: str = None):
        if category:
            if category in self._cache:
                del self._cache[category]
                print(f"{Prisma.CYN}[LORE]: Flushed cache for '{category}'.{Prisma.RST}")
        else:
            self._cache = {}
            print(f"{Prisma.CYN}[LORE]: Flushed entire Lore cache.{Prisma.RST}")

TheLore = LoreManifest.get_instance()