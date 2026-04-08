"""Genera il report PDF del progetto App Meteo."""

from fpdf import FPDF

# Font family name after add_font
_FONT = "dejavu"
_MONO = "dejavumono"


class ReportPDF(FPDF):
    def _setup_fonts(self):
        """Registra font Unicode dal sistema."""
        fonts = "C:/Windows/Fonts"
        self.add_font("dejavu", "", f"{fonts}/arial.ttf")
        self.add_font("dejavu", "B", f"{fonts}/arialbd.ttf")
        self.add_font("dejavu", "I", f"{fonts}/ariali.ttf")
        self.add_font("dejavumono", "", f"{fonts}/consola.ttf")

    def header(self):
        self.set_font(_FONT, "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "App Meteo - Report di Progetto", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font(_FONT, "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font(_FONT, "B", 13)
        self.set_text_color(30, 80, 160)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 80, 160)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(3)

    def body_text(self, text):
        self.set_font(_FONT, "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def code_block(self, text):
        self.set_font(_MONO, "", 8)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 4.5, text, fill=True)
        self.ln(2)

    def bullet(self, text):
        self.set_font(_FONT, "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(10)
        self.multi_cell(0, 5.5, f"  - {text}")


def main():
    pdf = ReportPDF()
    pdf._setup_fonts()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- Titolo ---
    pdf.set_font(_FONT, "B", 22)
    pdf.set_text_color(20, 60, 140)
    pdf.cell(0, 15, "App Meteo", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font(_FONT, "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Applicazione CLI per previsioni meteorologiche in Python",
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # --- 1. Descrizione ---
    pdf.section_title("1. Descrizione dell'applicazione")
    pdf.body_text(
        "App Meteo e' un'applicazione a riga di comando scritta in Python che permette "
        "di consultare le condizioni meteorologiche correnti e le previsioni fino a 5 giorni "
        "per qualsiasi citta' nel mondo. L'app utilizza le API gratuite di Open-Meteo: la "
        "Geocoding API converte il nome della citta' in coordinate geografiche, e la Weather "
        "Forecast API restituisce i dati meteo in tempo reale."
    )
    pdf.body_text(
        "L'architettura e' modulare (geocoding.py, weather.py, display.py, cache.py, config.py) "
        "e supporta: ricerca multi-citta' con batch API, cache con scadenza a 1 ora e "
        "persistenza su disco, interfaccia con box Unicode e icone meteo, configurazione "
        "tramite variabili d'ambiente, e una suite di 90 test automatizzati."
    )

    # --- 2. Funzionalita' principali ---
    pdf.section_title("2. Funzionalita' principali")
    features = [
        "Meteo corrente: temperatura, percepita, umidita', vento, raffiche, precipitazioni, pressione",
        "Previsioni a 3 o 5 giorni con max/min, precipitazioni, vento, alba e tramonto",
        "Supporto multi-citta' con input separato da virgola e batch API",
        "Cache intelligente: TTL 1 ora, persistenza su disco per uso offline",
        "Interfaccia visiva con box Unicode, icone meteo e barre proporzionali",
        "Configurazione completa tramite variabili d'ambiente (.env)",
        "90 test pytest: validazione, mock API, pipeline, sicurezza, edge cases",
    ]
    for f in features:
        pdf.bullet(f)
    pdf.ln(2)

    # --- 3. Screenshot simulato ---
    pdf.section_title("3. Esempio di output")
    pdf.body_text("Meteo corrente per una citta':")
    pdf.code_block(
        "  +==================================================+\n"
        "  | (sole)  Milano, Italia                           |\n"
        "  +==================================================+\n"
        "  | Condizioni:    Sereno                            |\n"
        "  | Temperatura:   22.5 C                            |\n"
        "  | Percepita:     21.0 C                            |\n"
        "  | Umidita':      65%  ||||||....                   |\n"
        "  | Vento:         12.3 km/h                         |\n"
        "  | Raffiche:      20.1 km/h                         |\n"
        "  | Pressione:     1013.2 hPa                        |\n"
        "  +==================================================+"
    )
    pdf.body_text("Previsioni a 3 giorni:")
    pdf.code_block(
        "  +==================================================+\n"
        "  | Previsioni 3 giorni - Milano, Italia             |\n"
        "  +==================================================+\n"
        "  | Mer 08/04  (sole) Sereno                         |\n"
        "  |   +22.5 / +12.0    percepita +21.0 / +10.5      |\n"
        "  |   Pioggia: 0.0mm (0%)   Vento: 12.3 km/h        |\n"
        "  |   Alba: 06:30  Tramonto: 19:45                   |\n"
        "  +--------------------------------------------------+\n"
        "  | Gio 09/04  (nuvola) Coperto                      |\n"
        "  |   +18.0 / +10.5    percepita +16.5 / +8.0       |\n"
        "  |   Pioggia: 0.0mm (10%)  Vento: 20.5 km/h        |\n"
        "  |   Alba: 06:28  Tramonto: 19:46                   |\n"
        "  +==================================================+"
    )

    # --- 4. Uso dell'IA ---
    pdf.section_title("4. Utilizzo dell'intelligenza artificiale")
    pdf.body_text(
        "L'intelligenza artificiale (Claude) e' stata utilizzata come collaboratore durante "
        "l'intero ciclo di sviluppo del progetto, non solo come generatore di codice:"
    )
    usages = [
        "Progettazione architetturale: strutturazione modulare del progetto con responsabilita' "
        "separate (geocoding, weather, display, cache, config)",
        "Implementazione guidata: ogni funzionalita' e' stata sviluppata seguendo una strategia "
        "di test strutturata con mock delle API esterne",
        "Debugging: l'IA ha identificato problemi come la sostituzione di sys.stdout a livello "
        "modulo che corrompeva il capture di pytest, e conflitti tra mock di moduli condivisi",
        "Code review: verifica della copertura test per ogni modifica, identificazione di test "
        "mancanti e di bug nei test stessi (es. importlib.reload dentro patch.dict)",
        "Sicurezza: analisi dei rischi, implementazione di sanitizzazione input, gestione "
        "consenso utente e permessi restrittivi sui file",
    ]
    for u in usages:
        pdf.bullet(u)
    pdf.ln(2)

    # --- 5. Riflessione ---
    pdf.section_title("5. Cosa ho imparato e cosa e' stato impegnativo")
    pdf.body_text(
        "La parte piu' formativa e' stata la progettazione dei test. Non si tratta solo di "
        "\"testare che funzioni\", ma di pensare a tutti gli scenari: cosa succede se l'API "
        "va in timeout? Se la risposta ha un formato inaspettato? Se l'utente inserisce emoji "
        "o caratteri speciali? Questo approccio ha portato a scoprire e prevenire bug reali."
    )
    pdf.body_text(
        "La sfida piu' grande e' stata la gestione dei mock nelle chiamate API. Quando due "
        "moduli condividono lo stesso oggetto requests.Session, i mock devono essere applicati "
        "con precisione al target giusto (es. geocoding._session.get anziche' requests.get). "
        "Un errore qui causa test che passano senza realmente testare, o peggio, che chiamano "
        "le API reali durante i test."
    )

    # --- 6. Orgoglio ---
    pdf.section_title("6. Una cosa di cui sono orgoglioso")
    pdf.body_text(
        "La suite di 90 test con copertura completa su ogni funzionalita'. Non e' solo un "
        "numero: ogni test ha uno scopo preciso, i mock sono deterministici (zero chiamate "
        "di rete), e i test di sicurezza verificano che la sanitizzazione dell'input blocchi "
        "tentativi di injection prima ancora che raggiungano l'API. Il fatto che ogni commit "
        "sia stato accompagnato dalla verifica che tutti i test passassero da' fiducia nella "
        "solidita' del codice."
    )

    # --- 7. Miglioramenti ---
    pdf.section_title("7. Cosa migliorerei con piu' tempo")
    pdf.body_text(
        "Trasformerei l'app in un'applicazione web con Flask o FastAPI, aggiungendo "
        "un'interfaccia grafica responsive accessibile da browser e dispositivi mobili. "
        "Questo permetterebbe di sfruttare grafici interattivi per le previsioni, mappe "
        "meteorologiche, e notifiche push per allerte meteo. Aggiungerei anche il supporto "
        "per unita' imperiali (Fahrenheit, mph), la localizzazione multilingua, e un sistema "
        "di preferiti per le citta' piu' cercate dall'utente."
    )

    # --- Struttura progetto ---
    pdf.section_title("Struttura del progetto")
    pdf.code_block(
        "progetto_meteo_Generation/\n"
        "|-- main.py              # Entry point\n"
        "|-- geocoding.py         # Citta' -> coordinate\n"
        "|-- weather.py           # Coordinate -> dati meteo\n"
        "|-- display.py           # Visualizzazione terminale\n"
        "|-- cache.py             # Cache TTL + persistenza\n"
        "|-- config.py            # Configurazione env vars\n"
        "|-- requirements.txt     # Dipendenze\n"
        "|-- .env.example         # Template variabili ambiente\n"
        "|-- README.md            # Documentazione\n"
        "+-- tests/               # 90 test pytest\n"
        "    |-- test_input.py\n"
        "    |-- test_geocoding.py\n"
        "    |-- test_weather.py\n"
        "    |-- test_cache.py\n"
        "    |-- test_config.py\n"
        "    |-- test_security.py\n"
        "    |-- test_pipeline.py\n"
        "    |-- test_error_handling.py\n"
        "    +-- test_edge_cases.py"
    )

    # --- Salva ---
    output = "C:/Users/Utente/Desktop/OMNI_progetti/progetto_meteo_Generation/Report_App_Meteo.pdf"
    pdf.output(output)
    print(f"PDF generato: {output}")


if __name__ == "__main__":
    main()
