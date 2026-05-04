import sys
import os
from pathlib import Path
from tkinter import messagebox


def _find_project_python(app_path: Path) -> Path | None:
    """Return project venv Python if available, otherwise None."""
    project_root = app_path.parent
    candidates = [
        project_root / ".venv" / "bin" / "python",
        project_root / "my_env" / "bin" / "python",
        project_root / "venv" / "bin" / "python",
    ]
    for python_path in candidates:
        if python_path.exists():
            return python_path
    return None


def _ensure_project_venv_python():
    app_path = Path(__file__).resolve()
    project_python = _find_project_python(app_path)
    if project_python is None:
        return

    active_python = Path(sys.executable).resolve()
    if active_python == project_python.resolve():
        return

    os.execv(str(project_python), [str(project_python), str(app_path)])


if __name__ == "__main__":
    _ensure_project_venv_python()
    try:
        from db import DB
        from ui import App

        db = DB()
    except ModuleNotFoundError as exc:
        print(f"Missing dependency: {exc}. Run: {sys.executable} -m pip install mysql-connector-python")
        raise SystemExit(1)
    except Exception as exc:
        messagebox.showerror("DB Error", f"Cannot connect DB: {exc}")
        raise SystemExit(1)

    app = App(db)
    app.mainloop()
