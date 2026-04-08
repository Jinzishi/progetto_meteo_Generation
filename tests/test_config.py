"""Test configurazione tramite variabili d'ambiente."""

import os
import importlib
from unittest.mock import patch

import pytest

import config


class TestConfigDefaults:
    """Verifica valori default senza variabili d'ambiente."""

    def test_default_geocoding_url(self):
        assert "geocoding-api.open-meteo.com" in config.GEOCODING_API_URL

    def test_default_weather_url(self):
        assert "api.open-meteo.com" in config.WEATHER_API_URL

    def test_default_api_key_empty(self):
        assert config.API_KEY == ""

    def test_default_timeout(self):
        assert config.REQUEST_TIMEOUT == 10

    def test_default_cache_ttl(self):
        assert config.CACHE_TTL == 3600

    def test_default_max_cities(self):
        assert config.MAX_CITIES == 10

    def test_default_cache_disk_enabled(self):
        assert config.CACHE_DISK_ENABLED is True


class TestConfigOverride:
    """Verifica override tramite variabili d'ambiente.

    Usa patch.dict + reload per testare la lettura da env,
    poi ripristina DOPO che il patch e' uscito.
    """

    def test_override_timeout(self):
        """Timeout puo' essere sovrascritto via env var."""
        with patch.dict(os.environ, {"METEO_REQUEST_TIMEOUT": "30"}):
            importlib.reload(config)
            assert config.REQUEST_TIMEOUT == 30
        importlib.reload(config)
        assert config.REQUEST_TIMEOUT == 10

    def test_override_api_key(self):
        """API key puo' essere impostata via env var."""
        with patch.dict(os.environ, {"METEO_API_KEY": "test-key-123"}):
            importlib.reload(config)
            assert config.API_KEY == "test-key-123"
        importlib.reload(config)
        assert config.API_KEY == ""

    def test_disable_cache_disk(self):
        """Cache disco puo' essere disabilitata."""
        with patch.dict(os.environ, {"METEO_CACHE_DISK": "false"}):
            importlib.reload(config)
            assert config.CACHE_DISK_ENABLED is False
        importlib.reload(config)
        assert config.CACHE_DISK_ENABLED is True
