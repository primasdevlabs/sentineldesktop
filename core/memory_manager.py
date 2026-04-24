"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/memory_manager.py
Description: Persistence layer for Sentinel.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import json
import os
import logging
import random
from typing import Dict, Any, Optional

class MemoryManager:
    def __init__(self, storage_path: str = "sentinel/data/memory.json") -> None:
        self.storage_path = storage_path
        self.memory: Dict[str, Any] = self._load_from_disk()
        self.logger = logging.getLogger("MemoryManager")

    def _load_from_disk(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_structure()
        return self._get_default_structure()

    def _get_default_structure(self) -> Dict[str, Any]:
        return {
            "user_name": None,
            "preferences": {"voice_style": "professional", "timezone": "auto"},
            "facts": {}
        }

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.memory.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.memory[key] = value
        self.save()

    def personalize_text(self, text: str) -> str:
        name = self.get("user_name")
        if not name: return text
        if name.lower() not in text.lower() and random.random() < 0.3:
            return f"{name}, " + text
        return text
