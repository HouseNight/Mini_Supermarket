from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from sieu_thi_mini_app.ui.style import apply_default_style


class AuditWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget, db: object) -> None:
        super().__init__(master)
        apply_default_style(self)
        self.db = db
        self.title("Nhật ký hoạt động")
        self.minsize(760, 420)
        self._center_window(780, 440)
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=16, style="Card.TFrame")
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Nhật ký hoạt động", style="Header.TLabel").pack(anchor="w")
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(8, 12))
        self.tree = ttk.Treeview(frame, columns=("created_at", "user", "action", "entity", "desc"), show="headings")
        for col, title in [("created_at", "Ngày"), ("user", "Người"), ("action", "Hành động"), ("entity", "Thực thể"), ("desc", "Mô tả")]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=140)
        self.tree.pack(fill="both", expand=True, pady=(8, 0))

    def _load(self) -> None:
        rows = self.db.fetch_all(
            "SELECT a.created_at, u.username AS user, a.action, a.entity_type || ':' || IFNULL(a.entity_id, '') AS entity, a.description FROM audit_logs a LEFT JOIN users u ON u.id = a.user_id ORDER BY a.created_at DESC LIMIT 200"
        )
        for row in rows:
            self.tree.insert("", "end", values=(row["created_at"], row["user"] or "system", row["action"], row["entity"], row["description"]))

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")
