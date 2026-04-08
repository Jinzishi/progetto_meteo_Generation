import json
import time
import os
import stat

import config

_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache.json")

# Cache in memoria: { chiave: { "data": ..., "timestamp": ... } }
_memory_cache = {}

# Consenso utente per la persistenza su disco
_disk_consent_given = False


def set_disk_consent(consent: bool):
    """Registra il consenso dell'utente per il salvataggio su disco."""
    global _disk_consent_given
    _disk_consent_given = consent


def _disk_allowed():
    """Verifica se la scrittura su disco e' permessa."""
    return config.CACHE_DISK_ENABLED and _disk_consent_given


def _load_from_disk():
    """Carica la cache da file se esiste."""
    global _memory_cache
    if _memory_cache:
        return
    if not _disk_allowed():
        return
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            _memory_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _memory_cache = {}


def _save_to_disk():
    """Salva la cache su file con permessi restrittivi (solo owner)."""
    if not _disk_allowed():
        return
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_memory_cache, f, ensure_ascii=False)
        # Permessi solo per il proprietario (rw-------)
        os.chmod(_CACHE_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def get(key: str) -> dict | None:
    """Recupera un valore dalla cache se esiste e non e' scaduto."""
    _load_from_disk()
    entry = _memory_cache.get(key)
    if entry is None:
        return None
    if time.time() - entry["timestamp"] > config.CACHE_TTL:
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
    """Svuota tutta la cache (memoria e disco)."""
    global _memory_cache
    _memory_cache = {}
    try:
        os.remove(_CACHE_FILE)
    except FileNotFoundError:
        pass
