from __future__ import annotations

from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sieu_thi_mini_app.database.db import Database
from sieu_thi_mini_app.ui.login_window import AppState, LoginWindow


def main() -> None:
    db = Database.from_default_path()
    db.initialize()
    state = AppState(db)
    app = LoginWindow(state)
    app.mainloop()


if __name__ == "__main__":
    main()
