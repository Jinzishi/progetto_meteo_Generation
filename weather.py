import requests

import cache
import config


# Sessione condivisa per riutilizzare le connessioni TCP
_session = requests.Session()

# Campi meteo correnti (inclusi precipitazioni e pressione)
_CURRENT_FIELDS = (
    "temperature_2m,apparent_temperature,weather_code,"
    "wind_speed_10m,wind_gusts_10m,relative_humidity_2m,"
    "precipitation,surface_pressure"
)

# Campi previsione giornaliera
_DAILY_FIELDS = (
    "weather_code,temperature_2m_max,temperature_2m_min,"
    "apparent_temperature_max,apparent_temperature_min,"
    "precipitation_sum,precipitation_probability_max,"
    "wind_speed_10m_max,wind_gusts_10m_max,"
    "sunrise,sunset"
)


def _parse_weather(current: dict, units: dict) -> dict:
    """Estrae i dati meteo rilevanti dalla risposta API."""
    return {
        "temperature": current["temperature_2m"],
        "temperature_unit": units["temperature_2m"],
        "apparent_temperature": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "humidity_unit": units["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "wind_speed_unit": units["wind_speed_10m"],
        "wind_gusts": current.get("wind_gusts_10m", 0),
        "precipitation": current.get("precipitation", 0),
        "precipitation_unit": units.get("precipitation", "mm"),
        "pressure": current.get("surface_pressure", 0),
        "pressure_unit": units.get("surface_pressure", "hPa"),
        "weather_code": current["weather_code"],
    }


def _parse_forecast(daily: dict, units: dict) -> list[dict]:
    """Estrae le previsioni giornaliere dalla risposta API."""
    days = []
    for i in range(len(daily["time"])):
        days.append({
            "date": daily["time"][i],
            "weather_code": daily["weather_code"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "temp_unit": units["temperature_2m_max"],
            "feels_max": daily["apparent_temperature_max"][i],
            "feels_min": daily["apparent_temperature_min"][i],
            "precipitation": daily["precipitation_sum"][i],
            "precipitation_unit": units["precipitation_sum"],
            "precipitation_prob": daily["precipitation_probability_max"][i],
            "wind_max": daily["wind_speed_10m_max"][i],
            "wind_unit": units["wind_speed_10m_max"],
            "wind_gusts_max": daily["wind_gusts_10m_max"][i],
            "sunrise": daily["sunrise"][i],
            "sunset": daily["sunset"][i],
        })
    return days


def get_weather(latitude: float, longitude: float) -> dict:
    """Recupera i dati meteo correnti per una singola posizione."""
    cache_key = f"weather:{latitude:.4f},{longitude:.4f}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": _CURRENT_FIELDS,
        "timezone": "auto",
    }
    if config.API_KEY:
        params["apikey"] = config.API_KEY

    response = _session.get(
        config.WEATHER_API_URL, params=params, timeout=config.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    result = _parse_weather(data["current"], data["current_units"])
    cache.set(cache_key, result)
    return result


def get_forecast(latitude: float, longitude: float, days: int = 5) -> list[dict]:
    """Recupera le previsioni giornaliere per i prossimi N giorni (3-5)."""
    days = max(3, min(days, 5))
    cache_key = f"forecast:{latitude:.4f},{longitude:.4f}:{days}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": _DAILY_FIELDS,
        "forecast_days": days,
        "timezone": "auto",
    }
    if config.API_KEY:
        params["apikey"] = config.API_KEY

    response = _session.get(
        config.WEATHER_API_URL, params=params, timeout=config.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    result = _parse_forecast(data["daily"], data["daily_units"])
    cache.set(cache_key, result)
    return result


def get_weather_multi(cities: list[dict]) -> list[dict]:
    """Recupera i dati meteo per piu' citta' in una singola richiesta API."""
    if not cities:
        return []

    if len(cities) == 1:
        return [get_weather(cities[0]["latitude"], cities[0]["longitude"])]

    params = {
        "latitude": ",".join(str(c["latitude"]) for c in cities),
        "longitude": ",".join(str(c["longitude"]) for c in cities),
        "current": _CURRENT_FIELDS,
        "timezone": "auto",
    }
    if config.API_KEY:
        params["apikey"] = config.API_KEY

    response = _session.get(
        config.WEATHER_API_URL, params=params, timeout=config.REQUEST_TIMEOUT + 5
    )
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data:
        results.append(_parse_weather(item["current"], item["current_units"]))
    return results
