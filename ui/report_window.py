from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from sieu_thi_mini_app.modules.report_module import ReportModule
from sieu_thi_mini_app.ui.invoice_detail_window import InvoiceDetailWindow
from sieu_thi_mini_app.ui.style import apply_default_style


class ReportWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget, state: object) -> None:
        super().__init__(master)
        apply_default_style(self)
        self.state = state
        self.title("Báo cáo")
        self.minsize(960, 620)
        self._center_window(980, 640)
        self.report = ReportModule(self.state.db)
        self._build_ui()
        self._load_reports()
        self.bind("<FocusIn>", self._on_window_focus)
        self.bind("<Map>", self._on_window_map)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=16, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="Panel.TFrame", padding=12)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="📊 Báo cáo", style="Header.TLabel").pack(anchor="w")

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.revenue_tab = ttk.Frame(notebook)
        self.best_tab = ttk.Frame(notebook)
        self.inventory_tab = ttk.Frame(notebook)

        notebook.add(self.revenue_tab, text="Doanh thu")
        notebook.add(self.best_tab, text="Bán chạy")
        notebook.add(self.inventory_tab, text="Tồn kho")
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook = notebook

        self._build_revenue_tab(self.revenue_tab)
        self._build_best_tab(self.best_tab)
        self._build_inventory_tab(self.inventory_tab)

    def _build_revenue_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        self.revenue_tree = ttk.Treeview(frame, columns=("invoice_no", "total", "status", "created_at"), show="headings")
        for col, title in [
            ("invoice_no", "Số hóa đơn"),
            ("total", "Tổng"),
            ("status", "Trạng thái"),
            ("created_at", "Ngày"),
        ]:
            self.revenue_tree.heading(col, text=title)
            self.revenue_tree.column(col, width=140)
        self.revenue_tree.pack(fill="both", expand=True)
        self.revenue_tree.bind("<Double-1>", self._on_invoice_double_click)

    def _build_best_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        self.best_tree = ttk.Treeview(frame, columns=("sku", "name", "qty", "revenue"), show="headings")
        for col, title in [("sku", "SKU"), ("name", "Tên"), ("qty", "SL bán"), ("revenue", "Doanh thu")]:
            self.best_tree.heading(col, text=title)
            self.best_tree.column(col, width=140)
        self.best_tree.pack(fill="both", expand=True)

    def _build_inventory_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        panel = ttk.Frame(frame, padding=12, style="Card.TFrame")
        panel.pack(fill="both", expand=True)
        self.inventory_tree = ttk.Treeview(panel, columns=("sku", "name", "qty", "min_stock", "low_stock"), show="headings")
        for col, title in [("sku", "SKU"), ("name", "Tên"), ("qty", "Tồn"), ("min_stock", "Tồn tối thiểu"), ("low_stock", "Cảnh báo")]:
            self.inventory_tree.heading(col, text=title)
            self.inventory_tree.column(col, width=120)
        self.inventory_tree.pack(fill="both", expand=True)

        btns = ttk.Frame(panel)
        btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="Làm mới", style="Accent.TButton", command=self._refresh_inventory_tab).pack(side="left")

    def _load_reports(self) -> None:
        self.report = ReportModule(self.state.db)
        self._load_revenue_report()
        self._load_best_selling_report()
        self._load_inventory_report()

    def _load_revenue_report(self) -> None:
        self.revenue_tree.delete(*self.revenue_tree.get_children())
        for row in self.report.revenue_report():
            iid = str(row["id"])
            self.revenue_tree.insert("", "end", iid=iid, values=(row["invoice_no"], f"{row['total_amount']:,.0f}", row["status"], row["created_at"]))

    def _load_best_selling_report(self) -> None:
        self.best_tree.delete(*self.best_tree.get_children())
        for row in self.report.best_selling_report():
            self.best_tree.insert("", "end", values=(row["sku"], row["name"], row["total_quantity"], f"{row['total_revenue']:,.0f}"))

    def _load_inventory_report(self) -> None:
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        for row in self.report.inventory_report():
            self.inventory_tree.insert(
                "",
                "end",
                values=(row["sku"], row["name"], row["quantity"], row["min_stock"], "Có" if row["low_stock"] else "Không"),
            )

    def _refresh_inventory_tab(self) -> None:
        self.report = ReportModule(self.state.db)
        self._load_inventory_report()

    def _refresh_report_window(self) -> None:
        self._load_reports()

    def _on_tab_changed(self, event: object) -> None:
        selected = event.widget.select()
        label = event.widget.tab(selected, "text")
        if label == "Tồn kho":
            self._refresh_report_window()

    def _on_window_focus(self, event: object) -> None:
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
        except Exception:
            return
        if current_tab == "Tồn kho":
            self._refresh_report_window()

    def _on_window_map(self, event: object) -> None:
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
        except Exception:
            return
        if current_tab == "Tồn kho":
            self._refresh_report_window()

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _on_invoice_double_click(self, event: object) -> None:
        sel = self.revenue_tree.focus()
        if not sel:
            return
        try:
            invoice_id = int(sel)
        except Exception:
            return
        InvoiceDetailWindow(self, self.state, invoice_id)
