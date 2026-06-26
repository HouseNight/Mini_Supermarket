from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from sieu_thi_mini_app.modules.product_module import ProductModule
from sieu_thi_mini_app.ui.audit_window import AuditWindow
from sieu_thi_mini_app.ui.report_window import ReportWindow
from sieu_thi_mini_app.ui.sales_window import SalesWindow
from sieu_thi_mini_app.ui.style import apply_default_style
from sieu_thi_mini_app.ui.user_product_window import UserProductWindow
from sieu_thi_mini_app.ui.warehouse_window import WarehouseWindow
from sieu_thi_mini_app.utils.constants import (
    APP_NAME,
    PERM_AUDIT_VIEW,
    PERM_REPORT_VIEW,
    PERM_SALE_MANAGE,
    PERM_WAREHOUSE_MANAGE,
    PERM_USER_MANAGE,
)


class MainWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Tk,
        state: object,
        *,
        on_logout: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        super().__init__(master)

        apply_default_style(self)

        self.state = state
        self.on_logout = on_logout
        self.on_exit = on_exit

        self.title(APP_NAME)
        self.minsize(1220, 720)
        self._center_window(1280, 740)

        self.protocol("WM_DELETE_WINDOW", self._exit)

        self._build_ui()

    def _build_ui(self) -> None:
        user = self.state.current_user

        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)

        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

        # ================= HEADER =================
        header = ttk.Frame(root, style="Panel.TFrame", padding=12)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text=f"🏪 {APP_NAME}",
            style="Header.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text=f"👤 {user['full_name']} · {user['role_name']}",
            style="Status.TLabel"
        ).grid(row=0, column=1, sticky="e")

        ttk.Separator(root).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 14)
        )

        # ================= SIDEBAR =================
        sidebar = ttk.Frame(root, style="Card.TFrame", padding=(14, 14))
        sidebar.grid(row=2, column=0, sticky="nsw", padx=(0, 16))
        sidebar.columnconfigure(0, minsize=240)

        ttk.Label(
            sidebar,
            text="Chức năng",
            style="SubHeader.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        self._add_button(
            sidebar,
            "👥 Người & Sản phẩm",
            PERM_USER_MANAGE,
            lambda: self._open_child_window(UserProductWindow),
            1
        )

        self._add_button(
            sidebar,
            "🛒 Bán hàng",
            PERM_SALE_MANAGE,
            lambda: self._open_child_window(SalesWindow),
            2
        )

        self._add_button(
            sidebar,
            "📦 Kho",
            PERM_WAREHOUSE_MANAGE,
            lambda: self._open_child_window(WarehouseWindow),
            3
        )

        self._add_button(
            sidebar,
            "📊 Báo cáo",
            PERM_REPORT_VIEW,
            lambda: self._open_child_window(ReportWindow),
            4
        )

        self._add_button(
            sidebar,
            "📋 Nhật ký",
            PERM_AUDIT_VIEW,
            self._open_audit_window,
            5
        )

        ttk.Separator(sidebar).grid(
            row=6,
            column=0,
            sticky="ew",
            pady=16
        )

        ttk.Button(
            sidebar,
            text="🚪 Đăng xuất",
            style="Secondary.TButton",
            command=self._logout
        ).grid(row=7, column=0, sticky="ew", pady=4)

        ttk.Button(
            sidebar,
            text="❌ Thoát",
            style="Danger.TButton",
            command=self._exit
        ).grid(row=8, column=0, sticky="ew", pady=4)

        # ================= CONTENT =================
        content = ttk.Frame(root, style="Card.TFrame", padding=18)
        content.grid(row=2, column=1, sticky="nsew")

        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self._build_dashboard(content)
        self._refresh_dashboard()

    def _build_dashboard(self, parent: ttk.Frame) -> None:
        # ================= SUMMARY AREA =================
        dashboard_top = ttk.Frame(parent, style="Card.TFrame")
        dashboard_top.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        dashboard_top.columnconfigure(0, weight=1)
        dashboard_top.columnconfigure(1, weight=1)
        dashboard_top.columnconfigure(2, weight=1)
        dashboard_top.columnconfigure(3, weight=0)

        self.products_count_label = self._create_summary_card(
            parent=dashboard_top,
            column=0,
            icon="📦",
            title="Sản phẩm"
        )

        self.categories_count_label = self._create_summary_card(
            parent=dashboard_top,
            column=1,
            icon="🏷️",
            title="Danh mục"
        )

        self.low_stock_label = self._create_summary_card(
            parent=dashboard_top,
            column=2,
            icon="⚠️",
            title="Tồn thấp"
        )

        ttk.Button(
            dashboard_top,
            text="🔄 Làm mới",
            style="Accent.TButton",
            command=self._refresh_dashboard
        ).grid(
            row=0,
            column=3,
            sticky="ne",
            padx=(14, 0),
            pady=(6, 0)
        )

        # ================= LOW STOCK LIST =================
        low_stock_frame = ttk.LabelFrame(
            parent,
            text="Danh sách sản phẩm cảnh báo tồn thấp",
            padding=12
        )
        low_stock_frame.grid(row=1, column=0, sticky="nsew")

        low_stock_frame.columnconfigure(0, weight=1)
        low_stock_frame.rowconfigure(1, weight=1)

        self.low_stock_message_label = ttk.Label(
            low_stock_frame,
            text="",
            style="Status.TLabel"
        )
        self.low_stock_message_label.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 8)
        )

        table_frame = ttk.Frame(low_stock_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.low_stock_tree = ttk.Treeview(
            table_frame,
            columns=("sku", "name", "quantity", "min_stock", "status"),
            show="headings",
            height=10
        )

        columns = [
            ("sku", "SKU", 110),
            ("name", "Tên sản phẩm", 320),
            ("quantity", "Tồn hiện tại", 115),
            ("min_stock", "Tồn tối thiểu", 115),
            ("status", "Trạng thái", 140),
        ]

        for col, title, width in columns:
            self.low_stock_tree.heading(col, text=title)
            self.low_stock_tree.column(
                col,
                width=width,
                minwidth=width,
                anchor="center",
                stretch=True
            )

        self.low_stock_tree.grid(row=0, column=0, sticky="nsew")

        y_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.low_stock_tree.yview
        )
        y_scrollbar.grid(row=0, column=1, sticky="ns")

        x_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.low_stock_tree.xview
        )
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        self.low_stock_tree.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        ttk.Label(
            parent,
            text="Chọn chức năng từ thanh điều hướng bên trái để thao tác.",
            style="Status.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=(16, 0))

    def _create_summary_card(
        self,
        parent: ttk.Frame,
        column: int,
        icon: str,
        title: str
    ) -> ttk.Label:
        card = ttk.Frame(parent, padding=14, style="Card.TFrame")
        card.grid(row=0, column=column, sticky="ew", padx=(0, 12))

        card.columnconfigure(0, weight=1)

        top_line = ttk.Frame(card, style="Card.TFrame")
        top_line.grid(row=0, column=0, sticky="ew")

        ttk.Label(
            top_line,
            text=icon,
            font=("Segoe UI", 22)
        ).pack(side="left")

        value_label = ttk.Label(
            top_line,
            text="0",
            font=("Segoe UI", 28, "bold")
        )
        value_label.pack(side="right")

        ttk.Label(
            card,
            text=title,
            font=("Segoe UI", 13, "bold")
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        return value_label

    def _refresh_dashboard(self) -> None:
        products = ProductModule(self.state.db).list_products()
        categories = ProductModule(self.state.db).list_categories()
        low_stock = ProductModule(self.state.db).list_inventory(low_stock_only=True)

        self.products_count_label.config(text=str(len(products)))
        self.categories_count_label.config(text=str(len(categories)))
        self.low_stock_label.config(text=str(len(low_stock)))

        self.low_stock_tree.delete(*self.low_stock_tree.get_children())

        if not low_stock:
            self.low_stock_message_label.config(
                text="✅ Không có sản phẩm nào dưới mức tồn tối thiểu."
            )
            return

        self.low_stock_message_label.config(
            text=f"⚠️ Có {len(low_stock)} sản phẩm cần chú ý và nên xem xét nhập thêm."
        )

        for item in low_stock:
            quantity = int(item["quantity"])
            min_stock = int(item["min_stock"])

            if quantity <= 0:
                status = "Hết hàng"
            else:
                status = "Tồn thấp"

            self.low_stock_tree.insert(
                "",
                "end",
                values=(
                    item["sku"],
                    item["name"],
                    quantity,
                    min_stock,
                    status,
                )
            )

    def _open_child_window(self, window_class: type[tk.Toplevel]) -> None:
        child = window_class(self, self.state)

        def on_child_closed(event: tk.Event) -> None:
            if event.widget is child:
                try:
                    if self.winfo_exists():
                        self._refresh_dashboard()
                except Exception:
                    pass

        child.bind("<Destroy>", on_child_closed, add="+")

    def _open_audit_window(self) -> None:
        child = AuditWindow(self, self.state.db)

        def on_child_closed(event: tk.Event) -> None:
            if event.widget is child:
                try:
                    if self.winfo_exists():
                        self._refresh_dashboard()
                except Exception:
                    pass

        child.bind("<Destroy>", on_child_closed, add="+")

    def _add_button(
        self,
        parent: ttk.Frame,
        label: str,
        permission: str,
        command: Callable[[], None],
        row: int
    ) -> None:
        button = ttk.Button(
            parent,
            text=label,
            style="Accent.TButton",
            command=command
        )

        button.grid(row=row, column=0, sticky="ew", pady=4)

        if permission and not self.state.auth.has_permission(
            self.state.current_user,
            permission
        ):
            button.state(["disabled"])

    def _logout(self) -> None:
        self.destroy()
        self.on_logout()

    def _exit(self) -> None:
        self.on_exit()

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)

        self.geometry(f"{width}x{height}+{x}+{y}")