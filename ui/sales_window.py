from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any

from sieu_thi_mini_app.modules.product_module import ProductModule
from sieu_thi_mini_app.modules.sales_module import InvoiceItem, SalesModule
from sieu_thi_mini_app.ui.style import apply_default_style
from sieu_thi_mini_app.utils.constants import PERM_SALE_MANAGE


class SalesWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget, state: object) -> None:
        super().__init__(master)
        apply_default_style(self)
        self.state = state
        self.title("Bán hàng")
        self.minsize(980, 620)
        self._center_window(1000, 640)
        self.sales = SalesModule(self.state.db)
        self.product = ProductModule(self.state.db)
        self.cart: list[dict[str, Any]] = []
        self._build_ui()
        self._load_products()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=16, style="Card.TFrame")
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=2)
        root.columnconfigure(1, weight=1)

        # Header
        header = ttk.Frame(root, style="Panel.TFrame", padding=12)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(header, text="🛒 Bán hàng", style="Header.TLabel").pack(anchor="w")

        left_panel = ttk.Frame(root)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=4)
        left_panel.rowconfigure(1, weight=1)
        left_panel.columnconfigure(0, weight=1)
        right_panel = ttk.Frame(root)
        right_panel.grid(row=1, column=1, sticky="nsew", pady=4)
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)

        ttk.Label(left_panel, text="📦 Danh sách sản phẩm", style="SubHeader.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.product_tree = ttk.Treeview(left_panel, columns=("sku", "name", "price", "qty"), show="headings", selectmode="browse")
        for col, title in [("sku", "SKU"), ("name", "Sản phẩm"), ("price", "Giá"), ("qty", "Tồn")]:
            self.product_tree.heading(col, text=title)
            self.product_tree.column(col, width=120)
        self.product_tree.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.product_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.product_tree.configure(yscrollcommand=scrollbar.set)

        control_frame = ttk.Frame(left_panel, style="Panel.TFrame", padding=8)
        control_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        control_frame.columnconfigure(1, weight=1)
        ttk.Label(control_frame, text="📋 Số lượng:", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.quantity_var = tk.StringVar(value="1")
        ttk.Entry(control_frame, textvariable=self.quantity_var, width=8).grid(row=0, column=1, sticky="w", padx=(6, 12))
        ttk.Button(control_frame, text="➕ Thêm vào giỏ", style="Accent.TButton", command=self._add_to_cart).grid(row=0, column=2, padx=4)

        ttk.Label(right_panel, text="🧺 Giỏ hàng", style="SubHeader.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        cart_frame = ttk.Frame(right_panel, style="Panel.TFrame", padding=8)
        cart_frame.grid(row=1, column=0, sticky="nsew")
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(0, weight=1)

        self.cart_tree = ttk.Treeview(cart_frame, columns=("product", "qty", "price", "total"), show="headings")
        for col, title in [("product", "Sản phẩm"), ("qty", "SL"), ("price", "Đơn giá"), ("total", "Thành tiền")]:
            self.cart_tree.heading(col, text=title)
            self.cart_tree.column(col, width=100)
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview).grid(row=0, column=1, sticky="ns")
        self.cart_tree.configure(yscrollcommand=lambda *args: None)

        summary = ttk.Frame(right_panel, style="Panel.TFrame", padding=8)
        summary.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        summary.columnconfigure(0, weight=1)
        ttk.Label(summary, text="💰 Tổng tiền:", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.total_label = ttk.Label(summary, text="0 ₫", style="CardValue.TLabel")
        self.total_label.grid(row=0, column=1, sticky="e")
        ttk.Button(summary, text="❌ Xóa mục", style="Danger.TButton", command=self._remove_item).grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(summary, text="✅ Thanh toán", style="Success.TButton", command=self._checkout).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(8, 0))

    def _load_products(self) -> None:
        products = self.product.list_products()
        self.product_tree.delete(*self.product_tree.get_children())
        for product in products:
            self.product_tree.insert(
                "",
                "end",
                iid=str(product["id"]),
                values=(product["sku"], product["name"], f"{product['sale_price']:,.0f}", product["quantity"]),
            )

    def _add_to_cart(self) -> None:
        if not self.state.auth.has_permission(self.state.current_user, PERM_SALE_MANAGE):
            messagebox.showwarning("Không đủ quyền", "Bạn không có quyền bán hàng.")
            return
        selection = self.product_tree.selection()
        if not selection:
            return
        product_id = int(selection[0])
        product = self.product.get_product(product_id)
        if product is None:
            return
        try:
            quantity = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên.")
            return
        if quantity <= 0 or quantity > product["quantity"]:
            messagebox.showerror("Lỗi", "Số lượng không hợp lệ hoặc vượt tồn kho.")
            return
        self.cart.append({
            "product_id": product_id,
            "name": product["name"],
            "quantity": quantity,
            "unit_price": product["sale_price"],
            "total": quantity * product["sale_price"],
        })
        self._refresh_cart()

    def _remove_item(self) -> None:
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = self.cart_tree.index(sel[0])
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
            self._refresh_cart()

    def _refresh_cart(self) -> None:
        self.cart_tree.delete(*self.cart_tree.get_children())
        total = 0
        for item in self.cart:
            total += item["total"]
            self.cart_tree.insert(
                "",
                "end",
                values=(item["name"], item["quantity"], f"{item['unit_price']:,.0f}", f"{item['total']:,.0f}"),
            )
        self.total_label.config(text=f"Tổng: {total:,.0f}")

    def _checkout(self) -> None:
        if not self.cart:
            return
        try:
            items = [InvoiceItem(product_id=item["product_id"], quantity=item["quantity"], unit_price=item["unit_price"]) for item in self.cart]
            invoice_id = self.sales.create_invoice(
                cashier_id=int(self.state.current_user["id"]),
                items=items,
                discount_amount=0.0,
                payment_method="Tiền mặt",
                payment_amount=sum(item["total"] for item in self.cart),
            )
            messagebox.showinfo("Thanh toán", f"Hóa đơn {invoice_id} đã tạo thành công.")
            self.cart.clear()
            self._refresh_cart()
            self._load_products()
        except Exception as exc:
            messagebox.showerror("Thanh toán thất bại", str(exc))

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")
