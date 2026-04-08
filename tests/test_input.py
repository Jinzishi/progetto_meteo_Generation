"""Test input validation - Sezione 1 della guida."""

from unittest.mock import patch

import pytest

from geocoding import get_coordinates


class TestInputValidation:
    """Verifica che l'app gestisca correttamente gli input."""

    @patch("geocoding._session.get")
    def test_valid_city(self, mock_get, geocoding_success_response):
        """Citta' valida restituisce coordinate."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        result = get_coordinates("Milano")

        assert result["name"] == "Milano"
        assert result["latitude"] == 45.4643
        assert result["longitude"] == 9.1895

    @patch("geocoding._session.get")
    def test_city_with_spaces(self, mock_get):
        """Citta' con spazi (es. 'New York')."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "name": "New York",
                    "country": "United States",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                }
            ]
        }

        result = get_coordinates("New York")

        assert result["name"] == "New York"
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["name"] == "New York"

    @patch("geocoding._session.get")
    def test_city_special_characters(self, mock_get):
        """Citta' con caratteri speciali (es. 'Sao Paulo')."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "name": "S\u00e3o Paulo",
                    "country": "Brazil",
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                }
            ]
        }

        result = get_coordinates("S\u00e3o Paulo")

        assert result["name"] == "S\u00e3o Paulo"

    def test_empty_string_raises_error(self):
        """Stringa vuota: bloccata dalla validazione."""
        with pytest.raises(ValueError, match="vuoto"):
            get_coordinates("")

    def test_only_spaces_raises_error(self):
        """Solo spazi: bloccata dalla validazione."""
        with pytest.raises(ValueError, match="vuoto"):
            get_coordinates("   ")

    @patch("geocoding._session.get")
    def test_numeric_input(self, mock_get):
        """Input numerico: passa validazione, l'API non trova risultati."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {}

        with pytest.raises(ValueError, match="non trovata"):
            get_coordinates("12345")

    def test_too_long_input_rejected(self):
        """Input troppo lungo (>100 char): bloccato dalla validazione."""
        with pytest.raises(ValueError, match="troppo lungo"):
            get_coordinates("A" * 101)

    def test_injection_characters_rejected(self):
        """Caratteri potenzialmente pericolosi bloccati dalla validazione."""
        with pytest.raises(ValueError, match="non validi"):
            get_coordinates("<script>alert(1)</script>")
