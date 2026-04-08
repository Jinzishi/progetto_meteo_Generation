import json
import time
import os

_DEFAULT_TTL = 3600  # 1 ora in secondi
_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache.json")

# Cache in memoria: { chiave: { "data": ..., "timestamp": ... } }
_memory_cache = {}


def _load_from_disk():
    """Carica la cache da file se esiste."""
    global _memory_cache
    if _memory_cache:
        return
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            _memory_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _memory_cache = {}


def _save_to_disk():
    """Salva la cache su file per persistenza offline."""
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_memory_cache, f, ensure_ascii=False)
    except OSError:
        pass


def get(key: str) -> dict | None:
    """Recupera un valore dalla cache se esiste e non e' scaduto."""
    _load_from_disk()
    entry = _memory_cache.get(key)
    if entry is None:
        return None
    if time.time() - entry["timestamp"] > _DEFAULT_TTL:
        del _memory_cache[key]
        _save_to_disk()
        return None
    return entry["data"]


def set(key: str, data: dict):
    """Salva un valore in cache con timestamp corrente."""
    _load_from_disk()
    _memory_cache[key] = {
        "data": data,
        "timestamp": time.time(),
    }
    _save_to_disk()


def clear():
    """Svuota tutta la cache."""
    global _memory_cache
    _memory_cache = {}
    try:
        os.remove(_CACHE_FILE)
    except FileNotFoundError:
        pass
