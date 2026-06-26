from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any

from sieu_thi_mini_app.modules.warehouse_module import WarehouseModule
from sieu_thi_mini_app.modules.product_module import ProductModule
from sieu_thi_mini_app.ui.style import apply_default_style
from sieu_thi_mini_app.ui.supplier_form_window import SupplierFormWindow
from sieu_thi_mini_app.utils.constants import PERM_WAREHOUSE_MANAGE, ROLE_WAREHOUSE


class WarehouseWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget, state: object) -> None:
        super().__init__(master)

        apply_default_style(self)

        self.state = state
        self.title("Quản lý kho")
        self.minsize(960, 620)
        self._center_window(980, 640)

        self.warehouse = WarehouseModule(self.state.db)
        self._receipt_items: list[dict[str, Any]] = []

        self._build_ui()
        self._load_suppliers()
        self._refresh_product_combobox()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=16, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        title_frame = ttk.Frame(container)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            title_frame,
            text="📦 Quản lý kho",
            style="Header.TLabel"
        ).pack(side="left")

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True, padx=4, pady=4)

        self.supplier_tab = ttk.Frame(notebook)
        self.receipt_tab = ttk.Frame(notebook)

        notebook.add(self.supplier_tab, text="Nhà cung cấp")
        notebook.add(self.receipt_tab, text="Nhập hàng")

        self._build_supplier_tab(self.supplier_tab)
        self._build_receipt_tab(self.receipt_tab)

    def _build_supplier_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        panel = ttk.Frame(frame, padding=12, style="Card.TFrame")
        panel.grid(row=0, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)

        self.supplier_tree = ttk.Treeview(
            panel,
            columns=("code", "name", "phone", "email", "address"),
            show="headings"
        )

        columns = [
            ("code", "Mã", 120),
            ("name", "Tên", 220),
            ("phone", "Điện thoại", 150),
            ("email", "Email", 220),
            ("address", "Địa chỉ", 300),
        ]

        for col, title, width in columns:
            self.supplier_tree.heading(col, text=title)
            self.supplier_tree.column(col, width=width, anchor="center")

        self.supplier_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            panel,
            orient="vertical",
            command=self.supplier_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.supplier_tree.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(panel)
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        ttk.Button(
            actions,
            text="➕ Tạo nhà cung cấp",
            style="Accent.TButton",
            command=self._create_supplier
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="❌ Xóa nhà cung cấp",
            style="Danger.TButton",
            command=self._delete_supplier
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="🔄 Làm mới",
            style="TButton",
            command=self._load_suppliers
        ).pack(side="left")

    def _build_receipt_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        panel = ttk.Frame(frame, padding=12, style="Card.TFrame")
        panel.grid(row=0, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        supplier_frame = ttk.Frame(panel)
        supplier_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        supplier_frame.columnconfigure(1, weight=1)

        ttk.Label(
            supplier_frame,
            text="🏢 Nhà cung cấp:",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.supplier_var = tk.StringVar()
        self.supplier_cb = ttk.Combobox(
            supplier_frame,
            textvariable=self.supplier_var,
            state="readonly"
        )
        self.supplier_cb.grid(row=0, column=1, sticky="ew")

        product_frame = ttk.Frame(panel)
        product_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        product_frame.columnconfigure(1, weight=1)

        ttk.Label(
            product_frame,
            text="Sản phẩm:"
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.product_var = tk.StringVar()
        self.product_cb = ttk.Combobox(
            product_frame,
            textvariable=self.product_var,
            state="readonly"
        )
        self.product_cb.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(
            product_frame,
            text="Số lượng:"
        ).grid(row=0, column=2, sticky="w", padx=(0, 6))

        self.qty_entry = ttk.Entry(product_frame, width=10)
        self.qty_entry.grid(row=0, column=3, sticky="w", padx=(0, 10))

        ttk.Label(
            product_frame,
            text="Đơn giá:"
        ).grid(row=0, column=4, sticky="w", padx=(0, 6))

        self.unit_entry = ttk.Entry(product_frame, width=14)
        self.unit_entry.grid(row=0, column=5, sticky="w", padx=(0, 10))

        ttk.Button(
            product_frame,
            text="➕ Thêm",
            style="Accent.TButton",
            command=self._add_receipt_item
        ).grid(row=0, column=6, sticky="ew")

        table_frame = ttk.Frame(panel)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.items_tree = ttk.Treeview(
            table_frame,
            columns=("sku", "name", "qty", "unit", "total"),
            show="headings"
        )

        item_columns = [
            ("sku", "SKU", 140),
            ("name", "Tên", 280),
            ("qty", "SL", 100),
            ("unit", "Đơn giá", 140),
            ("total", "Thành tiền", 160),
        ]

        for col, title, width in item_columns:
            self.items_tree.heading(col, text=title)
            self.items_tree.column(col, width=width, anchor="center")

        self.items_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.items_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.items_tree.configure(yscrollcommand=scrollbar.set)

        bottom_frame = ttk.Frame(panel)
        bottom_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        bottom_frame.columnconfigure(2, weight=1)

        ttk.Button(
            bottom_frame,
            text="❌ Xóa mục",
            style="Danger.TButton",
            command=self._remove_receipt_item
        ).grid(row=0, column=0, padx=(0, 8))

        ttk.Button(
            bottom_frame,
            text="🔄 Làm mới",
            style="TButton",
            command=self._refresh_receipt_tab
        ).grid(row=0, column=1, padx=(0, 8))

        self.total_label = ttk.Label(
            bottom_frame,
            text="Tổng: 0",
            style="CardValue.TLabel"
        )
        self.total_label.grid(row=0, column=2, sticky="w")

        ttk.Button(
            bottom_frame,
            text="✅ Nhập hàng",
            style="Success.TButton",
            command=self._submit_receipt
        ).grid(row=0, column=3, sticky="e")

    def _load_suppliers(self) -> None:
        rows = self.warehouse.list_suppliers()

        self.supplier_tree.delete(*self.supplier_tree.get_children())

        for row in rows:
            self.supplier_tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["code"],
                    row["name"],
                    row["phone"] or "",
                    row["email"] or "",
                    row["address"] or "",
                )
            )

        self._refresh_supplier_combobox()

    def _refresh_supplier_combobox(self) -> None:
        if not hasattr(self, "supplier_cb"):
            return

        suppliers = self.warehouse.list_suppliers()

        values = [
            f"{supplier['id']} - {supplier['name']}"
            for supplier in suppliers
        ]

        self.supplier_cb["values"] = values

    def _refresh_product_combobox(self) -> None:
        if not hasattr(self, "product_cb"):
            return

        products = ProductModule(self.state.db).list_products()

        values = [
            f"{product['id']} - {product['sku']} - {product['name']}"
            for product in products
        ]

        self.product_cb["values"] = values

    def _create_supplier(self) -> None:
        if not self.state.auth.has_permission(
            self.state.current_user,
            PERM_WAREHOUSE_MANAGE
        ):
            messagebox.showwarning(
                "Không đủ quyền",
                "Bạn không có quyền tạo nhà cung cấp."
            )
            return

        SupplierFormWindow(
            self,
            self.state,
            on_created=self._on_supplier_created
        )

    def _on_supplier_created(self) -> None:
        self._load_suppliers()
        self._refresh_supplier_combobox()

    def _delete_supplier(self) -> None:
        if not self.state.auth.has_permission(
            self.state.current_user,
            PERM_WAREHOUSE_MANAGE
        ):
            messagebox.showwarning(
                "Không đủ quyền",
                "Bạn không có quyền xóa nhà cung cấp."
            )
            return

        user_role = self.state.current_user.get("role_code")

        if user_role == ROLE_WAREHOUSE:
            messagebox.showwarning(
                "Không đủ quyền",
                "Nhân viên kho không được phép xóa nhà cung cấp."
            )
            return

        selected_item = self.supplier_tree.focus()

        if not selected_item:
            messagebox.showinfo(
                "Chọn nhà cung cấp",
                "Vui lòng chọn nhà cung cấp để xóa."
            )
            return

        if not messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc muốn xóa nhà cung cấp này?"
        ):
            return

        try:
            supplier_id = int(selected_item)

            self.warehouse.delete_supplier(
                supplier_id,
                deleted_by=self.state.current_user.get("id")
            )

            messagebox.showinfo(
                "Hoàn tất",
                "Đã xóa nhà cung cấp."
            )

        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))

        self._load_suppliers()

    def _add_receipt_item(self) -> None:
        product_raw = self.product_cb.get().strip()

        if not product_raw:
            messagebox.showinfo(
                "Chọn sản phẩm",
                "Vui lòng chọn sản phẩm."
            )
            return

        try:
            product_id = int(product_raw.split("-")[0].strip())
        except Exception:
            messagebox.showerror(
                "Lỗi",
                "Mã sản phẩm không hợp lệ."
            )
            return

        quantity_raw = self.qty_entry.get().strip()
        unit_cost_raw = self.unit_entry.get().strip()

        if not quantity_raw:
            messagebox.showerror(
                "Lỗi",
                "Vui lòng nhập số lượng."
            )
            return

        if not unit_cost_raw:
            messagebox.showerror(
                "Lỗi",
                "Vui lòng nhập đơn giá."
            )
            return

        try:
            quantity = int(quantity_raw)
        except ValueError:
            messagebox.showerror(
                "Lỗi",
                "Số lượng phải là số nguyên."
            )
            return

        try:
            unit_cost = float(unit_cost_raw)
        except ValueError:
            messagebox.showerror(
                "Lỗi",
                "Đơn giá phải là số hợp lệ."
            )
            return

        if quantity <= 0:
            messagebox.showerror(
                "Lỗi",
                "Số lượng phải lớn hơn 0."
            )
            return

        if unit_cost < 0:
            messagebox.showerror(
                "Lỗi",
                "Đơn giá không được âm."
            )
            return

        product = self.state.db.fetch_one(
            "SELECT sku, name FROM products WHERE id = ?",
            (product_id,)
        )

        if not product:
            messagebox.showerror(
                "Lỗi",
                "Sản phẩm không tồn tại."
            )
            return

        line_total = quantity * unit_cost

        self._receipt_items.append(
            {
                "product_id": product_id,
                "quantity": quantity,
                "unit_cost": unit_cost,
            }
        )

        self.items_tree.insert(
            "",
            "end",
            values=(
                product["sku"],
                product["name"],
                quantity,
                f"{unit_cost:,.0f}",
                f"{line_total:,.0f}",
            )
        )

        self.qty_entry.delete(0, tk.END)
        self.unit_entry.delete(0, tk.END)

        self._update_total()

    def _remove_receipt_item(self) -> None:
        selected_item = self.items_tree.focus()

        if not selected_item:
            messagebox.showinfo(
                "Chọn mục",
                "Vui lòng chọn dòng cần xóa."
            )
            return

        index = self.items_tree.index(selected_item)

        self.items_tree.delete(selected_item)

        if 0 <= index < len(self._receipt_items):
            self._receipt_items.pop(index)

        self._update_total()

    def _update_total(self) -> None:
        total = sum(
            int(item["quantity"]) * float(item["unit_cost"])
            for item in self._receipt_items
        )

        self.total_label.config(text=f"Tổng: {total:,.0f}")

    def _submit_receipt(self) -> None:
        if not self._receipt_items:
            messagebox.showinfo(
                "Chưa có mục",
                "Vui lòng thêm ít nhất một mục nhập hàng."
            )
            return

        supplier_raw = self.supplier_cb.get().strip()
        supplier_id = None

        if supplier_raw:
            try:
                supplier_id = int(supplier_raw.split("-")[0].strip())
            except Exception:
                supplier_id = None

        try:
            receipt_id = self.warehouse.create_receipt_with_items(
                supplier_id,
                self._receipt_items,
                created_by=self.state.current_user.get("id")
            )

            messagebox.showinfo(
                "Hoàn tất",
                f"Đã tạo phiếu nhập id={receipt_id}"
            )

            self._clear_receipt_items()
            self.supplier_cb.set("")
            self.product_cb.set("")
            self._refresh_product_combobox()

        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))

    def _refresh_receipt_tab(self) -> None:
        self._refresh_supplier_combobox()
        self._refresh_product_combobox()

        self.supplier_cb.set("")
        self.product_cb.set("")

        self.qty_entry.delete(0, tk.END)
        self.unit_entry.delete(0, tk.END)

        self._clear_receipt_items()

        messagebox.showinfo(
            "Hoàn tất",
            "Đã làm mới tab nhập hàng."
        )

    def _clear_receipt_items(self) -> None:
        self._receipt_items = []

        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        self._update_total()

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)

        self.geometry(f"{width}x{height}+{x}+{y}")