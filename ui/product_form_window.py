from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from sieu_thi_mini_app.modules.product_module import ProductModule
from sieu_thi_mini_app.ui.style import apply_default_style


class ProductFormWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Widget,
        state: object,
        *,
        on_created: Callable[[], None] | None = None
    ) -> None:
        super().__init__(master)

        apply_default_style(self)

        self.state = state
        self.on_created = on_created
        self.product = ProductModule(self.state.db)

        self.title("Tạo sản phẩm")
        self.resizable(False, False)
        self._center_window(680, 580)

        self.sku_var = tk.StringVar()
        self.barcode_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="cai")
        self.cost_var = tk.StringVar()
        self.sale_var = tk.StringVar()
        self.min_stock_var = tk.StringVar(value="0")
        self.category_var = tk.StringVar()

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
            text="📦 Tạo sản phẩm",
            style="Header.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="Nhập thông tin sản phẩm bên dưới.",
            style="Status.TLabel"
        ).pack(anchor="w", pady=(6, 0))

        # ===== Form nhập liệu =====
        form_frame = ttk.Frame(container, style="Card.TFrame")
        form_frame.grid(row=1, column=0, sticky="nsew")

        form_frame.columnconfigure(0, minsize=150)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="SKU:").grid(
            row=0,
            column=0,
            sticky="w",
            pady=8
        )

        self.sku_entry = ttk.Entry(
            form_frame,
            textvariable=self.sku_var
        )
        self.sku_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Barcode:").grid(
            row=1,
            column=0,
            sticky="w",
            pady=8
        )

        self.barcode_entry = ttk.Entry(
            form_frame,
            textvariable=self.barcode_var
        )
        self.barcode_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Tên sản phẩm:").grid(
            row=2,
            column=0,
            sticky="w",
            pady=8
        )

        self.name_entry = ttk.Entry(
            form_frame,
            textvariable=self.name_var
        )
        self.name_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Danh mục:").grid(
            row=3,
            column=0,
            sticky="w",
            pady=8
        )

        categories = self.product.list_categories()
        self.category_values = [
            f"{category['id']} - {category['name']}"
            for category in categories
        ]

        self.cat_cb = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            values=self.category_values,
            state="readonly"
        )
        self.cat_cb.grid(
            row=3,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Đơn vị:").grid(
            row=4,
            column=0,
            sticky="w",
            pady=8
        )

        self.unit_entry = ttk.Entry(
            form_frame,
            textvariable=self.unit_var
        )
        self.unit_entry.grid(
            row=4,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Giá vốn:").grid(
            row=5,
            column=0,
            sticky="w",
            pady=8
        )

        self.cost_entry = ttk.Entry(
            form_frame,
            textvariable=self.cost_var
        )
        self.cost_entry.grid(
            row=5,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Giá bán:").grid(
            row=6,
            column=0,
            sticky="w",
            pady=8
        )

        self.sale_entry = ttk.Entry(
            form_frame,
            textvariable=self.sale_var
        )
        self.sale_entry.grid(
            row=6,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(form_frame, text="Tồn tối thiểu:").grid(
            row=7,
            column=0,
            sticky="w",
            pady=8
        )

        self.min_entry = ttk.Entry(
            form_frame,
            textvariable=self.min_stock_var
        )
        self.min_entry.grid(
            row=7,
            column=1,
            sticky="ew",
            pady=8
        )

        # ===== Nút thao tác =====
        button_frame = ttk.Frame(container, style="Card.TFrame")
        button_frame.grid(row=2, column=0, sticky="ew", pady=(24, 0))

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(
            button_frame,
            text="✅ Tạo",
            style="Accent.TButton",
            command=self._submit
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

        self.sku_entry.focus_set()
        self.bind("<Return>", lambda _event: self._submit())

    def _submit(self) -> None:
        sku = self.sku_var.get().strip()
        barcode = self.barcode_var.get().strip() or None
        name = self.name_var.get().strip()
        category_raw = self.category_var.get().strip()
        unit = self.unit_var.get().strip() or "cai"
        cost_raw = self.cost_var.get().strip()
        sale_raw = self.sale_var.get().strip()
        min_stock_raw = self.min_stock_var.get().strip()

        if not sku:
            messagebox.showerror("Lỗi", "SKU không được để trống.")
            return

        if not name:
            messagebox.showerror("Lỗi", "Tên sản phẩm không được để trống.")
            return

        if not category_raw:
            messagebox.showerror("Lỗi", "Vui lòng chọn danh mục.")
            return

        try:
            category_id = int(category_raw.split("-")[0].strip())
        except Exception:
            messagebox.showerror("Lỗi", "Danh mục không hợp lệ.")
            return

        try:
            cost_price = float(cost_raw or 0)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá vốn phải là số hợp lệ.")
            return

        try:
            sale_price = float(sale_raw or 0)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá bán phải là số hợp lệ.")
            return

        try:
            min_stock = int(min_stock_raw or 0)
        except ValueError:
            messagebox.showerror("Lỗi", "Tồn tối thiểu phải là số nguyên.")
            return

        if cost_price < 0:
            messagebox.showerror("Lỗi", "Giá vốn không được âm.")
            return

        if sale_price < 0:
            messagebox.showerror("Lỗi", "Giá bán không được âm.")
            return

        if min_stock < 0:
            messagebox.showerror("Lỗi", "Tồn tối thiểu không được âm.")
            return

        try:
            product_id = self.product.create_product(
                sku=sku,
                barcode=barcode,
                name=name,
                category_id=category_id,
                unit=unit,
                cost_price=cost_price,
                sale_price=sale_price,
                min_stock=min_stock
            )

            try:
                self.state.db.execute(
                    """
                    INSERT INTO audit_logs
                        (user_id, action, entity_type, entity_id, description)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        self.state.current_user.get("id"),
                        "create_product",
                        "product",
                        product_id,
                        f"Tạo sản phẩm {sku} - {name}",
                    )
                )
            except Exception:
                pass

            messagebox.showinfo(
                "Hoàn tất",
                "Đã tạo sản phẩm."
            )

            if callable(self.on_created):
                self.on_created()

            self.destroy()

        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)

        self.geometry(f"{width}x{height}+{x}+{y}")