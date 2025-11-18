# Szybki start �?" Football Prediction Web App

Poni��szy poradnik jest skierowany do osƈb nietechnicznych. Ka��de zadanie zosta�'o uproszczone do jednego polecenia albo gotowego skryptu.

## 1. Co b�tdzie potrzebne
1. **Popro�> w�'a�>ciciela projektu** o dost�tp do repozytorium GitHub oraz kontenera Azure Blob.
2. **Zainstaluj Python 3.9+** ze strony [python.org](https://www.python.org/downloads/). W instalatorze zaznacz opcj�t �?�Add Python to PATH�?�.
3. **Pobierz ZIP z projektem** (zielony przycisk �?�Code�?� ��' �?�Download ZIP�?�), a nast�tpnie rozpakuj go np. do `Dokumenty\football-prediction-web-app-forked`.

## 2. Dodaj sekrety (jednorazowo)
1. Otwƈrz **Windows Terminal ��' PowerShell**.
2. Przejd�� do folderu projektu jedn� komend� (zmie�" �>cie��k�t, je�>li trzeba):
   ```
   cd "%USERPROFILE%\Documents\football-prediction-web-app-forked"
   ```
3. Utwƈrz w�'asny plik ustawieu z szablonu:
   ```
   copy .env.example .env
   ```
4. Otwƈrz go do edycji:
   ```
   notepad .env
   ```
5. Wklej ci�g po�'�czenia otrzymany od w�'a�>ciciela (albo zaktualizuj warto�>ci zast�tp�):
   ```
   AZURE_CONNECTION_STRING=wklej_warto�>��
   AZURE_CONTAINER_NAME=football-data
   ```
   Mo�>esz te�� nadpisa�� opcjonalne ustawieu, je�>li kto�> Ci�t o to poprosi (typowy u��ytkownik nie musi tego robi��):
   ```
   FOOTBALL_DATA_URL=https://www.football-data.co.uk
   FOOTBALL_DATA_TABLE=mmz4281
   PREDICTED_FPATH=static/predicted.txt
   ```
   Zapisz plik i zamknij Notatnik. Ten plik zostaje wy�'�cznie na Twoim komputerze.

## 3. Uruchom dashboard (jedno polecenie)
1. W tym samym oknie PowerShell wpisz:
   ```
   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"
   ```
   Skrypt sam stworzy �>rodowisko, doinstaluje pakiety i w�'�czy Streamlit.
2. Poczekaj, a�� otworzy si�t karta w przegl�darce. Wybierz ligi, przejrzyj metryki i raporty meczowe.
3. Po zako�"czeniu wrƈ�� do PowerShell i wci�>nij `Ctrl+C`, aby zatrzyma�� aplikacj�t.

> **Wskazƈwka:** Gdyby Windows zablokowa�' skrypt, uruchom `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, a nast�tpnie ponƈw powy��sze polecenie.

## 4. Od�>wie�� predykcje (jedno polecenie, opcjonalnie)
Tylko na pro�>b�t w�'a�>ciciela projektu uruchom:
```
powershell -ExecutionPolicy Bypass -File ".\scripts\refresh-predictions.ps1"
```
Skrypt upewni si�t, ��e zale��no�>ci s� gotowe, pobierze najnowsze dane i zaktualizuje metryki w Azure.

## 4a. Uruchamianie bez Azure (tylko lokalnie)
Je�>li **nie masz** dost�tp do konta Azure, masz dwie mo�>liwo�>ci:

1. **Praca lokalna bez danych dashboardu**
   - Sklonuj repozytorium, stw�'rz �>rodowisko wirtualne i zainstaluj zale��no�>ci.
   - Otwƈrz i uruchamiaj notebook badawczy lokalnie:
     - `python -m venv .venv`, aktywacja, `pip install -r requirements.txt`
     - `jupyter notebook train.ipynb`

2. **Dashboard offline z lokalnym plikiem predykcji**
   - Zdob�d� plik Parquet z predykcjami (np. `data/predictions_valid.parquet`) od osoby, kt�'ra uruchomi�'a pipeline'y.
   - W `.env` ustaw:
     ```text
     PREDICTIONS_SOURCE=local
     PREDICTIONS_LOCAL_PATH=data/predictions_valid.parquet
     ```
   - W tym trybie mo��esz pomin�� `AZURE_CONNECTION_STRING` i `AZURE_CONTAINER_NAME`, ale:
     - Skrypt od�>wie��aj�cy (`refresh-predictions.ps1`) i `run_pipelines.py` **nie** zadzia�'aj� bez Azure.
   - Nast�tpnie uruchom:
     ```powershell
     powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"
     ```
     Dashboard odczyta predykcje z lokalnego pliku Parquet zamiast z Azure.

## 5. B�'yskawiczna �>ci�ga
- `copy .env.example .env` ��' `notepad .env` ��' wklej sekrety ��' zapisz.
- `powershell -ExecutionPolicy Bypass -File ".\scripts\setup-and-launch.ps1"` ��' dashboard.
- `powershell -ExecutionPolicy Bypass -File ".\scripts\refresh-predictions.ps1"` ��' aktualizacja danych.

## Potrzebna pomoc?
- **Niepoprawny ci�g po�'�czenia:** ponownie otwƈrz plik `notepad .env` i usu�" zb�tdne spacje.
- **Windows blokuje skrypt:** wykonaj `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` w PowerShell i sprƈbuj jeszcze raz.
- **Pusta karta Streamlit:** upewnij si�t, ��e konsola ze skryptem nadal dzia�'a; je�>li nie, uruchom ponownie krok 3.
- **B�'�d podczas od�>wie��ania:** skopiuj czerwony komunikat z konsoli i przeka�� go zespo�'owi technicznemu.
