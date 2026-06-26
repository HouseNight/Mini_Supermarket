from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from sieu_thi_mini_app.modules.sales_module import SalesModule
from sieu_thi_mini_app.ui.style import apply_default_style


class InvoiceDetailWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget, state: object, invoice_id: int) -> None:
        super().__init__(master)
        apply_default_style(self)
        self.state = state
        self.invoice_id = invoice_id
        self.sales = SalesModule(self.state.db)
        self.title(f"Chi tiết hóa đơn #{invoice_id}")
        self.minsize(560, 360)
        self._center_window(600, 420)
        self._build_ui()
        self._load_invoice()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=16, style="Card.TFrame")
        frame.pack(fill="both", expand=True)

        self.header = ttk.Label(frame, text="", style="Header.TLabel")
        self.header.pack(anchor="w", pady=(0, 12))

        self.tree = ttk.Treeview(frame, columns=("sku", "name", "qty", "unit", "line_total"), show="headings")
        for col, title in [("sku", "SKU"), ("name", "Tên"), ("qty", "SL"), ("unit", "Giá"), ("line_total", "Tổng")] :
            self.tree.heading(col, text=title)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True, pady=(8,0))

    def _load_invoice(self) -> None:
        invoice = self.sales.get_invoice_by_id(self.invoice_id)
        if not invoice:
            self.header.config(text="Hóa đơn không tồn tại")
            return
        self.header.config(text=f"{invoice['invoice_no']} · Thành tiền: {invoice['total_amount']:,.0f} · Trạng thái: {invoice['status']}")
        items = self.sales.get_invoice_items(self.invoice_id)
        for it in items:
            self.tree.insert("", "end", values=(it["sku"], it["product_name"], it["quantity"], f"{it['unit_price']:,.0f}", f"{it['line_total']:,.0f}"))

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")
