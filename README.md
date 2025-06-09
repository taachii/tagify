# Tagify – Aplikacja do klasyfikacji zdjęć

Tagify to webowa aplikacja oparta na Flasku, umożliwiająca zarządzanie zdjęciami i automatyczną klasyfikację obrazów za pomocą modeli uczenia głębokiego (np. ResNet50, EfficientNet).

---

## Funkcje

- Rejestracja i logowanie użytkowników
- Obsługa ról: `regular` / `pro` / `admin`
- Klasyfikacja zdjęć z użyciem modeli ML (w toku)
- Ulepszanie konta do wersji PRO (placeholder)
- Dostęp tylko dla zalogowanych użytkowników

---

## Jak uruchomić projekt lokalnie

### Krok 1: Utwórz i aktywuj wirtualne środowisko

#### Windows (CMD/Powershell)

```Powershell
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
flask db init # tylko raz!
flask db migrate
flask db upgrade
```

### Krok 4: Uruchom aplikację

```bash
python run.py
```

Aplikacja będzie dostępna pod adresem:
👉 http://127.0.0.1:5000

---

## Struktura projektu

project/
├── app/
│   ├── auth/            # logowanie, rejestracja
│   ├── core/            # strona główna, pro
│   ├── static/          # style CSS
│   ├── templates/       # base.html
│   ├── models.py        # definicja modelu User
│   └── __init__.py      # konfiguracja aplikacji
├── instance/            # lokalna baza danych SQLite
├── run.py               # punkt startowy aplikacji
├── requirements.txt     # zależności
└── README.md

---

## Wymagania

- Python 3.9+
- Flask
- Flask-WTF
- Flask-Login
- Flask-Migrate
- SQLAlchemy
- email-validator

---

## Licencja

Projekt powstał jako część pracy inżynierskiej.
Można go swobodnie rozwijać i adaptować do celów edukacyjnych.