"""
Language / text management for the `mukip` Python package.

This mirrors how MuKiP-Visual manages text: the primary UI-independent texts
(such as the setup-file field tooltips used by the VSCode language server)
come from **MuKiP itself** -- they are baked into the MuKiP jar and are read at
initialization time via
`com.wang_lab.mukip.components.ComponentsLoader.initializeComponents(lang)`.

This module intentionally does **not** bundle its own copy of MuKiP's texts;
it calls into MuKiP (the running JVM) to obtain them, exactly like the Visual
front-end does during its initialization.
"""

import json
import sys
from typing import Dict, Optional

from .jvm_manager import get_class


def _merge(source, target: Dict):
    """Recursively merge a (nested) dict into target, like MuKiP-Visual does."""
    for k, v in source.items():
        if isinstance(v, str):
            target[k] = v
        elif isinstance(v, dict):
            tv = target.get(k)
            if isinstance(tv, dict):
                _merge(v, tv)
            else:
                target[k] = v


class LangManager:
    """
    Manager for texts provided by MuKiP.

    The `data` dict is filled by calling into MuKiP (the jar), which returns the
    content of its bundled `lang/<code>.json` resources. The server (and any
    future consumer) reads texts through `getTooltip` (used for hover help) or
    `__getitem__` (generic key lookup).
    """

    def __init__(self, lang: str = "en_us"):
        self.lang = lang
        self.data: Dict = {}

    def read_language(self, content: str):
        """Parse a MuKiP lang JSON string and merge it into the current data."""
        try:
            data = json.loads(content)
            _merge(data, self.data)
        except Exception:
            # Malformed text should not break the server.
            pass

    def load_from_mukip(self, lang: Optional[str] = None):
        """
        Call into MuKiP to obtain its built-in language texts.

        `initializeComponents(lang)` returns the contents of the `lang/<code>.json`
        resources bundled inside the MuKiP jar. If the jar has no language
        resources (e.g. an outdated build), the call simply yields nothing and
        hover help gracefully degrades instead of failing.
        """
        lang = lang or self.lang
        try:
            loader = get_class("com.wang_lab.mukip.components.ComponentsLoader")
            langs = loader.initializeComponents(lang)
            for text in langs:
                self.read_language(str(text))
        except Exception as e:
            print(f"[mukip.lang] failed to load language from MuKiP: {e}", file=sys.stderr)

    def getTooltip(self, key_path: str) -> Optional[str]:
        """
        Resolve a tooltip for a component field.

        Key path maps to `setup.tooltip.<...>` inside MuKiP's lang data, with the
        same `$k` / `*` wildcard fallbacks used by MuKiP-Visual's LangManager.
        """
        parts = ["setup", "tooltip"] + key_path.split(".")
        current = self.data
        for part in parts:
            if isinstance(current, str):
                return current
            current1 = current.get(part)
            if current1 is None and part.endswith("$k"):
                current1 = current.get("*$k")
            if current1 is None:
                current1 = current.get("*")
            if current1 is None:
                return None
            current = current1
        return str(current)

    def __getitem__(self, item: str) -> str:
        parts = item.split(".")
        current = self.data
        try:
            for part in parts:
                if isinstance(current, str):
                    return current
                current1 = current.get(part)
                if current1 is None:
                    current1 = current.get("*")
                if current1 is None:
                    raise KeyError
                current = current1
            return str(current)
        except (KeyError, TypeError):
            return f"[{item}]"


# A module-level singleton, preloaded from MuKiP.
lang = LangManager()
