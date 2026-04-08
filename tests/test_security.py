"""Test sicurezza: API key, limiti batch, permessi file, consenso utente."""

import os
import stat
from unittest.mock import patch, Mock

import pytest

import cache
import config
from geocoding import get_coordinates, get_coordinates_multi
from weather import get_weather


class TestApiKeyInjection:
    """Verifica che l'API key venga passata quando configurata."""

    @patch("geocoding._session.get")
    @patch.object(config, "API_KEY", "my-secret-key")
    def test_geocoding_sends_api_key(self, mock_get, geocoding_success_response):
        """Geocoding include apikey nei parametri se configurata."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        get_coordinates("Milano")

        _, kwargs = mock_get.call_args
        assert kwargs["params"]["apikey"] == "my-secret-key"

    @patch("geocoding._session.get")
    @patch.object(config, "API_KEY", "")
    def test_geocoding_no_key_when_empty(self, mock_get, geocoding_success_response):
        """Geocoding non include apikey se vuota."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        get_coordinates("Milano")

        _, kwargs = mock_get.call_args
        assert "apikey" not in kwargs["params"]

    @patch("weather._session.get")
    @patch.object(config, "API_KEY", "weather-key")
    def test_weather_sends_api_key(self, mock_get, weather_success_response):
        """Weather include apikey nei parametri se configurata."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = weather_success_response

        get_weather(45.0, 9.0)

        _, kwargs = mock_get.call_args
        assert kwargs["params"]["apikey"] == "weather-key"


class TestMaxCitiesLimit:
    """Verifica il limite massimo di citta' per batch."""

    @patch("geocoding._session.get")
    @patch.object(config, "MAX_CITIES", 3)
    def test_multi_truncates_to_max(self, mock_get):
        """get_coordinates_multi tronca alla soglia MAX_CITIES."""
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "results": [{"name": "X", "country": "Y", "latitude": 1.0, "longitude": 2.0}]
        }

        cities = ["A", "B", "C", "D", "E"]
        results, errors = get_coordinates_multi(cities)

        # Solo 3 chiamate (MAX_CITIES=3), non 5
        assert mock_get.call_count == 3


class TestCacheFilePermissions:
    """Verifica permessi restrittivi sul file cache."""

    def test_cache_file_owner_only(self):
        """File cache creato con permessi solo per il proprietario."""
        cache.set_disk_consent(True)
        cache.set("perm_test", {"data": 1})

        assert os.path.exists(cache._CACHE_FILE)

        file_stat = os.stat(cache._CACHE_FILE)
        # Su Windows os.chmod e' limitato, ma verifichiamo che il file esista
        # Su Unix verifichiamo i permessi restrittivi
        if os.name != "nt":
            mode = stat.S_IMODE(file_stat.st_mode)
            assert mode == (stat.S_IRUSR | stat.S_IWUSR)

        cache.set_disk_consent(False)


class TestCacheDiskConfig:
    """Verifica che CACHE_DISK_ENABLED=false impedisca la scrittura."""

    @patch.object(config, "CACHE_DISK_ENABLED", False)
    def test_disk_disabled_via_config(self):
        """Con CACHE_DISK_ENABLED=false, nessun file scritto anche con consenso."""
        cache.set_disk_consent(True)
        cache.set("disabled_test", {"data": 1})

        assert not os.path.exists(cache._CACHE_FILE)
        cache.set_disk_consent(False)


class TestMainConsent:
    """Verifica il flusso consenso nel main."""

    @patch("builtins.input", side_effect=["s", "Milano", "1"])
    @patch("geocoding._session.get")
    @patch("weather._session.get")
    def test_consent_yes_enables_disk(
        self, mock_weather, mock_geo, mock_input,
        geocoding_success_response, weather_success_response
    ):
        """Consenso 's' abilita la cache su disco."""
        mock_geo.return_value.raise_for_status = lambda: None
        mock_geo.return_value.json.return_value = geocoding_success_response
        mock_weather.return_value.raise_for_status = lambda: None
        mock_weather.return_value.json.return_value = weather_success_response

        from main import main
        main()

        assert cache._disk_consent_given is True

    @patch("builtins.input", side_effect=["n", "Roma", "1"])
    @patch("geocoding._session.get")
    @patch("weather._session.get")
    def test_consent_no_disables_disk(
        self, mock_weather, mock_geo, mock_input,
        geocoding_success_response, weather_success_response
    ):
        """Consenso 'n' disabilita la cache su disco."""
        mock_geo.return_value.raise_for_status = lambda: None
        mock_geo.return_value.json.return_value = geocoding_success_response
        mock_weather.return_value.raise_for_status = lambda: None
        mock_weather.return_value.json.return_value = weather_success_response

        from main import main
        main()

        assert cache._disk_consent_given is False
        assert not os.path.exists(cache._CACHE_FILE)
