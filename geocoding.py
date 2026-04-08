import requests
import cache


# Sessione condivisa per riutilizzare le connessioni TCP
_session = requests.Session()


def get_coordinates(city_name: str) -> dict:
    """Converte il nome di una città in coordinate geografiche usando Open-Meteo Geocoding API."""
    cache_key = f"geo:{city_name.lower().strip()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "it"}

    response = _session.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"Città '{city_name}' non trovata.")

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
    """Geocodifica più città. Ritorna lista di risultati e lista di errori."""
    results = []
    errors = []
    for city in city_names:
        try:
            results.append(get_coordinates(city))
        except (ValueError, requests.RequestException) as e:
            errors.append({"city": city, "error": str(e)})
    return results, errors
