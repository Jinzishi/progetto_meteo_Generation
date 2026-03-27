WEATHER_DESCRIPTIONS = {
    0: "Sereno",
    1: "Prevalentemente sereno",
    2: "Parzialmente nuvoloso",
    3: "Coperto",
    45: "Nebbia",
    48: "Nebbia con brina",
    51: "Pioggerella leggera",
    53: "Pioggerella moderata",
    55: "Pioggerella intensa",
    61: "Pioggia leggera",
    63: "Pioggia moderata",
    65: "Pioggia forte",
    71: "Neve leggera",
    73: "Neve moderata",
    75: "Neve forte",
    80: "Rovesci leggeri",
    81: "Rovesci moderati",
    82: "Rovesci violenti",
    95: "Temporale",
    96: "Temporale con grandine leggera",
    99: "Temporale con grandine forte",
}

WEATHER_ICONS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌦️",
    53: "🌦️",
    55: "🌧️",
    61: "🌧️",
    63: "🌧️",
    65: "🌧️",
    71: "🌨️",
    73: "🌨️",
    75: "❄️",
    80: "🌦️",
    81: "🌧️",
    82: "⛈️",
    95: "⛈️",
    96: "⛈️",
    99: "⛈️",
}


def display_weather(city_info: dict, weather_data: dict):
    """Visualizza i dati meteo in formato leggibile."""
    code = weather_data["weather_code"]
    icon = WEATHER_ICONS.get(code, "🌡️")
    description = WEATHER_DESCRIPTIONS.get(code, "Sconosciuto")

    print()
    print(f"  {icon}  Meteo per {city_info['name']}, {city_info['country']}")
    print("  " + "─" * 40)
    print(f"  Condizioni:    {description}")
    print(f"  Temperatura:   {weather_data['temperature']}{weather_data['temperature_unit']}")
    print(f"  Percepita:     {weather_data['apparent_temperature']}{weather_data['temperature_unit']}")
    print(f"  Umidità:       {weather_data['humidity']}{weather_data['humidity_unit']}")
    print(f"  Vento:         {weather_data['wind_speed']} {weather_data['wind_speed_unit']}")
    print()
