# Szybki start – Football Prediction Web App

Ten poradnik jest skierowany do osób nietechnicznych. Każde zadanie zostało uproszczone do jednego polecenia albo gotowego skryptu.

## 1. Co będzie potrzebne
- Dostęp do repozytorium GitHub (ZIP z kodem) lub klona Git.
- Zainstalowany Python 3.9+ ze strony [python.org](https://www.python.org/downloads/) (w instalatorze zaznacz „Add Python to PATH”).
- (Opcjonalnie) dostęp do kontenera Azure Blob – **nie jest wymagany**, jeśli chcesz pracować tylko lokalnie, patrz sekcja „4a. Uruchamianie bez Azure”.

## 2. Dodaj plik `.env`
1. Otwórz **Windows Terminal lub PowerShell**.
2. Przejdź do folderu projektu (dostosuj ścieżkę, jeśli trzeba):
   ```powershell
   cd "$env:USERPROFILE\Documents\football-prediction-web-app-forked"
   ```
3. Skopiuj przykładowy plik konfiguracyjny:
   ```powershell
   copy .env.example .env
   ```
4. Otwórz go do edycji:
   ```powershell
   notepad .env
   ```
5. W zależności od trybu pracy:
   - **Z Azure (domyślnie)** – ustaw wartości podane przez właściciela projektu:
     ```text
     AZURE_CONNECTION_STRING=...
     AZURE_CONTAINER_NAME=football-data
     ```
   - **Bez Azure, tylko lokalnie** – możesz **pozostawić** `AZURE_CONNECTION_STRING` i `AZURE_CONTAINER_NAME` puste lub zakomentowane i skonfigurować tryb lokalny (szczegóły w sekcji 4a).

Zapisz plik i zamknij Notatnik. Ten plik jest lokalny, nie trafia do repozytorium.

## 3. Uruchom dashboard (jedno polecenie)
1. W tym samym oknie PowerShell wpisz:
   ```powershell
   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"
   ```
   Skrypt sam stworzy środowisko, zainstaluje pakiety i uruchomi Streamlit.
2. Poczekaj, aż otworzy się karta w przeglądarce. Wybierz ligi, przejrzyj metryki i raporty meczowe.
3. Po zakończeniu wróć do PowerShell i wciśnij `Ctrl+C`, aby zatrzymać aplikację.

> **Wskazówka:** Gdyby Windows zablokował skrypt, uruchom:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> a następnie ponownie:
> ```powershell
> powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"
> ```

## 4. Odśwież predykcje (opcjonalnie, wymaga Azure)
Tylko na prośbę właściciela projektu uruchom:
```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\refresh-predictions.ps1"
```
Skrypt upewni się, że zależności są gotowe, pobierze najnowsze dane i zaktualizuje metryki w Azure.

## 4a. Uruchamianie bez Azure (w pełni lokalnie)
Jeśli **nie masz** dostępu do konta Azure albo chcesz pracować tylko lokalnie, masz dwie możliwości.

### 4a.1. Praca lokalna bez dashboardu
- Sklonuj repozytorium lub rozpakuj ZIP.
- Utwórz środowisko wirtualne i zainstaluj zależności:
  ```powershell
  cd "$env:USERPROFILE\Documents\football-prediction-web-app-forked"
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- Uruchamiaj notebook badawczy lokalnie:
  ```powershell
  jupyter notebook train.ipynb
  ```

### 4a.2. Dashboard offline z lokalnym plikiem predykcji (pełny tryb lokalny)
W tym trybie dashboard działa normalnie, ale zamiast Azure czyta predykcje z lokalnego pliku Parquet.

1. **Przygotuj plik z predykcjami**
   - Zdobądź plik Parquet z predykcjami (np. `data/predictions_valid.parquet`) od osoby, która uruchomiła pipeline’y **albo** wygeneruj go lokalnie (np. osobnym skryptem/notebookiem).
   - Umieść plik w katalogu projektu, np. w `data/predictions_valid.parquet`.

2. **Skonfiguruj `.env` pod tryb lokalny**
   - Upewnij się, że plik `.env` istnieje (patrz sekcja 2):
     ```powershell
     copy .env.example .env   # jeśli jeszcze nie istnieje
     notepad .env
     ```
   - W pliku `.env`:
     - Możesz **usunąć lub pozostawić puste** wpisy:
       ```text
       AZURE_CONNECTION_STRING=
       AZURE_CONTAINER_NAME=
       ```
     - Dodaj/ustaw zmienne odpowiedzialne za tryb lokalny:
       ```text
       PREDICTIONS_SOURCE=local
       PREDICTIONS_LOCAL_PATH=data/predictions_valid.parquet
       ```

3. **Uruchom dashboard bez Azure**
   W PowerShell w katalogu projektu wpisz:
   ```powershell
   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"
   ```
   Dashboard odczyta predykcje z lokalnego pliku Parquet zamiast z Azure. Żadne połączenie z chmurą nie jest wymagane.

> Uwaga: w trybie lokalnym **nie działają**:
> - skrypt `scripts\refresh-predictions.ps1`,
> - komenda `python run_pipelines.py` (odświeżanie danych nadal jest zaprojektowane pod Azure).

## 5. Błyskawiczna ściąga
- `copy .env.example .env` → `notepad .env` → uzupełnij konfigurację.
- `powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"` → uruchom dashboard.
- (Opcjonalnie, tylko z Azure) `powershell -ExecutionPolicy Bypass -File ".\scripts\refresh-predictions.ps1"` → odśwież dane.

## Potrzebna pomoc?
- **Dashboard nie startuje:** sprawdź, czy `setup-and-launch.ps1` nie zakończył się błędem w konsoli.
- **Błąd pliku Parquet w trybie lokalnym:** upewnij się, że ścieżka w `PREDICTIONS_LOCAL_PATH` jest poprawna i plik istnieje.
- **Windows blokuje skrypt:** wykonaj `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` w PowerShell i spróbuj jeszcze raz.
