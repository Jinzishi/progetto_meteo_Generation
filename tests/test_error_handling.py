"""Test Error Handling (Sezione 6 della guida).

Testa che l'app non crashi, ritorni messaggi chiari,
e gestisca eccezioni esterne.
"""

from unittest.mock import patch, Mock
from io import StringIO

import pytest
import requests

from geocoding import get_coordinates
from weather import get_weather


class TestGeocodingErrorHandling:
    """L'app gestisce errori geocoding senza crash."""

    @patch("geocoding._session.get")
    def test_timeout_raises_not_crashes(self, mock_get):
        """Timeout non causa crash, solleva eccezione gestibile."""
        mock_get.side_effect = requests.Timeout("Read timed out")

        with pytest.raises(requests.Timeout):
            get_coordinates("Milano")

    @patch("geocoding._session.get")
    def test_connection_error_raises_not_crashes(self, mock_get):
        """Errore di rete non causa crash."""
        mock_get.side_effect = requests.ConnectionError("DNS resolution failed")

        with pytest.raises(requests.ConnectionError):
            get_coordinates("Milano")

    @patch("geocoding._session.get")
    def test_invalid_json_raises_not_crashes(self, mock_get):
        """JSON invalido non causa crash."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

        with pytest.raises(ValueError):
            get_coordinates("Milano")

    @patch("geocoding._session.get")
    def test_http_403_forbidden(self, mock_get):
        """Rate limit o accesso negato gestito correttamente."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            get_coordinates("Milano")


class TestWeatherErrorHandling:
    """L'app gestisce errori weather API senza crash."""

    @patch("weather._session.get")
    def test_timeout_raises_not_crashes(self, mock_get):
        """Timeout weather non causa crash."""
        mock_get.side_effect = requests.Timeout("Read timed out")

        with pytest.raises(requests.Timeout):
            get_weather(45.0, 9.0)

    @patch("weather._session.get")
    def test_malformed_response(self, mock_get):
        """Risposta malformata solleva errore chiaro."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {"unexpected": "format"}

        with pytest.raises(KeyError):
            get_weather(45.0, 9.0)


class TestMainErrorHandling:
    """Il main cattura tutte le eccezioni e mostra messaggi chiari."""

    @patch("builtins.input", return_value="Milano")
    @patch("geocoding._session.get")
    def test_main_catches_timeout(self, mock_get, mock_input):
        """main() cattura il timeout senza crash."""
        mock_get.side_effect = requests.Timeout("Timeout")

        from main import main
        # Verifica che main() non sollevi eccezioni (le cattura internamente)
        main()  # non deve fare raise

    @patch("builtins.input", return_value="")
    def test_main_handles_empty_input(self, mock_input, capsys):
        """main() gestisce input vuoto con messaggio chiaro."""
        from main import main
        main()

        output = capsys.readouterr().out
        assert "nessuna citt" in output.lower()

    @patch("builtins.input", return_value="CittaInesistente999")
    @patch("geocoding._session.get")
    def test_main_catches_city_not_found(self, mock_get, mock_input, capsys):
        """main() cattura ValueError per citta' non trovata."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {}

        from main import main
        main()

        output = capsys.readouterr().out
        assert "Errore" in output
