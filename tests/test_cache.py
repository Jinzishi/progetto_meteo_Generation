"""Test Cache con scadenza temporale (TTL 1 ora)."""

import time
from unittest.mock import patch

import pytest

import cache


@pytest.fixture(autouse=True)
def clean_cache():
    """Pulisce la cache prima e dopo ogni test."""
    cache.clear()
    yield
    cache.clear()


class TestCacheBasic:
    """Test operazioni base della cache."""

    def test_set_and_get(self):
        """Salvare e recuperare un valore."""
        cache.set("test_key", {"value": 42})
        result = cache.get("test_key")
        assert result == {"value": 42}

    def test_get_missing_key(self):
        """Chiave inesistente ritorna None."""
        result = cache.get("nonexistent")
        assert result is None

    def test_overwrite_existing_key(self):
        """Sovrascrivere un valore esistente."""
        cache.set("key", {"v": 1})
        cache.set("key", {"v": 2})
        assert cache.get("key") == {"v": 2}

    def test_clear_removes_all(self):
        """Clear svuota tutta la cache."""
        cache.set("a", {"v": 1})
        cache.set("b", {"v": 2})
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None


class TestCacheExpiry:
    """Test scadenza temporale (TTL)."""

    @patch("cache.time")
    def test_valid_within_ttl(self, mock_time):
        """Dati validi entro 1 ora vengono restituiti."""
        mock_time.time.return_value = 1000.0
        cache.set("city", {"temp": 20})

        # 30 minuti dopo
        mock_time.time.return_value = 2800.0
        assert cache.get("city") == {"temp": 20}

    @patch("cache.time")
    def test_expired_after_ttl(self, mock_time):
        """Dati scaduti dopo 1 ora vengono rimossi."""
        mock_time.time.return_value = 1000.0
        cache.set("city", {"temp": 20})

        # 61 minuti dopo (3660 secondi)
        mock_time.time.return_value = 4660.0
        assert cache.get("city") is None

    @patch("cache.time")
    def test_exactly_at_ttl_boundary(self, mock_time):
        """Dati esattamente a 3600 secondi sono ancora validi."""
        mock_time.time.return_value = 1000.0
        cache.set("city", {"temp": 20})

        # Esattamente 1 ora (3600 secondi)
        mock_time.time.return_value = 4600.0
        assert cache.get("city") == {"temp": 20}

    @patch("cache.time")
    def test_expired_one_second_after_ttl(self, mock_time):
        """Dati a 3601 secondi sono scaduti."""
        mock_time.time.return_value = 1000.0
        cache.set("city", {"temp": 20})

        # 1 ora + 1 secondo
        mock_time.time.return_value = 4601.0
        assert cache.get("city") is None


class TestCachePersistence:
    """Test persistenza su disco per scenario offline."""

    def test_survives_memory_reset(self):
        """Dati salvati su disco sopravvivono al reset della memoria."""
        cache.set_disk_consent(True)
        cache.set("persistent", {"data": "saved"})

        # Simula reset memoria (nuova sessione)
        cache._memory_cache = {}

        result = cache.get("persistent")
        assert result == {"data": "saved"}
        cache.set_disk_consent(False)

    def test_clear_removes_file(self):
        """Clear rimuove anche il file su disco."""
        import os

        cache.set_disk_consent(True)
        cache.set("temp", {"data": 1})
        assert os.path.exists(cache._CACHE_FILE)

        cache.clear()
        assert not os.path.exists(cache._CACHE_FILE)
        cache.set_disk_consent(False)

    def test_no_file_without_consent(self):
        """Senza consenso, nessun file viene scritto su disco."""
        import os

        cache.set_disk_consent(False)
        cache.set("noconsent", {"data": 1})
        assert not os.path.exists(cache._CACHE_FILE)


class TestCacheIntegration:
    """Test integrazione cache con geocoding e weather."""

    @patch("geocoding._session.get")
    def test_geocoding_uses_cache(self, mock_get, geocoding_success_response):
        """Seconda chiamata geocoding usa la cache, non l'API."""
        from geocoding import get_coordinates

        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        # Prima chiamata: va all'API
        result1 = get_coordinates("Milano")
        assert mock_get.call_count == 1

        # Seconda chiamata: usa la cache
        result2 = get_coordinates("Milano")
        assert mock_get.call_count == 1  # non incrementa
        assert result1 == result2

    @patch("geocoding._session.get")
    def test_geocoding_cache_case_insensitive(self, mock_get, geocoding_success_response):
        """Cache geocoding e' case-insensitive."""
        from geocoding import get_coordinates

        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = geocoding_success_response

        get_coordinates("Milano")
        get_coordinates("milano")
        get_coordinates("MILANO")
        assert mock_get.call_count == 1

    @patch("weather._session.get")
    def test_weather_uses_cache(self, mock_get, weather_success_response):
        """Seconda chiamata weather usa la cache, non l'API."""
        from weather import get_weather

        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = weather_success_response

        result1 = get_weather(45.4643, 9.1895)
        assert mock_get.call_count == 1

        result2 = get_weather(45.4643, 9.1895)
        assert mock_get.call_count == 1
        assert result1 == result2

    @patch("cache.time")
    @patch("weather._session.get")
    def test_weather_refetches_after_expiry(self, mock_get, mock_time, weather_success_response):
        """Dopo scadenza cache, weather rifà la chiamata API."""
        from weather import get_weather

        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = weather_success_response

        mock_time.time.return_value = 1000.0
        get_weather(45.4643, 9.1895)
        assert mock_get.call_count == 1

        # 2 ore dopo: cache scaduta
        mock_time.time.return_value = 8200.0
        get_weather(45.4643, 9.1895)
        assert mock_get.call_count == 2
