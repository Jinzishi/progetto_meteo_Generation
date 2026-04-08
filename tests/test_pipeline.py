"""Test Business Logic - Pipeline completa (Sezione 4 della guida).

Testa il flusso: city -> geocode -> weather -> display
Mocka solo le API esterne.
"""

from unittest.mock import patch, Mock

import pytest
import requests as req

from geocoding import get_coordinates
from weather import get_weather, get_forecast
from display import display_weather, display_forecast


def _make_mock_response(json_data):
    """Crea un mock response con json() e raise_for_status()."""
    mock = Mock()
    mock.raise_for_status = lambda: None
    mock.json.return_value = json_data
    return mock


class TestPipelineSuccess:
    """Test flusso completo corretto."""

    @patch("weather._session.get")
    @patch("geocoding._session.get")
    def test_full_flow(
        self,
        mock_geo_get,
        mock_weather_get,
        geocoding_success_response,
        weather_success_response,
        capsys,
    ):
        """Pipeline completa: city -> coordinate -> meteo -> display."""
        mock_geo_get.return_value = _make_mock_response(geocoding_success_response)
        mock_weather_get.return_value = _make_mock_response(weather_success_response)

        city_info = get_coordinates("Milano")
        weather_data = get_weather(city_info["latitude"], city_info["longitude"])
        display_weather(city_info, weather_data)

        output = capsys.readouterr().out
        assert "Milano" in output
        assert "22.5" in output
        assert "Sereno" in output


    @patch("weather._session.get")
    @patch("geocoding._session.get")
    def test_full_flow_with_forecast(
        self,
        mock_geo_get,
        mock_weather_get,
        geocoding_success_response,
        weather_success_response,
        forecast_success_response,
        capsys,
    ):
        """Pipeline con previsioni: city -> meteo corrente + forecast."""
        mock_geo_get.return_value = _make_mock_response(geocoding_success_response)
        # Prima chiamata: meteo corrente, seconda: forecast
        mock_weather_get.side_effect = [
            _make_mock_response(weather_success_response),
            _make_mock_response(forecast_success_response),
        ]

        city_info = get_coordinates("Milano")
        weather_data = get_weather(city_info["latitude"], city_info["longitude"])
        display_weather(city_info, weather_data)

        forecast = get_forecast(city_info["latitude"], city_info["longitude"], 3)
        display_forecast(city_info, forecast)

        output = capsys.readouterr().out
        assert "Milano" in output
        assert "Previsioni 3 giorni" in output
        assert "08/04" in output


class TestPipelineFailures:
    """Test fallimenti nella pipeline."""

    @patch("geocoding._session.get")
    def test_geocoding_fails_stops_pipeline(self, mock_get):
        """Se geocoding fallisce, la pipeline si ferma."""
        mock_get.return_value = _make_mock_response({})

        with pytest.raises(ValueError):
            get_coordinates("CittaInesistente")

    @patch("weather._session.get")
    @patch("geocoding._session.get")
    def test_weather_fails_after_geocoding(
        self, mock_geo_get, mock_weather_get, geocoding_success_response
    ):
        """Se weather fallisce dopo geocoding riuscito, eccezione propagata."""
        mock_geo_get.return_value = _make_mock_response(geocoding_success_response)
        mock_weather_get.side_effect = req.Timeout("Timeout")

        city_info = get_coordinates("Milano")

        with pytest.raises(req.Timeout):
            get_weather(city_info["latitude"], city_info["longitude"])
