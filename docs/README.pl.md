# Football Prediction Web App �?" Dokumentacja Techniczna

## 1. Przegl�d
Football Prediction Web App pobiera terminarze i wyniki pi�'karskie, tworzy cechy, trenuje modele XGBoost, wyja�>nia predykcje za pomoc� SHAP i prezentuje wska��niki w dashboardzie Streamlit opartym na Azure Blob Storage oraz pipeline'ach CI/CD.

## 2. Struktura Repozytorium
| ��cie��ka | Opis |
| --- | --- |
| `app.py` | Wej�>ciowy interfejs Streamlit (filtry lig, metryki, raporty meczowe). |
| `run_pipelines.py` | Uruchamia procesy od�>wie��ania danych i partycji walidacyjnej w Azure. |
| `src/frontend/` | Helpery Streamlit (`data.py`, `metrics.py`, `match_report.py`). |
| `src/preprocess/` | In��ynieria cech (np. `features.py`, `league_table.py`). |
| `src/modelling/` | Trening modeli, eksperymenty Hyperopt, serializacja modeli. |
| `src/explain/` | Modu�'y do wyja�>nialno�>ci SHAP. |
| `src/storage/` | Adaptery Azure Blob (`AzureBlobTable`, operacje na parquet). |
| `src/utils/config.py` | Konfiguracja centralna (metadane lig, �>cie��ki, progi). |
| `.github/workflows/` | Workflows GitHub Actions dla CI/CD. |
| `train.ipynb` | Notebook badawczy do eksperymentƈw i Hyperopt. |

