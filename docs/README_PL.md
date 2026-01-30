# Aplikacja Webowa do Predykcji Wyników Piłkarskich

Aplikacja webowa wykorzystująca uczenie maszynowe do przewidywania wyników meczów piłkarskich w głównych ligach europejskich. Zbudowana przy użyciu Streamlit, XGBoost i SHAP dla wyjaśnialnej sztucznej inteligencji.

## Funkcje

- **Predykcje Meczów**: Przewidywanie wyników (Gospodarze/Remis/Goście) przy użyciu regresji XGBoost na różnicy bramek
- **Rekomendacje Zakładów**: Sugestie zakładów wspierane przez AI z obliczaniem przewagi i wielkością stawki według kryterium Kelly'ego
- **Wyjaśnialność**: Wyjaśnienia oparte na SHAP pokazujące, które cechy wpływają na każdą predykcję
- **Śledzenie Historii**: Baza danych SQLite do przechowywania uruchomień, predykcji, zakładów i wyników
- **Wsparcie Wielu Lig**: 10 lig europejskich z danymi z football-data.co.uk
- **Elastyczne Przechowywanie**: Lokalny system plików lub Azure Blob Storage

## Szybki Start

### Wymagania

- Python 3.8+ (zalecany 3.10 lub 3.11)
- Git
- pip

### Instalacja

```bash
# Sklonuj repozytorium
git clone https://github.com/your-repo/football-prediction-web-app.git
cd football-prediction-web-app

# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Aktywuj (Linux/macOS)
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Zainicjalizuj dane (tylko za pierwszym razem)
python run_pipelines.py

# Uruchom aplikację
streamlit run app.py
```

Aplikacja otwiera się pod adresem `http://localhost:8501`

## Struktura Projektu

```
football-prediction-web-app/
├── app.py                      # Punkt wejścia interfejsu Streamlit
├── run_pipelines.py            # Orkiestrator pipeline'ów danych
├── requirements.txt            # Zależności Python
├── .env.example                # Szablon zmiennych środowiskowych
│
├── src/
│   ├── db/                     # Moduł bazy danych SQLite
│   │   ├── __init__.py         # Eksporty modułu
│   │   ├── schema.py           # Definicje tabel
│   │   └── client.py           # Operacje CRUD
│   │
│   ├── explain/                # Wyjaśnialność modelu
│   │   └── shap.py             # Obliczanie wartości SHAP
│   │
│   ├── frontend/               # Komponenty UI Streamlit
│   │   ├── data.py             # Ładowanie/agregacja danych
│   │   ├── metrics.py          # Metryki wydajności
│   │   └── match_report.py     # Renderowanie kart meczów
│   │
│   ├── modelling/              # Eksperymenty ML
│   │   └── experiment.py       # Strojenie hiperparametrów
│   │
│   ├── pipelines/              # Przetwarzanie danych
│   │   └── update.py           # Orkiestracja pipeline'ów
│   │
│   ├── preprocess/             # Inżynieria cech
│   │   └── features.py         # Klasa SeasonProcessor
│   │
│   ├── storage/                # Backendy przechowywania
│   │   └── tables.py           # Tabele Lokalne/Azure/Zewnętrzne
│   │
│   ├── trades/                 # Rekomendacje zakładów
│   │   ├── __init__.py         # Eksporty modułu
│   │   └── recommend.py        # Scoring i wyjaśnialność
│   │
│   └── utils/                  # Narzędzia
│       ├── config.py           # Klasa konfiguracji
│       └── functions.py        # Funkcje pomocnicze
│
├── data/                       # Lokalne przechowywanie danych
│   ├── fixtures/               # Aktualne terminy meczów
│   ├── results/                # Historyczne wyniki meczów
│   ├── processed/              # Przetworzone dane treningowe
│   ├── predictions/            # Predykcje modelu
│   ├── models/                 # Wytrenowane modele
│   └── app.db                  # Baza danych SQLite
│
├── tests/                      # Zestaw testów
│   ├── conftest.py             # Fixtures pytest
│   ├── test_imports.py         # Weryfikacja importów
│   ├── test_trade_scoring.py   # Testy logiki zakładów
│   └── test_explainability.py  # Testy ekstrakcji SHAP
│
└── docs/                       # Dokumentacja
    ├── README_EN.md            # Dokumentacja angielska
    ├── README_PL.md            # Ten plik (polski)
    ├── SETUP_WINDOWS.md        # Przewodnik instalacji Windows
    ├── SETUP_LINUX.md          # Przewodnik instalacji Linux/macOS
    ├── CONFIGURATION.md        # Referencja konfiguracji
    └── TROUBLESHOOTING.md      # Typowe problemy
```

## Konfiguracja

### Zmienne Środowiskowe

| Zmienna | Domyślna | Opis |
|---------|----------|------|
| `STORAGE_BACKEND` | `local` | Backend przechowywania: `local` lub `azure` |
| `DATA_DIR` | `data` | Lokalny katalog danych |
| `DB_PATH` | `data/app.db` | Ścieżka bazy danych SQLite |
| `AZURE_CONNECTION_STRING` | - | Połączenie Azure Blob (jeśli backend azure) |
| `AZURE_CONTAINER_NAME` | - | Nazwa kontenera Azure (jeśli backend azure) |

