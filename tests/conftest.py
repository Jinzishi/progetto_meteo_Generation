import pytest
import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """Pulisce la cache prima di ogni test per evitare interferenze."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def geocoding_success_response():
    """Risposta valida dall'API Geocoding."""
    return {
        "results": [
            {
                "name": "Milano",
                "country": "Italia",
                "latitude": 45.4643,
                "longitude": 9.1895,
            }
        ]
    }


@pytest.fixture
def geocoding_empty_response():
    """Risposta senza risultati dall'API Geocoding."""
    return {}


@pytest.fixture
def weather_success_response():
    """Risposta valida dall'API Weather."""
    return {
        "current": {
            "temperature_2m": 22.5,
            "relative_humidity_2m": 65,
            "apparent_temperature": 21.0,
            "weather_code": 0,
            "wind_speed_10m": 12.3,
            "wind_gusts_10m": 20.1,
            "precipitation": 0.0,
            "surface_pressure": 1013.2,
        },
        "current_units": {
            "temperature_2m": "\u00b0C",
            "relative_humidity_2m": "%",
            "wind_speed_10m": "km/h",
            "wind_gusts_10m": "km/h",
            "precipitation": "mm",
            "surface_pressure": "hPa",
        },
    }


@pytest.fixture
def forecast_success_response():
    """Risposta valida dall'API previsioni giornaliere."""
    return {
        "daily": {
            "time": ["2026-04-08", "2026-04-09", "2026-04-10"],
            "weather_code": [0, 3, 61],
            "temperature_2m_max": [22.5, 18.0, 15.2],
            "temperature_2m_min": [12.0, 10.5, 8.3],
            "apparent_temperature_max": [21.0, 16.5, 13.0],
            "apparent_temperature_min": [10.5, 8.0, 6.0],
            "precipitation_sum": [0.0, 0.0, 5.2],
            "precipitation_probability_max": [0, 10, 80],
            "wind_speed_10m_max": [12.3, 20.5, 30.0],
            "wind_gusts_10m_max": [25.0, 40.2, 55.0],
            "sunrise": ["2026-04-08T06:30", "2026-04-09T06:28", "2026-04-10T06:27"],
            "sunset": ["2026-04-08T19:45", "2026-04-09T19:46", "2026-04-10T19:48"],
        },
        "daily_units": {
            "temperature_2m_max": "\u00b0C",
            "temperature_2m_min": "\u00b0C",
            "apparent_temperature_max": "\u00b0C",
            "apparent_temperature_min": "\u00b0C",
            "precipitation_sum": "mm",
            "precipitation_probability_max": "%",
            "wind_speed_10m_max": "km/h",
            "wind_gusts_10m_max": "km/h",
        },
    }


@pytest.fixture
def city_info():
    """Dati citta' di esempio."""
    return {
        "name": "Milano",
        "country": "Italia",
        "latitude": 45.4643,
        "longitude": 9.1895,
    }


@pytest.fixture
def weather_data():
    """Dati meteo di esempio."""
    return {
        "temperature": 22.5,
        "temperature_unit": "\u00b0C",
        "apparent_temperature": 21.0,
        "humidity": 65,
        "humidity_unit": "%",
        "wind_speed": 12.3,
        "wind_speed_unit": "km/h",
        "wind_gusts": 20.1,
        "precipitation": 0.0,
        "precipitation_unit": "mm",
        "pressure": 1013.2,
        "pressure_unit": "hPa",
        "weather_code": 0,
    }
