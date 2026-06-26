from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from sieu_thi_mini_app.modules.warehouse_module import WarehouseModule

try:
    from sieu_thi_mini_app.ui.style import apply_default_style
except Exception:
    apply_default_style = None


class SupplierFormWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Widget,
        state: object,
        on_created: Callable[[], None] | None = None
    ) -> None:
        super().__init__(master)

        if apply_default_style:
            apply_default_style(self)

        self.state = state
        self.warehouse = WarehouseModule(self.state.db)
        self.on_created = on_created

        self.title("Tạo nhà cung cấp")
        self.resizable(False, False)
        self._center_window(560, 420)

        self.code_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="🏢 Tạo nhà cung cấp",
            font=("Segoe UI", 15, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        subtitle = ttk.Label(
            container,
            text="Nhập thông tin nhà cung cấp mới",
            foreground="#555"
        )
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

        container.columnconfigure(0, minsize=130)
        container.columnconfigure(1, weight=1, minsize=340)

        ttk.Label(container, text="Mã nhà cung cấp:").grid(
            row=2, column=0, sticky="w", pady=8
        )
        ttk.Entry(container, textvariable=self.code_var).grid(
            row=2, column=1, sticky="ew", pady=8
        )

        ttk.Label(container, text="Tên:").grid(
            row=3, column=0, sticky="w", pady=8
        )
        ttk.Entry(container, textvariable=self.name_var).grid(
            row=3, column=1, sticky="ew", pady=8
        )

        ttk.Label(container, text="Điện thoại:").grid(
            row=4, column=0, sticky="w", pady=8
        )
        ttk.Entry(container, textvariable=self.phone_var).grid(
            row=4, column=1, sticky="ew", pady=8
        )

        ttk.Label(container, text="Email:").grid(
            row=5, column=0, sticky="w", pady=8
        )
        ttk.Entry(container, textvariable=self.email_var).grid(
            row=5, column=1, sticky="ew", pady=8
        )

        ttk.Label(container, text="Địa chỉ:").grid(
            row=6, column=0, sticky="w", pady=8
        )
        ttk.Entry(container, textvariable=self.address_var).grid(
            row=6, column=1, sticky="ew", pady=8
        )

        button_frame = ttk.Frame(container)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(24, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(
            button_frame,
            text="Tạo",
            command=self._create
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            button_frame,
            text="Hủy",
            command=self.destroy
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _create(self) -> None:
        code = self.code_var.get().strip()
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip() or None
        email = self.email_var.get().strip() or None
        address = self.address_var.get().strip() or None

        if not code:
            messagebox.showerror("Lỗi", "Mã nhà cung cấp không được để trống.")
            return

        if not name:
            messagebox.showerror("Lỗi", "Tên nhà cung cấp không được để trống.")
            return

        try:
            supplier_id = self.warehouse.create_supplier(
                code=code,
                name=name,
                phone=phone,
                email=email,
                address=address
            )

            messagebox.showinfo(
                "Thành công",
                f"Đã tạo nhà cung cấp {name}."
            )

            if callable(self.on_created):
                self.on_created()

            self.destroy()

        except Exception as exc:
            messagebox.showerror("Lỗi tạo nhà cung cấp", str(exc))

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)

        self.geometry(f"{width}x{height}+{x}+{y}")