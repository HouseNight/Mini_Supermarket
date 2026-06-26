from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from sieu_thi_mini_app.database.db import Database
from sieu_thi_mini_app.modules.auth_user_module import AuthUserModule
from sieu_thi_mini_app.ui.main_window import MainWindow
from sieu_thi_mini_app.ui.style import apply_default_style
from sieu_thi_mini_app.utils.constants import APP_NAME


class AppState:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.auth = AuthUserModule(db)
        self.current_user: dict[str, object] | None = None


class LoginWindow(tk.Tk):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.title(f"Đăng nhập - {APP_NAME}")
        self.resizable(False, False)
        apply_default_style(self)
        self._center_window(460, 320)
        self.protocol("WM_DELETE_WINDOW", self._exit_app)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=24, style="Card.TFrame")
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)

        ttk.Label(container, text="🏪 " + APP_NAME, style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        ttk.Label(container, text="✅ Đăng nhập để quản lý siêu thị", style="Status.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))

        ttk.Label(container, text="👤 Tên đăng nhập", style="CardTitle.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        username_entry = ttk.Entry(container, textvariable=self.username_var)
        username_entry.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(container, text="🔐 Mật khẩu", style="CardTitle.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        password_entry = ttk.Entry(container, textvariable=self.password_var, show="*")
        password_entry.grid(row=3, column=1, sticky="ew", pady=6)
        password_entry.bind("<Return>", lambda _event: self._login())

        button_frame = ttk.Frame(container)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        button_frame.columnconfigure(0, weight=1)
        ttk.Button(button_frame, text="✅ Đăng nhập", style="Accent.TButton", command=self._login).grid(row=0, column=0, sticky="ew")

        username_entry.focus_set()

    def _login(self) -> None:
        try:
            username = self.username_var.get().strip()
            password = self.password_var.get()
            self.state.current_user = self.state.auth.login(username, password)
        except Exception as exc:
            messagebox.showerror("Đăng nhập thất bại", str(exc))
            return
        self.password_var.set("")
        self.withdraw()
        MainWindow(self, self.state, on_logout=self._show_login, on_exit=self._exit_app)

    def _show_login(self) -> None:
        self.state.current_user = None
        self.deiconify()
        self.lift()

    def _exit_app(self) -> None:
        try:
            self.state.db.close()
        finally:
            self.destroy()

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")