### Obsługiwane Ligi

| Kod | Liga | Dane Dostępne Od |
|-----|------|------------------|
| E0 | Anglia Premier League | 2005 |
| E1 | Anglia Championship | 2005 |
| D1 | Niemcy Bundesliga | 2006 |
| I1 | Włochy Serie A | 2005 |
| SP1 | Hiszpania La Liga | 2005 |
| F1 | Francja Ligue 1 | 2005 |
| P1 | Portugalia Primeira Liga | 2017 |
| N1 | Holandia Eredivisie | 2017 |
| T1 | Turcja Super Lig | 2017 |
| B1 | Belgia First Division | 2017 |

## Jak To Działa

### Pipeline Danych

1. **Pobieranie Terminów**: Pobranie aktualnych terminów meczów z football-data.co.uk
2. **Pobieranie Wyników**: Pobranie historycznych wyników meczów według sezonu/ligi
3. **Inżynieria Cech**: Obliczenie statystyk drużyn, formy, pozycji
4. **Trening Modelu**: Trening regresora XGBoost na różnicy bramek
5. **Predykcje**: Generowanie predykcji z wyjaśnieniami SHAP
6. **Zapis**: Zapis do lokalnych plików parquet lub Azure Blob Storage

### System Rekomendacji Zakładów

Silnik rekomendacji zakładów ocenia nadchodzące mecze:

1. **Pewność Modelu**: Obliczana przy użyciu funkcji sigmoid na przewidywanej różnicy bramek
   - `pewność = 1 / (1 + exp(-|różnica_bramek|))`
   - Różnica 0 bramek → 50% pewności
   - Różnica 1 bramki → 73% pewności
   - Różnica 2 bramek → 88% pewności

2. **Implikowane Prawdopodobieństwo Rynkowe**: `1 / kurs`

3. **Przewaga (Edge)**: `pewność_modelu - prawdopodobieństwo_implikowane`

4. **Wartość Oczekiwana (EV)**: `przewaga × (kurs - 1)`

5. **Wielkość Stawki**: Ćwierć-kryterium Kelly'ego
   - `stawka = przewaga / (4 × (kurs - 1))`
   - Ograniczona do maksymalnie 5% bankrolla

6. **Wynik Kompozytowy**: Łączy przewagę, EV i bonus za optymalny zakres kursów

### Wyjaśnialność

Każda predykcja zawiera wartości SHAP (SHapley Additive exPlanations):

- **Dodatnie SHAP**: Cechy przesuwające predykcję w kierunku zwycięstwa gospodarzy
- **Ujemne SHAP**: Cechy przesuwające predykcję w kierunku zwycięstwa gości
- **Główne Czynniki**: Najbardziej wpływowe cechy wyświetlane w UI i zapisywane w bazie danych

## Schemat Bazy Danych

### Tabele

| Tabela | Przeznaczenie |
|--------|---------------|
| `runs` | Rekordy uruchomień pipeline'u/aplikacji |
| `predictions` | Predykcje modelu per uruchomienie |
| `trades` | Rekomendowane zakłady per uruchomienie |
| `results` | Końcowe wyniki meczów |

### Kluczowe Pola

**predictions**:
- `match_key`: Unikalny identyfikator (data_liga_gospodarz_gość)
- `pred_result`: Predykcja H/D/A
- `pred_diff`: Przewidywana różnica bramek
- `shap_top_json`: Top 5 cech SHAP

**trades**:
- `side`: Strona zakładu (H/D/A)
- `edge`: Przewaga modelu nad rynkiem
- `ev`: Wartość oczekiwana
- `stake`: Rekomendowana wielkość stawki
- `rationale_json`: Wyjaśnienie z czynnikami SHAP

## Referencja API

### Moduł Zakładów

```python
from src.trades import TradeRecommender, TradeConfig, get_recommended_trades

# Konfiguracja parametrów zakładów
config = TradeConfig(
    min_edge=0.05,      # Wymagana minimalna przewaga 5%
    min_odds=1.2,       # Minimalny kurs
    max_odds=10.0,      # Maksymalny kurs
    bankroll=100.0,     # Bankroll do obliczenia stawki
    top_n=10            # Liczba rekomendowanych zakładów
)

# Pobierz rekomendacje
trades = get_recommended_trades(predictions_df, config)

for trade in trades:
    print(f"{trade.home_team} vs {trade.away_team}")
    print(f"  Strona: {trade.side} @ {trade.odds}")
    print(f"  Przewaga: {trade.edge*100:.1f}%")
    print(f"  Stawka: {trade.stake:.2f}")
```

### Moduł Bazy Danych

