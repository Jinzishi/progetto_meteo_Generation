import re

import requests

import cache
import config


# Sessione condivisa per riutilizzare le connessioni TCP
_session = requests.Session()

# Pattern per validazione input: solo lettere, spazi, trattini, apostrofi, punti
_VALID_CITY_RE = re.compile(r"^[\w\s\-'.À-ÿ]+$", re.UNICODE)


def _sanitize_city(name: str) -> str:
    """Valida e sanitizza il nome della citta'."""
    name = name.strip()
    if not name:
        raise ValueError("Il nome della citta' non puo' essere vuoto.")
    if len(name) > 100:
        raise ValueError("Il nome della citta' e' troppo lungo (max 100 caratteri).")
    if not _VALID_CITY_RE.match(name):
        raise ValueError(f"Il nome '{name}' contiene caratteri non validi.")
    return name


def get_coordinates(city_name: str) -> dict:
    """Converte il nome di una citta' in coordinate geografiche usando Open-Meteo Geocoding API."""
    city_name = _sanitize_city(city_name)

    cache_key = f"geo:{city_name.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    params = {"name": city_name, "count": 1, "language": "it"}
    if config.API_KEY:
        params["apikey"] = config.API_KEY

    response = _session.get(
        config.GEOCODING_API_URL, params=params, timeout=config.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"Citta' '{city_name}' non trovata.")

    result = data["results"][0]
    coords = {
        "name": result["name"],
        "country": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
    }
    cache.set(cache_key, coords)
    return coords


def get_coordinates_multi(city_names: list[str]) -> list[dict]:
    """Geocodifica piu' citta'. Ritorna lista di risultati e lista di errori."""
    results = []
    errors = []
    for city in city_names[:config.MAX_CITIES]:
        try:
            results.append(get_coordinates(city))
        except (ValueError, requests.RequestException) as e:
            errors.append({"city": city, "error": str(e)})
    return results, errors
