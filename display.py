from datetime import datetime

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

# Nomi giorni in italiano
_DAYS_IT = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

# Larghezza box
_W = 50


def _box_top():
    return "  ╔" + "═" * _W + "╗"


def _box_bottom():
    return "  ╚" + "═" * _W + "╝"


def _box_separator():
    return "  ╠" + "═" * _W + "╣"


def _box_line(text: str):
    # Calcola la larghezza visiva considerando che le emoji occupano 2 colonne
    visual_len = 0
    for ch in text:
        if ord(ch) > 0xFFFF or ch in "☀️🌤⛅☁🌫🌦🌧🌨❄⛈🌡💧💨🌅🌇📊🔽🔼":
            visual_len += 2
        elif ch == '\ufe0f':
            continue
        else:
            visual_len += 1
    padding = _W - visual_len
    if padding < 0:
        padding = 0
    return "  ║ " + text + " " * (padding - 1) + "║"


def _bar(value: float, max_val: float, width: int = 10) -> str:
    """Genera una barra visiva proporzionale."""
    filled = int((value / max_val) * width) if max_val > 0 else 0
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)


def display_weather(city_info: dict, weather_data: dict):
    """Visualizza i dati meteo correnti con layout migliorato."""
    code = weather_data["weather_code"]
    icon = WEATHER_ICONS.get(code, "🌡️")
    description = WEATHER_DESCRIPTIONS.get(code, "Sconosciuto")

    print()
    print(_box_top())
    print(_box_line(f"{icon}  {city_info['name']}, {city_info['country']}"))
    print(_box_separator())
    print(_box_line(f"Condizioni:    {description}"))
    print(_box_line(f"Temperatura:   {weather_data['temperature']}{weather_data['temperature_unit']}"))
    print(_box_line(f"Percepita:     {weather_data['apparent_temperature']}{weather_data['temperature_unit']}"))
    print(_box_line(f"Umidita':      {weather_data['humidity']}{weather_data['humidity_unit']}  {_bar(weather_data['humidity'], 100)}"))
    print(_box_line(f"Vento:         {weather_data['wind_speed']} {weather_data['wind_speed_unit']}"))

    if weather_data.get("wind_gusts"):
        print(_box_line(f"Raffiche:      {weather_data['wind_gusts']} {weather_data['wind_speed_unit']}"))
    if weather_data.get("precipitation"):
        print(_box_line(f"Precipitaz.:   {weather_data['precipitation']} {weather_data.get('precipitation_unit', 'mm')}"))
    if weather_data.get("pressure"):
        print(_box_line(f"Pressione:     {weather_data['pressure']} {weather_data.get('pressure_unit', 'hPa')}"))

    print(_box_bottom())
    print()


def display_forecast(city_info: dict, forecast: list[dict]):
    """Visualizza le previsioni giornaliere in un unico blocco compatto."""
    print()
    print(_box_top())
    print(_box_line(f"📊  Previsioni {len(forecast)} giorni - {city_info['name']}, {city_info['country']}"))

    for day in forecast:
        print(_box_separator())

        date = datetime.strptime(day["date"], "%Y-%m-%d")
        day_name = _DAYS_IT[date.weekday()]
        date_str = date.strftime("%d/%m")
        code = day["weather_code"]
        icon = WEATHER_ICONS.get(code, "🌡️")
        desc = WEATHER_DESCRIPTIONS.get(code, "Sconosciuto")

        sunrise_t = day["sunrise"].split("T")[1] if "T" in day["sunrise"] else day["sunrise"]
        sunset_t = day["sunset"].split("T")[1] if "T" in day["sunset"] else day["sunset"]

        print(_box_line(f"{day_name} {date_str}  {icon} {desc}"))
        print(_box_line(f"  {day['temp_max']:+.1f}° / {day['temp_min']:+.1f}°   percepita {day['feels_max']:+.1f}° / {day['feels_min']:+.1f}°"))
        print(_box_line(f"  💧 {day['precipitation']}{day['precipitation_unit']} ({day['precipitation_prob']}%)   💨 {day['wind_max']} {day['wind_unit']} (raff. {day['wind_gusts_max']})"))
        print(_box_line(f"  🌅 {sunrise_t}  🌇 {sunset_t}"))

    print(_box_bottom())
    print()
