# Phoenix Basic Easy Version (Tkinter + MySQL)

A small, beginner-friendly version of your project idea:
- Login with role-based panel (admin / manager / investor)
- Investor can request deposit
- Manager can add daily cost (deducts from wallet)
- Admin can approve deposits
- Admin can also view manager daily cost history and summary

## 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Create MySQL DB

```sql
CREATE DATABASE IF NOT EXISTS phoenix_basic;
```

## 3) Update DB credentials

Open `config.py` and change:
- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

## 4) Run

```bash
python app.py
```

## Demo users

- admin / 1234
- manager / 1234
- investor / 1234

## File Structure

- `app.py` -> entry point
- `config.py` -> DB settings
- `db.py` -> all MySQL queries and methods
- `ui.py` -> login/signup and role routing
- `admin_panel.py` -> admin part
- `manager_panel.py` -> manager part
- `investor_panel.py` -> investor part
