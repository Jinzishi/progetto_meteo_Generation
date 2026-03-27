from geocoding import get_coordinates
from weather import get_weather
from display import display_weather


def main():
    print("═══ App Meteo ═══")
    city = input("Inserisci il nome della città: ").strip()

    if not city:
        print("Errore: nessuna città inserita.")
        return

    try:
        city_info = get_coordinates(city)
        weather_data = get_weather(city_info["latitude"], city_info["longitude"])
        display_weather(city_info, weather_data)
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()
