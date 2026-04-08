import sys
import io

from geocoding import get_coordinates, get_coordinates_multi
from weather import get_weather, get_weather_multi, get_forecast
from display import display_weather, display_forecast


def _ask_mode() -> str:
    """Chiede all'utente quale modalita' usare."""
    print()
    print("  [1] Meteo corrente")
    print("  [2] Previsioni 3 giorni")
    print("  [3] Previsioni 5 giorni")
    print()
    choice = input("Scegli modalita' (1/2/3): ").strip()
    return choice


def main():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║           ☁️  APP METEO  ☀️           ║")
    print("  ╚══════════════════════════════════════╝")

    raw = input("\n  Citta' (separa piu' citta' con virgola): ").strip()

    if not raw:
        print("Errore: nessuna citta' inserita.")
        return

    city_names = [c.strip() for c in raw.split(",") if c.strip()]

    if not city_names:
        print("Errore: nessuna citta' valida inserita.")
        return

    mode = _ask_mode()
    forecast_days = 0
    if mode == "2":
        forecast_days = 3
    elif mode == "3":
        forecast_days = 5

    # Singola città
    if len(city_names) == 1:
        try:
            city_info = get_coordinates(city_names[0])
            weather_data = get_weather(city_info["latitude"], city_info["longitude"])
            display_weather(city_info, weather_data)
            if forecast_days:
                forecast = get_forecast(city_info["latitude"], city_info["longitude"], forecast_days)
                display_forecast(city_info, forecast)
        except Exception as e:
            print(f"Errore: {e}")
        return

    # Più città
    try:
        cities, errors = get_coordinates_multi(city_names)

        for err in errors:
            print(f"  Attenzione: citta' '{err['city']}' non trovata, saltata.")

        if not cities:
            print("Errore: nessuna citta' trovata.")
            return

        weather_results = get_weather_multi(cities)

        for city_info, weather_data in zip(cities, weather_results):
            display_weather(city_info, weather_data)
            if forecast_days:
                forecast = get_forecast(city_info["latitude"], city_info["longitude"], forecast_days)
                display_forecast(city_info, forecast)
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()