## 3. Konfiguracja ��rodowiska
1. **Wymagania:** Python 3.9+, Azure z Blob Storage, Git, opcjonalnie Jupyter.
2. **��rodowisko wirtualne:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Sekrety i konfiguracja:** Zacznij od przyk�'adowego pliku `.env.example` i trzymaj sekrety tylko w swojej lokalnej kopii:
   ```powershell
   copy .env.example .env
   notepad .env
   ```
   Wymagane klucze (dla pe�'nego trybu z Azure):
   ```text
   AZURE_CONNECTION_STRING=...
   AZURE_CONTAINER_NAME=...
   ```
   Opcjonalne nadpisania (zwykle mo��esz zostawi�� warto�>ci domy�>lne z kodu):
   ```text
   FOOTBALL_DATA_URL=https://www.football-data.co.uk
   FOOTBALL_DATA_TABLE=mmz4281
   PREDICTED_FPATH=static/predicted.txt
   PREDICTIONS_SOURCE=azure        # albo "local" dla trybu offline
   PREDICTIONS_LOCAL_PATH=data/predictions_valid.parquet
   ```
4. **Od�>wie��anie danych:** Po zmianach w pipeline'ach/storage uruchom `python run_pipelines.py`.
5. **Lokalny dashboard:** `streamlit run app.py` odczytuje dane z Azure.
6. **Notebook:** `jupyter notebook train.ipynb` do eksperymentƈw.

### 3.0 Referencja konfiguracji

| Klucz                    | Domy�>lna warto�>��                    | Wymagany (tryb Azure) | Sekret | Uwagi |
| ------------------------ | -------------------------------------- | --------------------- | ------ | ----- |
| `AZURE_CONNECTION_STRING` | _brak_                                | Tak                   | Tak    | Ci�g po�'�czenia do Azure Blob; niepotrzebny, gdy `PREDICTIONS_SOURCE=local`. |
| `AZURE_CONTAINER_NAME`  | _brak_                                  | Tak                   | Nie    | Nazwa kontenera Azure Blob; w `.env.example` sugerowana warto�>�� `football-data`. |
| `FOOTBALL_DATA_URL`     | `https://www.football-data.co.uk`       | Nie                   | Nie    | Bazowy URL do surowych CSV z terminarzami/wynikami. |
| `FOOTBALL_DATA_TABLE`   | `mmz4281`                               | Nie                   | Nie    | Fragment �>cie��ki dla historycznych wynikƈw na football-data.co.uk. |
| `PREDICTED_FPATH`       | `static/predicted.txt`                  | Nie                   | Nie    | Lokalna �>cie��ka u�>ywana przez niektƈre skrypty do statusu predykcji. |
| `PREDICTIONS_SOURCE`    | `azure`                                 | Nie                   | Nie    | `azure` ��>czyta predykcje z Blob, `local` korzysta z lokalnego pliku Parquet. |
| `PREDICTIONS_LOCAL_PATH`| `data/predictions_valid.parquet`        | Nie                   | Nie    | Lokalna �>cie��ka do pliku Parquet z predykcjami przy `PREDICTIONS_SOURCE=local`. |

### 3.1 Praca tylko lokalnie (bez Azure)
Dla osƈb, ktƈre nie maj� dost�tp do konta Azure:
- Mo��na wci��z skonfigurowa�� �>rodowisko, zainstalowa�� zale��no�>ci i przegl�da�� kod oraz notebook lokalnie.
- Uruchamianie `train.ipynb` dzia�'a wy�'�cznie na Twoim komputerze; w razie potrzeby surowe CSV mo��na pobra�� r�cznie z football-data.co.uk.
- Mo��esz uruchomi�� dashboard Streamlit w **trybie offline**, je�>li masz lokalny plik Parquet z predykcjami:
  - Ustaw `PREDICTIONS_SOURCE=local` i wska�� plik w `PREDICTIONS_LOCAL_PATH` (np. `data/predictions_valid.parquet`).
  - W tym trybie mo��esz pozostawi�� `AZURE_CONNECTION_STRING` i `AZURE_CONTAINER_NAME` puste.
  - Dashboard odczyta predykcje z lokalnego pliku, ale `run_pipelines.py` i wszelkie operacje na Azure pozostaj� niedost�tpne bez Azure.

## 4. Cykl ��ycia danych
1. **Pozyskiwanie:** Surowe CSV z [football-data.co.uk](https://www.football-data.co.uk/).
2. **Cechy:** `src/preprocess/features.py` odtwarza statystyki sprzed meczu i wykorzystuje `LeagueTable` do agregacji krocz�cych.
3. **Magazyn:** Oczyszczone partycje zapisywane w Azure Blob poprzez `src/storage/tables.py`; du��e pliki parquet nie trafiaj� do repo.
4. **Predykcje:** `run_pipelines.py` tworzy partycj�t `valid`, ktƈr� czyta Streamlit; partycje train/test od�>wie��ane manualnie przed eksperymentami.

## 5. Modelowanie
- **Algorytm:** XGBoost radzi sobie z danymi tabelarycznymi i brakami pocz�tkƈw sezonu.
- **Hyperparametry:** `Hyperopt` w `src/modelling/experiment.py`; wyniki dokumentowane w `train.ipynb`.
- **Metryki:** Optymalizacja RMSE, a w UI pokazywane s� Accuracy i ROI.
- **Wyja�>nienia:** Modu�'y `src/explain/` wraz z SHAP zwracaj� wp�'yw ka��dej cechy.

## 6. Frontend Streamlit
- `src/frontend/data.py` przygotowuje dane do metryk i wykresƈw krocz�cych.
- `src/frontend/metrics.py` formatuje KPI oraz dashboard metryczny.
- `src/frontend/match_report.py` tworzy expandery `FixtureReport`/`ResultReport` z kursami, zwrotami i tabel� SHAP.
- Wskazƈwki a11y: zachowuj czytelne etykiety, do wykresƈw dodawaj opisy tekstowe i nie polegaj tylko na kolorach.

## 7. Wdro��enie i Operacje
1. **CI/CD:** GitHub Actions buduj� i wdra��aj� aplikacj�t na Azure App Service po pushu do `master`.
2. **App Service:** W portalu ustaw komend�t startow� uruchamiaj�c� `streamlit run app.py`.
3. **Harmonogram:** Maszyna wirtualna wykonuje cron (np. `0 0 * * 3,6 /usr/bin/python /home/site/wwwroot/run_pipelines.py`) aby od�>wie��a�� dane; u��ywaj �>cie��ek absolutnych.
4. **Monitoring:** Logi Streamlit dost�tpne w diagnostyce App Service; metryki Azure Blob potwierdzaj� �>wie��o�>�� danych.

## 8. Rozwi�zywanie problemƈw
| Problem | Rozwi�zanie |
| --- | --- |
| Puste tabelki w Streamlit | Sprawd�� zmienne `AZURE_*` i istnienie partycji `valid`. |
| B�'�tdy pipeline'u o brakuj�cych cechach | Uruchom preprocessing i potwierd�� zgodno�>�� schematu w `Config.FEATURES`. |
| Brak tabel SHAP | Zweryfikuj obecno�>�� kolumn SHAP i ponownie wytrenuj model po zmianie schematu. |
| Cron nie dzia�'a | Sprawd�� `crontab -l`, uprawnienia wykonywalne i ewentualnie zrestartuj VM. |

## 9. Dalsze kroki
- Automatyzacja treningu w Azure ML lub Synapse.
- Dodanie testƈw pytest w `tests/`.
- Zamiana cron na Event Grid + Functions.
- Udoskonalenie uk�'adu wielokolumnowego pod k�tem nawigacji klawiatur�.
