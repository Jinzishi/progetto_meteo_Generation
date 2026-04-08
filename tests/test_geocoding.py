"""Test Geocoding Service (Mock API) - Sezione 2 della guida."""

from unittest.mock import patch, Mock

import pytest
import requests

from geocoding import get_coordinates


class TestGeocodingSuccess:
    """Test casi di successo geocoding."""

    @patch("geocoding._session.get")
    def test_returns_correct_coordinates(self, mock_get, geocoding_success_response):
        """Citta' trovata restituisce coordinate corrette."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        result = get_coordinates("Milano")

        assert result["latitude"] == 45.4643
        assert result["longitude"] == 9.1895
        assert result["name"] == "Milano"
        assert result["country"] == "Italia"

    @patch("geocoding._session.get")
    def test_api_called_with_correct_params(self, mock_get, geocoding_success_response):
        """Verifica che l'API venga chiamata con i parametri corretti."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        import config
        get_coordinates("Milano")

        mock_get.assert_called_once_with(
            config.GEOCODING_API_URL,
            params={"name": "Milano", "count": 1, "language": "it"},
            timeout=config.REQUEST_TIMEOUT,
        )

    @patch("geocoding._session.get")
    def test_country_missing_defaults_empty(self, mock_get):
        """Se country manca dalla risposta, default stringa vuota."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "results": [
                {"name": "TestCity", "latitude": 10.0, "longitude": 20.0}
            ]
        }

        result = get_coordinates("TestCity")

        assert result["country"] == ""


class TestGeocodingErrors:
    """Test gestione errori geocoding."""

    @patch("geocoding._session.get")
    def test_city_not_found(self, mock_get):
        """Citta' non trovata solleva ValueError."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {}

        with pytest.raises(ValueError, match="non trovata"):
            get_coordinates("CittaInesistente999")

    @patch("geocoding._session.get")
    def test_empty_results_list(self, mock_get):
        """Lista risultati vuota solleva ValueError."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {"results": []}

        with pytest.raises(ValueError, match="non trovata"):
            get_coordinates("CittaVuota")

    @patch("geocoding._session.get")
    def test_api_timeout(self, mock_get):
        """Timeout API solleva eccezione."""
        mock_get.side_effect = requests.Timeout("Connection timed out")

        with pytest.raises(requests.Timeout):
            get_coordinates("Milano")

    @patch("geocoding._session.get")
    def test_api_connection_error(self, mock_get):
        """Errore di connessione solleva eccezione."""
        mock_get.side_effect = requests.ConnectionError("No connection")

        with pytest.raises(requests.ConnectionError):
            get_coordinates("Milano")

    @patch("geocoding._session.get")
    def test_api_http_500(self, mock_get):
        """Errore HTTP 500 solleva HTTPError."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            get_coordinates("Milano")
