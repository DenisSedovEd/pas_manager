"""Единая точка правды для значений, общих с фронтендом.

Читает representations/shared/src/config.json — тот же файл, который
импортируют web и Telegram mini app через @pas/shared.
"""

import json
from pathlib import Path

_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "representations"
    / "shared"
    / "src"
    / "config.json"
)

with _CONFIG_PATH.open(encoding="utf-8") as f:
    _raw = json.load(f)

PASSWORD_LENGTH: int = _raw["password"]["length"]
PASSWORD_SPECIAL_CHARS: str = _raw["password"]["specialChars"]
PASSWORD_EXCLUDED_CHARS: str = _raw["password"]["excludedChars"]

ICON_MAX_BYTES: int = _raw["icon"]["maxBytes"]
ICON_FALLBACK_EMOJI: str = _raw["icon"]["fallbackEmoji"]
