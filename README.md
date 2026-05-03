# Phoenix Livestock Investment Management System (Tkinter + MySQL)

A small, beginner-friendly version of your project idea:
- Login with role-based panel (admin / manager / investor)
- Investor can request deposit
- Manager can add daily cost (deducts from wallet)
- Admin can approve deposits
- Admin can also view manager daily cost history and summary

## 1) Windows setup

### Install Python

Install Python 3.10+ from the official website and make sure `python` or `py` works in Command Prompt / PowerShell.

### Install MySQL

Install MySQL Server and start the service. Create a database for this project in the next step.

### Create virtual environment

Open PowerShell or Command Prompt in this folder and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If PowerShell blocks activation, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 1b) Linux setup

### Install Python

Install Python 3.10+ from your package manager and make sure `python3` works in Terminal.

### Install MySQL

Install MySQL Server and start the service. Create a database for this project in the next step.

### Create virtual environment

Open Terminal in this folder and run:

```bash
python3 -m venv .venv
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

On Linux, you can also run:

```bash
python3 app.py
```

## GitHub update

After making changes locally, update GitHub with:

```bash
git add README.md
git commit -m "Update README with Windows setup"
git push origin main
```

If your default branch is not `main`, replace it with your branch name.

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
