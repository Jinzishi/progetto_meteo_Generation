# App Meteo

Applicazione CLI in Python che recupera e visualizza le condizioni meteorologiche correnti per qualsiasi citta' nel mondo, utilizzando le API gratuite di Open-Meteo.

## Installazione

**Prerequisiti:** Python 3.8+

```bash
# Clona il repository
git clone https://github.com/tuo-utente/progetto-meteo.git
cd progetto-meteo

# Installa le dipendenze
pip install -r requirements.txt
```

## Utilizzo

```bash
python main.py
```

L'app chiede il nome di una citta' e mostra il meteo corrente:

```
=== App Meteo ===
Inserisci il nome della citta': Milano
```

## Output di esempio

```
  ☀️  Meteo per Milano, Italia
  ────────────────────────────────────────
  Condizioni:    Sereno
  Temperatura:   22.5°C
  Percepita:     21.0°C
  Umidita':      65%
  Vento:         12.3 km/h
```

## Funzionalita'

- Ricerca citta' per nome con supporto multilingua (es. "Sao Paulo", "Zurich", "New York")
- Geocodifica automatica tramite Open-Meteo Geocoding API
- Dati meteo in tempo reale: temperatura, temperatura percepita, umidita', vento, condizioni
- Icone meteo visuali nel terminale
- Descrizioni condizioni in italiano (22 codici meteo supportati)

## Struttura del progetto

```
progetto_meteo_Generation/
├── main.py            # Entry point e orchestrazione
├── geocoding.py       # Conversione citta' -> coordinate (lat/lon)
├── weather.py         # Recupero dati meteo da coordinate
├── display.py         # Formattazione e visualizzazione output
├── requirements.txt   # Dipendenze del progetto
└── tests/
    ├── conftest.py          # Fixtures condivise
    ├── test_input.py        # Test validazione input
    ├── test_geocoding.py    # Test servizio geocoding
    ├── test_weather.py      # Test servizio meteo
    ├── test_pipeline.py     # Test flusso completo
    ├── test_error_handling.py  # Test gestione errori
    └── test_edge_cases.py   # Test casi limite
```

## Gestione degli errori

L'app gestisce i seguenti scenari senza crash:

| Scenario | Comportamento |
|----------|---------------|
| Input vuoto o solo spazi | Messaggio: "Errore: nessuna citta' inserita." |
| Citta' non trovata | Messaggio: "Errore: Citta' 'xyz' non trovata." |
| Timeout API | Messaggio di errore generico |
| Errore di connessione | Messaggio di errore generico |
| Errore HTTP (500, 403, ecc.) | Messaggio di errore generico |

## Informazioni API

L'app utilizza due API gratuite di [Open-Meteo](https://open-meteo.com/) (nessuna chiave API richiesta):

- **Geocoding API** (`geocoding-api.open-meteo.com/v1/search`) - Converte il nome della citta' in coordinate geografiche (latitudine/longitudine)
- **Weather Forecast API** (`api.open-meteo.com/v1/forecast`) - Restituisce i dati meteo correnti date le coordinate

Parametri meteo richiesti: `temperature_2m`, `relative_humidity_2m`, `apparent_temperature`, `weather_code`, `wind_speed_10m`

## Test

```bash
# Esegui tutti i test
python -m pytest tests/ -v

# Esegui test specifici
python -m pytest tests/test_geocoding.py -v
```

La test suite comprende 47 test con copertura su:
- Validazione input (6 test)
- Servizio geocoding con mock API (8 test)
- Servizio meteo con mock API (7 test)
- Pipeline completa (3 test)
- Gestione errori (7 test)
- Casi limite: UTF-8, emoji, nomi lunghi, test parametrizzati (16 test)

## Miglioramenti futuri

- Previsioni multi-giorno (3/5/7 giorni)
- Cache delle richieste per ridurre chiamate API
- Supporto per unita' imperiali (Fahrenheit, mph)
- Storico ricerche salvato su file
- Interfaccia web con Flask/FastAPI
- Supporto per coordinate dirette oltre al nome citta'
