![alt text](https://github.com/taachii/tagify/tree/main/app/static/img/favicon.ico)
# Tagify – Aplikacja do klasyfikacji zdjęć

Tagify to webowa aplikacja oparta na Flasku, umożliwiająca zarządzanie zdjęciami i automatyczną klasyfikację obrazów za pomocą modeli uczenia głębokiego (ResNet50, EfficientNet).

---

## Funkcje

- Rejestracja i logowanie użytkowników
- Obsługa ról: `admin`, `regular`, `researcher`
- Przesyłanie plików ZIP ze zdjęciami do automatycznej klasyfikacji
- Wybór modelu klasyfikacyjnego (tylko dla roli `researcher`)
- Korekta wyników klasyfikacji i generowanie ZIP-a z wynikami
- Historia klasyfikacji i możliwość usuwania wyników
- Panel administratora do zarządzania użytkownikami (aktywacja, dezaktywacja, edycja, usuwanie)
- Panel badacza do przeglądania statystyk modeli (dokładność, strata, czasy epok)
- Mechanizm wygasania wyników po 24h oraz automatyczne czyszczenie plików tymczasowych
- System powiadomień (toast i alerty) z rozróżnieniem typów wiadomości

---

## Jak uruchomić projekt lokalnie

### Krok 1: Utwórz i aktywuj wirtualne środowisko

#### Windows (CMD/Powershell)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS (bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Krok 2: Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### Krok 3: Utwórz bazę danych

```bash
flask db init       # tylko przy pierwszym uruchomieniu
flask db migrate
flask db upgrade
```

### Krok 4: Uruchom aplikację

```bash
python run.py
```

Aplikacja będzie dostępna pod adresem:
👉 http://127.0.0.1:5005

---

## Struktura projektu

```markdown
tagify
├── app/
│   ├── blueprints/
│   │   ├── admin/            # panel administratora
│   │   ├── auth/             # logowanie, rejestracja
│   │   ├── core/             # strona główna
│   │   ├── researcher/       # panel badacza, statystyki modeli
│   │   └── user/             # panel użytkownika, klasyfikacja
│   ├── models.py             # definicje modeli bazy danych (User, Classification)
│   ├── static/               # statyczne pliki CSS, JS, obrazy
│   ├── templates/            # szablony Jinja2 (layouty, strony)
│   ├── utils/                # moduły pomocnicze (klasyfikacja, wygasanie)
│   └── __init__.py           # konfiguracja aplikacji Flask
├── instance/                 # baza danych SQLite i przechowywanie plików tymczasowych
├── migrations/               # pliki migracji bazy danych (Alembic)
├── models/                   # wytrenowane modele TensorFlow (.keras, history.json)
├── requirements.txt          # zależności projektu
├── run.py                    # punkt startowy aplikacji
└── README.md                 # dokumentacja (ten plik)
```
---

## Wymagania

- Python 3.11 lub nowszy
- Flask i rozszerzenia Flask-Login, Flask-Migrate, Flask-WTF
- SQLAlchemy
- Flask-Login
- TensorFlow 2.19.0
- Przeglądarka z obsługą JavaScript

### Pełna lista wymagań znajduje się w pliku `requirements.txt`

---

## Obsługa modeli i klasyfikacji

- Modele klasyfikacyjne (ResNet50, EfficientNetB0) są przechowywane w katalogu models/ (nieobecnym w repozytorium z powodu rozmiarów przekraczających limit GitHuba). Katalog ten można pobrać stąd: [Pobierz modele](https://drive.google.com/file/d/1oCxJwgCrE8KPWXaneOL-c8RcYEZX39EZ/view?usp=sharing)
- Użytkownicy mogą przesyłać pliki ZIP ze zdjęciami do klasyfikacji
- Przykładowe foldery ze zdjęciami do testów można pobrać tutaj:
  - [Zbiór testowy - test.zip](https://drive.google.com/file/d/1aOf9k2RgLTpbgGOtubV49oaIX_9j8kJI/view?usp=sharing)
  - [Zbiór testowy - test_3classes.zip](https://drive.google.com/file/d/1IBPYxqoIYH8dRT2jPWJv1nRuQMJ-Mwi7/view?usp=sharing)
- Wyniki klasyfikacji są prezentowane z wizualnym podkreśleniem pewności predykcji
- Użytkownik może ręcznie poprawić klasyfikację dla poszczególnych zdjęć, również może wskazać klasę "others" przy zdjęciach niepasujących do żadnej z dostępnych klas
- Po zatwierdzeniu wyników generowany jest plik ZIP z posegregowanymi zdjęciami wg poprawionych klas

---

## Panel administratora

- Zarządzanie użytkownikami (edycja, dezaktywacja, aktywacja, usuwanie)
- Przegladanie listy użytkowników z paginacją, lazy loadingiem oraz filtrowaniem po nazwie

---

## Panel badacza (researcher)

- Możliwość wyboru modelu spośród dostępnych do klasyfikacji
- Podgląd szczegółowych statystyk treningu: dokładność, strata, czas epoki itp
- Wizualizacja wykresów accuracy i loss

---

## Notyfikacje i komunikaty

- Toasty: krótkie informacje typu success i info - znikają automatycznie
- Alerty: ważne komunikaty typu danger i warning - widoczne stale
- Formularze walidują dnae i wyświetlają błędy przy polach

---

## Plany na przyszłość

- Możliwość integracji z chmurą MEGA dla przechowywania i synchronizacji zdjęć (obecnie odłożone)
- Internaconalizacja i wsparcie dla wielu języków

---

## Licencja

Projekt powstał jako część pracy inżynierskiej.
Można go swobodnie rozwijać i adaptować do celów edukacyjnych.

---

## Autor
Adam Chyt
Uniwersytet Śląski, Wydział Nauk Ścisłych i Technicznych
2025
