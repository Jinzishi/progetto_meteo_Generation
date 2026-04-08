"""Test Edge Cases (Sezione 7 della guida).

Casi limite: lowercase/uppercase, citta' duplicata, input lungo,
emoji, encoding UTF-8, weather code sconosciuto.
"""

from unittest.mock import patch

import pytest

from geocoding import get_coordinates
from display import display_weather, display_forecast, WEATHER_DESCRIPTIONS, WEATHER_ICONS


class TestGeocodingEdgeCases:
    """Edge cases per geocoding."""

    @patch("geocoding._session.get")
    def test_lowercase_city(self, mock_get, geocoding_success_response):
        """Citta' in minuscolo viene inviata all'API."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        result = get_coordinates("milano")

        args, kwargs = mock_get.call_args
        assert kwargs["params"]["name"] == "milano"
        assert result["name"] == "Milano"

    @patch("geocoding._session.get")
    def test_uppercase_city(self, mock_get, geocoding_success_response):
        """Citta' in maiuscolo viene inviata all'API."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        result = get_coordinates("MILANO")

        args, kwargs = mock_get.call_args
        assert kwargs["params"]["name"] == "MILANO"

    @patch("geocoding._session.get")
    def test_very_long_input(self, mock_get):
        """Input molto lungo non causa crash."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {}

        with pytest.raises(ValueError, match="non trovata"):
            get_coordinates("A" * 1000)

    @patch("geocoding._session.get")
    def test_emoji_input(self, mock_get):
        """Input con emoji non causa crash."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {}

        with pytest.raises(ValueError, match="non trovata"):
            get_coordinates("\U0001f327\ufe0f")

    @patch("geocoding._session.get")
    def test_utf8_characters(self, mock_get):
        """Caratteri internazionali UTF-8 gestiti correttamente."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "name": "Z\u00fcrich",
                    "country": "Switzerland",
                    "latitude": 47.3769,
                    "longitude": 8.5417,
                }
            ]
        }

        result = get_coordinates("Z\u00fcrich")

        assert result["name"] == "Z\u00fcrich"

    @patch("geocoding._session.get")
    @pytest.mark.parametrize("city", ["Milano", "Roma", "Paris", "London", "Tokyo"])
    def test_multiple_cities(self, mock_get, city):
        """Test parametrizzato su piu' citta'."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "name": city,
                    "country": "Test",
                    "latitude": 40.0,
                    "longitude": 10.0,
                }
            ]
        }

        result = get_coordinates(city)

        assert result["name"] == city


class TestDisplayEdgeCases:
    """Edge cases per la visualizzazione."""

    def test_unknown_weather_code(self, city_info, capsys):
        """Weather code sconosciuto mostra 'Sconosciuto'."""
        weather_data = {
            "temperature": 15.0,
            "temperature_unit": "\u00b0C",
            "apparent_temperature": 14.0,
            "humidity": 50,
            "humidity_unit": "%",
            "wind_speed": 5.0,
            "wind_speed_unit": "km/h",
            "weather_code": 999,
        }

        display_weather(city_info, weather_data)

        output = capsys.readouterr().out
        assert "Sconosciuto" in output

    def test_all_weather_codes_have_description(self):
        """Ogni weather code ha una descrizione associata."""
        for code in WEATHER_ICONS:
            assert code in WEATHER_DESCRIPTIONS, f"Code {code} manca in WEATHER_DESCRIPTIONS"

    def test_all_weather_codes_have_icon(self):
        """Ogni weather code ha un'icona associata."""
        for code in WEATHER_DESCRIPTIONS:
            assert code in WEATHER_ICONS, f"Code {code} manca in WEATHER_ICONS"

    def test_display_long_city_name(self, capsys):
        """Citta' con nome lungo non rompe il layout."""
        long_city = {
            "name": "Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch",
            "country": "UK",
        }
        weather_data = {
            "temperature": 10.0,
            "temperature_unit": "\u00b0C",
            "apparent_temperature": 8.0,
            "humidity": 70,
            "humidity_unit": "%",
            "wind_speed": 20.0,
            "wind_speed_unit": "km/h",
            "weather_code": 3,
        }

        display_weather(long_city, weather_data)

        output = capsys.readouterr().out
        assert "Llanfair" in output

    def test_display_with_extra_fields(self, city_info, weather_data, capsys):
        """Display mostra raffiche, precipitazioni e pressione se presenti."""
        weather_data["wind_gusts"] = 35.0
        weather_data["precipitation"] = 2.5
        weather_data["precipitation_unit"] = "mm"
        weather_data["pressure"] = 1015.0
        weather_data["pressure_unit"] = "hPa"

        display_weather(city_info, weather_data)

        output = capsys.readouterr().out
        assert "35.0" in output
        assert "2.5" in output
        assert "1015.0" in output

    def test_display_forecast(self, city_info, capsys):
        """Forecast visualizza tutti i giorni con dettagli."""
        forecast = [
            {
                "date": "2026-04-08",
                "weather_code": 0,
                "temp_max": 22.0,
                "temp_min": 12.0,
                "temp_unit": "\u00b0C",
                "feels_max": 20.0,
                "feels_min": 10.0,
                "precipitation": 0.0,
                "precipitation_unit": "mm",
                "precipitation_prob": 5,
                "wind_max": 15.0,
                "wind_unit": "km/h",
                "wind_gusts_max": 30.0,
                "sunrise": "2026-04-08T06:30",
                "sunset": "2026-04-08T19:45",
            },
        ]

        display_forecast(city_info, forecast)

        output = capsys.readouterr().out
        assert "Previsioni 1 giorni" in output
        assert "08/04" in output
        assert "22.0" in output
        assert "12.0" in output
        assert "06:30" in output
        assert "19:45" in output
        assert "Sereno" in output
