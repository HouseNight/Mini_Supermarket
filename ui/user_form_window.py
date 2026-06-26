from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from sieu_thi_mini_app.modules.auth_user_module import AuthUserModule
from sieu_thi_mini_app.ui.style import apply_default_style


class UserFormWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Widget,
        state: object,
        on_created: Callable[[], None] | None = None
    ) -> None:
        super().__init__(master)

        apply_default_style(self)

        self.state = state
        self.auth = AuthUserModule(self.state.db)
        self.on_created = on_created

        self.title("Tạo người dùng")
        self.minsize(720, 560)
        self._center_window(720, 560)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.fullname_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=24, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # ===== Tiêu đề =====
        header_frame = ttk.Frame(container, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        ttk.Label(
            header_frame,
            text="👤 Tạo người dùng",
            style="Header.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="Điền thông tin tài khoản mới vào biểu mẫu bên dưới.",
            style="Status.TLabel"
        ).pack(anchor="w", pady=(6, 0))

        # ===== Form nhập liệu =====
        form_frame = ttk.Frame(container, style="Card.TFrame")
        form_frame.grid(row=1, column=0, sticky="nsew")

        form_frame.columnconfigure(0, minsize=160)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Tên đăng nhập:").grid(
            row=0,
            column=0,
            sticky="w",
            pady=8
        )

        username_entry = ttk.Entry(
            form_frame,
            textvariable=self.username_var
        )
        username_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Mật khẩu:").grid(
            row=1,
            column=0,
            sticky="w",
            pady=8
        )

        password_entry = ttk.Entry(
            form_frame,
            textvariable=self.password_var,
            show="*"
        )
        password_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Họ tên:").grid(
            row=2,
            column=0,
            sticky="w",
            pady=8
        )

        ttk.Entry(
            form_frame,
            textvariable=self.fullname_var
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Email:").grid(
            row=3,
            column=0,
            sticky="w",
            pady=8
        )

        ttk.Entry(
            form_frame,
            textvariable=self.email_var
        ).grid(
            row=3,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Điện thoại:").grid(
            row=4,
            column=0,
            sticky="w",
            pady=8
        )

        ttk.Entry(
            form_frame,
            textvariable=self.phone_var
        ).grid(
            row=4,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Vai trò:").grid(
            row=5,
            column=0,
            sticky="w",
            pady=8
        )

        roles = [role["code"] for role in self.auth.list_roles()]
        self.role_var = tk.StringVar(value=roles[0] if roles else "ADMIN")

        ttk.Combobox(
            form_frame,
            textvariable=self.role_var,
            values=roles,
            state="readonly"
        ).grid(
            row=5,
            column=1,
            sticky="ew",
            pady=8
        )

        # Cho bấm Enter để tạo nhanh
        username_entry.focus_set()
        self.bind("<Return>", lambda _event: self._create())

        # ===== Nút thao tác =====
        button_frame = ttk.Frame(container, style="Card.TFrame")
        button_frame.grid(row=2, column=0, sticky="ew", pady=(24, 0))

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(
            button_frame,
            text="✅ Tạo",
            style="Accent.TButton",
            command=self._create
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8),
            ipady=4
        )

        ttk.Button(
            button_frame,
            text="❌ Hủy",
            style="Danger.TButton",
            command=self.destroy
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(8, 0),
            ipady=4
        )

    def _create(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get()
        fullname = self.fullname_var.get().strip()
        email = self.email_var.get().strip() or None
        phone = self.phone_var.get().strip() or None
        role_code = self.role_var.get().strip()

        if not username:
            messagebox.showerror("Lỗi", "Tên đăng nhập không được để trống.")
            return

        if not password:
            messagebox.showerror("Lỗi", "Mật khẩu không được để trống.")
            return

        if not fullname:
            messagebox.showerror("Lỗi", "Họ tên không được để trống.")
            return

        if not role_code:
            messagebox.showerror("Lỗi", "Vui lòng chọn vai trò.")
            return

        try:
            user_id = self.auth.create_user(
                username=username,
                password=password,
                full_name=fullname,
                email=email,
                phone=phone,
                role_code=role_code
            )

            messagebox.showinfo(
                "Thành công",
                f"Người dùng {username} đã được tạo."
            )

            if callable(self.on_created):
                self.on_created()

            self.destroy()

        except Exception as exc:
            messagebox.showerror("Lỗi tạo người dùng", str(exc))

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)

        self.geometry(f"{width}x{height}+{x}+{y}")