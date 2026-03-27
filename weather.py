import requests


def get_weather(latitude: float, longitude: float) -> dict:
    """Recupera i dati meteo correnti da Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data["current"]
    units = data["current_units"]

    return {
        "temperature": current["temperature_2m"],
        "temperature_unit": units["temperature_2m"],
        "apparent_temperature": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "humidity_unit": units["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "wind_speed_unit": units["wind_speed_10m"],
        "weather_code": current["weather_code"],
    }
