# Aplikacja Webowa do Prognozowania Meczów – Dokumentacja (PL)

## Przegląd
Ten projekt to aplikacja webowa oparta na Streamlit, która prognozuje wyniki meczów piłkarskich przy użyciu modeli XGBoost i wyjaśnia te prognozy za pomocą wartości SHAP. Dane są pobierane z https://www.football-data.co.uk, przetwarzane lokalnie i zapisywane w plikach, bez wykorzystania usług Azure.

## Struktura Projektu
- Katalog główny: `app.py` (interfejs Streamlit), `run_pipelines.py` (pipeline danych i prognoz).
- Kod źródłowy: `src/` z modułami:
  - `preprocess/` – inżynieria cech i logika tabel ligowych.
  - `modelling/` – trenowanie modeli oraz strojenie hiperparametrów.
  - `pipelines/` – pipeline od pobrania danych do prognoz.
  - `storage/` – warstwa lokalnego zapisu/odczytu.
  - `frontend/` – dashboard, metryki i raporty meczów.
  - `utils/` – konfiguracja i funkcje pomocnicze.
- Dane lokalne: katalog `data/` (tworzony w czasie działania) przechowuje wyniki, terminarze, dane przetworzone, modele i prognozy.

## Instalacja
1. Utwórz wirtualne środowisko:
   - Windows: `python -m venv .venv` oraz `.\.venv\Scripts\activate`
2. Zainstaluj zależności:
   - `pip install -r requirements.txt`

## Uruchamianie Pipeline’u i Aplikacji
1. Wygeneruj lub odśwież lokalne dane, wytrenuj model i zbuduj prognozy:
   - `python run_pipelines.py`
2. Uruchom aplikację webową:
   - `streamlit run app.py`
3. Otwórz adres podany przez Streamlit (zwykle `http://localhost:8501`), aby korzystać z dashboardu.

## Przechowywanie Danych
1. `run_pipelines.py` pobiera surowe wyniki/terminarze z Football-Data, przetwarza je, trenuje/ładuje model i zapisuje prognozy do katalogu `data/`.
2. Aplikacja Streamlit odczytuje prognozy z `data/` poprzez `src/frontend/data.py`.
3. Do lokalnego uruchomienia nie jest wymagane żadne konto Azure – wszystkie pliki pozostają na Twojej maszynie.
