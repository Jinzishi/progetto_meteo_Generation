import os

# URL API configurabili tramite variabili d'ambiente
GEOCODING_API_URL = os.environ.get(
    "METEO_GEOCODING_URL",
    "https://geocoding-api.open-meteo.com/v1/search",
)
WEATHER_API_URL = os.environ.get(
    "METEO_WEATHER_URL",
    "https://api.open-meteo.com/v1/forecast",
)

# API key opzionale (Open-Meteo non la richiede, ma utile se si cambia provider)
API_KEY = os.environ.get("METEO_API_KEY", "")

# Timeout richieste HTTP (secondi)
REQUEST_TIMEOUT = int(os.environ.get("METEO_REQUEST_TIMEOUT", "10"))

# Cache TTL (secondi) - default 1 ora
CACHE_TTL = int(os.environ.get("METEO_CACHE_TTL", "3600"))

# Abilitazione cache su disco (l'utente puo' disabilitarla)
CACHE_DISK_ENABLED = os.environ.get("METEO_CACHE_DISK", "true").lower() == "true"

# Numero massimo di citta' per richiesta batch
MAX_CITIES = int(os.environ.get("METEO_MAX_CITIES", "10"))