```python
from src.db import init_db, create_run, save_predictions, save_trades

# Zainicjalizuj bazę danych
init_db()

# Utwórz rekord uruchomienia
run_id = create_run(notes="Dzienne uruchomienie predykcji")

# Zapisz predykcje
count = save_predictions(run_id, predictions_df)

# Zapisz zakłady
trade_dicts = [t.to_dict() for t in trades]
save_trades(run_id, trade_dicts)
```

## Testowanie

```bash
# Uruchom wszystkie testy
pytest tests/ -v

# Uruchom konkretny plik testowy
pytest tests/test_trade_scoring.py -v

# Uruchom z pokryciem kodu
pytest tests/ --cov=src --cov-report=html
```

## Rozwój

### Dodawanie Nowych Funkcji

1. Utwórz gałąź funkcji: `git checkout -b feature/moja-funkcja`
2. Zaimplementuj zmiany z testami
3. Uruchom testy: `pytest tests/`
4. Zatwierdź z opisowym komunikatem
5. Utwórz pull request

### Styl Kodu

- Używaj type hints dla sygnatur funkcji
- Postępuj zgodnie z wytycznymi PEP 8
- Dodawaj docstrings dla funkcji publicznych
- Utrzymuj funkcje skoncentrowane i małe

## Rozwiązywanie Problemów

Zobacz [TROUBLESHOOTING.md](TROUBLESHOOTING.md) dla typowych problemów.

### Szybkie Rozwiązania

**Brak danych predykcji:**
```bash
python run_pipelines.py
```

**Problemy z bazą danych:**
```bash
rm data/app.db  # Usuń i pozwól aplikacji odtworzyć
```

**Port w użyciu:**
```bash
streamlit run app.py --server.port 8502
```

## Licencja

Ten projekt służy celom edukacyjnym. Zakłady wiążą się z ryzykiem; korzystaj odpowiedzialnie.

## Podziękowania

- Źródło danych: [football-data.co.uk](https://www.football-data.co.uk/)
- Framework ML: XGBoost
- Wyjaśnialność: SHAP
- Framework UI: Streamlit

---

## Słownik Terminów

| Termin Angielski | Termin Polski | Opis |
|------------------|---------------|------|
| Edge | Przewaga | Różnica między pewnością modelu a prawdopodobieństwem implikowanym przez rynek |
| EV (Expected Value) | Wartość Oczekiwana | Oczekiwany zysk z zakładu |
| Kelly Criterion | Kryterium Kelly'ego | Formuła optymalizacji wielkości stawki |
| SHAP | SHAP | SHapley Additive exPlanations - metoda wyjaśniania predykcji |
| Bankroll | Bankroll | Całkowity kapitał przeznaczony na zakłady |
| Stake | Stawka | Kwota postawiona na zakład |
| Odds | Kurs | Współczynnik oferowany przez bukmachera |
| Home Win (H) | Zwycięstwo Gospodarzy | Wygrana drużyny grającej u siebie |
| Draw (D) | Remis | Mecz zakończony remisem |
| Away Win (A) | Zwycięstwo Gości | Wygrana drużyny grającej na wyjeździe |
| Pipeline | Pipeline | Sekwencja operacji przetwarzania danych |
| Feature Engineering | Inżynieria Cech | Tworzenie nowych zmiennych z surowych danych |
| Model Confidence | Pewność Modelu | Stopień pewności modelu co do predykcji |

## Często Zadawane Pytania (FAQ)

### Jak często powinienem aktualizować dane?

Zalecamy uruchamianie `python run_pipelines.py` przed każdą kolejką ligową, najlepiej w środę i sobotę.

### Czy mogę używać aplikacji bez Azure?

Tak! Domyślnie aplikacja używa lokalnego systemu plików (`STORAGE_BACKEND=local`). Azure jest opcjonalny.

### Jak interpretować wartość Edge?

- Edge 5% oznacza, że model uważa, iż rzeczywiste prawdopodobieństwo jest o 5 punktów procentowych wyższe niż implikuje rynek
- Wyższy edge = większa teoretyczna przewaga
- Minimalna rekomendowana wartość: 5%

### Co oznacza wynik SHAP?

- Wartości SHAP pokazują, jak każda cecha wpływa na predykcję
- Dodatnie wartości: przesuwają predykcję w kierunku zwycięstwa gospodarzy
- Ujemne wartości: przesuwają predykcję w kierunku zwycięstwa gości
- Większa wartość absolutna = większy wpływ

### Dlaczego niektóre mecze nie mają rekomendacji?

Mecz może nie mieć rekomendacji, jeśli:
- Edge jest poniżej minimalnego progu (domyślnie 5%)
- Kursy są poza zakresem (domyślnie 1.2-10.0)
- Wynik kompozytowy jest zbyt niski
- Mecz już się odbył (ma wynik)

### Jak zmienić konfigurację zakładów?

Użyj panelu bocznego w aplikacji Streamlit lub programowo:

```python
config = TradeConfig(
    min_edge=0.10,    # Zwiększ minimalny edge do 10%
    bankroll=500.0,   # Zwiększ bankroll
    top_n=5           # Pokaż tylko top 5 zakładów
)
```
