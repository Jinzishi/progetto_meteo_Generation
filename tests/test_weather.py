"""Test Weather Fetching (Mock API) - Sezione 3 della guida."""

from unittest.mock import patch, Mock

import pytest
import requests

from weather import get_weather, get_forecast


class TestWeatherSuccess:
    """Test casi di successo weather API."""

    @patch("weather._session.get")
    def test_returns_correct_data(self, mock_get, weather_success_response):
        """Risposta valida restituisce dati meteo corretti."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = weather_success_response

        result = get_weather(45.4643, 9.1895)

        assert result["temperature"] == 22.5
        assert result["temperature_unit"] == "\u00b0C"
        assert result["apparent_temperature"] == 21.0
        assert result["humidity"] == 65
        assert result["humidity_unit"] == "%"
        assert result["wind_speed"] == 12.3
        assert result["wind_speed_unit"] == "km/h"
        assert result["wind_gusts"] == 20.1
        assert result["precipitation"] == 0.0
        assert result["pressure"] == 1013.2
        assert result["weather_code"] == 0

    @patch("weather._session.get")
    def test_negative_temperature(self, mock_get):
        """Temperature negative gestite correttamente."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "current": {
                "temperature_2m": -5.0,
                "relative_humidity_2m": 80,
                "apparent_temperature": -9.0,
                "weather_code": 71,
                "wind_speed_10m": 25.0,
                "wind_gusts_10m": 40.0,
                "precipitation": 2.5,
                "surface_pressure": 1020.0,
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

        result = get_weather(60.0, 10.0)

        assert result["temperature"] == -5.0
        assert result["apparent_temperature"] == -9.0
        assert result["precipitation"] == 2.5


class TestForecast:
    """Test previsioni giornaliere."""

    @patch("weather._session.get")
    def test_returns_correct_days(self, mock_get, forecast_success_response):
        """Previsione a 3 giorni restituisce 3 elementi."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = forecast_success_response

        result = get_forecast(45.4643, 9.1895, days=3)

        assert len(result) == 3
        assert result[0]["date"] == "2026-04-08"
        assert result[0]["temp_max"] == 22.5
        assert result[0]["temp_min"] == 12.0
        assert result[0]["precipitation"] == 0.0
        assert result[0]["precipitation_prob"] == 0

    @patch("weather._session.get")
    def test_forecast_all_fields_present(self, mock_get, forecast_success_response):
        """Ogni giorno ha tutti i campi necessari."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = forecast_success_response

        result = get_forecast(45.4643, 9.1895, days=3)

        expected_keys = {
            "date", "weather_code", "temp_max", "temp_min", "temp_unit",
            "feels_max", "feels_min", "precipitation", "precipitation_unit",
            "precipitation_prob", "wind_max", "wind_unit", "wind_gusts_max",
            "sunrise", "sunset",
        }
        for day in result:
            assert set(day.keys()) == expected_keys

    @patch("weather._session.get")
    def test_forecast_rainy_day(self, mock_get, forecast_success_response):
        """Giorno di pioggia ha dati precipitazioni corretti."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = forecast_success_response

        result = get_forecast(45.4643, 9.1895, days=3)

        rainy = result[2]  # terzo giorno: pioggia
        assert rainy["weather_code"] == 61
        assert rainy["precipitation"] == 5.2
        assert rainy["precipitation_prob"] == 80

    @patch("weather._session.get")
    def test_forecast_days_clamped(self, mock_get, forecast_success_response):
        """Giorni vengono limitati tra 3 e 5."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = forecast_success_response

        get_forecast(45.0, 9.0, days=1)
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["forecast_days"] == 3

    @patch("weather._session.get")
    def test_forecast_timeout(self, mock_get):
        """Timeout sulle previsioni solleva eccezione."""
        mock_get.side_effect = requests.Timeout("Timeout")

        with pytest.raises(requests.Timeout):
            get_forecast(45.0, 9.0)

    @patch("weather._session.get")
    def test_forecast_uses_cache(self, mock_get, forecast_success_response):
        """Seconda chiamata previsioni usa la cache."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = forecast_success_response

        get_forecast(45.4643, 9.1895, days=3)
        get_forecast(45.4643, 9.1895, days=3)
        assert mock_get.call_count == 1


class TestWeatherErrors:
    """Test gestione errori weather API."""

    @patch("weather._session.get")
    def test_api_timeout(self, mock_get):
        """Timeout API solleva eccezione."""
        mock_get.side_effect = requests.Timeout("Connection timed out")

        with pytest.raises(requests.Timeout):
            get_weather(45.0, 9.0)

    @patch("weather._session.get")
    def test_api_http_500(self, mock_get):
        """Errore HTTP 500 solleva HTTPError."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            get_weather(45.0, 9.0)

    @patch("weather._session.get")
    def test_missing_current_key(self, mock_get):
        """Risposta senza 'current' solleva KeyError."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {"daily": {}}

        with pytest.raises(KeyError):
            get_weather(45.0, 9.0)

    @patch("weather._session.get")
    def test_missing_field_in_current(self, mock_get):
        """Campo mancante in 'current' solleva KeyError."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "current": {"temperature_2m": 20.0},
            "current_units": {"temperature_2m": "\u00b0C"},
        }

        with pytest.raises(KeyError):
            get_weather(45.0, 9.0)
