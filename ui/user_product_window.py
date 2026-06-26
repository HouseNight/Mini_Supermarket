from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any

from sieu_thi_mini_app.modules.auth_user_module import AuthUserModule
from sieu_thi_mini_app.modules.product_module import ProductModule
from sieu_thi_mini_app.ui.style import apply_default_style
from sieu_thi_mini_app.ui.user_form_window import UserFormWindow
from sieu_thi_mini_app.ui.product_form_window import ProductFormWindow
from sieu_thi_mini_app.utils.constants import PERM_PRODUCT_MANAGE, PERM_USER_MANAGE
from sieu_thi_mini_app.utils.password_utils import hash_password


class UserProductWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget, state: object) -> None:
        super().__init__(master)

        apply_default_style(self)

        self.state = state
        self.title("Quản lý người dùng và sản phẩm")
        self.minsize(1000, 620)
        self._center_window(1040, 660)

        self.auth = AuthUserModule(self.state.db)
        self.product = ProductModule(self.state.db)

        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=16, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        title_frame = ttk.Frame(container, style="Card.TFrame")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(
            title_frame,
            text="👥📦 Quản lý người dùng & sản phẩm",
            style="Header.TLabel"
        ).pack(side="left")

        notebook = ttk.Notebook(container)
        notebook.grid(row=1, column=0, sticky="nsew")

        self.user_tab = ttk.Frame(notebook)
        self.product_tab = ttk.Frame(notebook)

        notebook.add(self.user_tab, text="Người dùng")
        notebook.add(self.product_tab, text="Sản phẩm")

        self._build_user_tab(self.user_tab)
        self._build_product_tab(self.product_tab)

    def _build_user_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        panel = ttk.Frame(frame, padding=12, style="Card.TFrame")
        panel.grid(row=0, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)

        self.user_tree = ttk.Treeview(
            panel,
            columns=("username", "full_name", "role", "active"),
            show="headings",
            selectmode="browse"
        )

        columns = [
            ("username", "Tài khoản", 180),
            ("full_name", "Họ tên", 260),
            ("role", "Vai trò", 180),
            ("active", "Trạng thái", 140),
        ]

        for col, title, width in columns:
            self.user_tree.heading(col, text=title)
            self.user_tree.column(col, width=width, anchor="center")

        self.user_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            panel,
            orient="vertical",
            command=self.user_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.user_tree.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(panel, style="Card.TFrame")
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        ttk.Button(
            actions,
            text="➕ Tạo người dùng",
            style="Accent.TButton",
            command=self._create_user
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="🔐 Đổi mật khẩu",
            style="TButton",
            command=self._change_password
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="❌ Xóa người dùng",
            style="Danger.TButton",
            command=self._delete_user
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="🔄 Làm mới",
            style="TButton",
            command=self._load_users
        ).pack(side="left")

    def _build_product_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        panel = ttk.Frame(frame, padding=12, style="Card.TFrame")
        panel.grid(row=0, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)

        self.product_tree = ttk.Treeview(
            panel,
            columns=("sku", "name", "category", "price", "qty"),
            show="headings",
            selectmode="browse"
        )

        columns = [
            ("sku", "SKU", 160),
            ("name", "Tên", 280),
            ("category", "Danh mục", 180),
            ("price", "Giá bán", 160),
            ("qty", "Tồn", 100),
        ]

        for col, title, width in columns:
            self.product_tree.heading(col, text=title)
            self.product_tree.column(col, width=width, anchor="center")

        self.product_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            panel,
            orient="vertical",
            command=self.product_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.product_tree.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(panel, style="Card.TFrame")
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        ttk.Button(
            actions,
            text="➕ Tạo sản phẩm",
            style="Accent.TButton",
            command=self._create_product
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="❌ Xóa sản phẩm",
            style="Danger.TButton",
            command=self._delete_product
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="🔄 Làm mới",
            style="TButton",
            command=self._load_products
        ).pack(side="left")

    def _load_data(self) -> None:
        self._load_users()
        self._load_products()

    def _load_users(self) -> None:
        rows = self.auth.list_users()

        self.user_tree.delete(*self.user_tree.get_children())

        for row in rows:
            self.user_tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["username"],
                    row["full_name"],
                    row["role_name"],
                    "Hoạt động" if row["is_active"] else "Khóa",
                )
            )

    def _load_products(self) -> None:
        rows = self.product.list_products()

        self.product_tree.delete(*self.product_tree.get_children())

        for row in rows:
            self.product_tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["sku"],
                    row["name"],
                    row["category"],
                    f"{row['sale_price']:,.0f}",
                    row["quantity"],
                )
            )

    def _create_user(self) -> None:
        if not self.state.auth.has_permission(
            self.state.current_user,
            PERM_USER_MANAGE
        ):
            messagebox.showwarning(
                "Không đủ quyền",
                "Bạn không có quyền tạo người dùng."
            )
            return

        UserFormWindow(
            self,
            self.state,
            on_created=self._load_users
        )

    def _change_password(self) -> None:
        if not self.state.auth.has_permission(
            self.state.current_user,
            PERM_USER_MANAGE
        ):
            messagebox.showwarning(
                "Không đủ quyền",
                "Bạn không có quyền đổi mật khẩu người dùng."
            )
            return

        selected_item = self.user_tree.focus()

        if not selected_item:
            messagebox.showinfo(
                "Chọn người dùng",
                "Vui lòng chọn người dùng để đổi mật khẩu."
            )
            return

        try:
            user_id = int(selected_item)
            user = self.auth.get_user(user_id)

            if not user:
                messagebox.showerror("Lỗi", "Không tìm thấy người dùng.")
                return

            self._open_change_password_dialog(user_id, user)

        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))

    def _open_change_password_dialog(
        self,
        user_id: int,
        user: dict[str, Any]
    ) -> None:
        dialog = tk.Toplevel(self)
        apply_default_style(dialog)

        dialog.title(f"Đổi mật khẩu - {user['username']}")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        width = 460
        height = 260

        frame = ttk.Frame(dialog, padding=20, style="Card.TFrame")
        frame.pack(fill="both", expand=True)

        frame.columnconfigure(0, minsize=150)
        frame.columnconfigure(1, weight=1)

        ttk.Label(
            frame,
            text=f"🔐 Đổi mật khẩu",
            style="Header.TLabel"
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 8)
        )

        ttk.Label(
            frame,
            text=f"Tài khoản: {user['username']}",
            style="Status.TLabel"
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 16)
        )

        ttk.Label(frame, text="Mật khẩu mới:").grid(
            row=2,
            column=0,
            sticky="w",
            pady=8
        )

        password_var = tk.StringVar()
        password_entry = ttk.Entry(
            frame,
            textvariable=password_var,
            show="*"
        )
        password_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            pady=8
        )

        ttk.Label(frame, text="Xác nhận mật khẩu:").grid(
            row=3,
            column=0,
            sticky="w",
            pady=8
        )

        confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(
            frame,
            textvariable=confirm_var,
            show="*"
        )
        confirm_entry.grid(
            row=3,
            column=1,
            sticky="ew",
            pady=8
        )

        button_frame = ttk.Frame(frame, style="Card.TFrame")
        button_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(18, 0)
        )

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        def apply_change() -> None:
            new_password = password_var.get()
            confirm_password = confirm_var.get()

            if not new_password:
                messagebox.showerror(
                    "Lỗi",
                    "Mật khẩu không được để trống."
                )
                return

            if len(new_password) < 4:
                messagebox.showerror(
                    "Lỗi",
                    "Mật khẩu nên có ít nhất 4 ký tự."
                )
                return

            if new_password != confirm_password:
                messagebox.showerror(
                    "Lỗi",
                    "Mật khẩu xác nhận không trùng khớp."
                )
                return

            try:
                self._change_user_password(
                    user_id=user_id,
                    new_password=new_password
                )

                messagebox.showinfo(
                    "Thành công",
                    f"Đã đổi mật khẩu cho {user['username']}."
                )

                dialog.destroy()

            except Exception as exc:
                messagebox.showerror("Lỗi", str(exc))

        ttk.Button(
            button_frame,
            text="✅ Áp dụng",
            style="Accent.TButton",
            command=apply_change
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        ttk.Button(
            button_frame,
            text="❌ Hủy",
            style="Danger.TButton",
            command=dialog.destroy
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )

        password_entry.focus_set()
        dialog.bind("<Return>", lambda _event: apply_change())

        self._center_child_window(dialog, width, height)

    def _change_user_password(
        self,
        user_id: int,
        new_password: str
    ) -> None:
        password_hash = hash_password(new_password)
        changed_by = self.state.current_user.get("id")

        self.state.db.execute(
            """
            UPDATE users
            SET password_hash = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE id = ?
            """,
            (password_hash, changed_by, user_id)
        )

        try:
            self.state.db.execute(
                """
                INSERT INTO audit_logs
                    (user_id, action, entity_type, entity_id, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    changed_by,
                    "change_password",
                    "user",
                    user_id,
                    f"Đổi mật khẩu người dùng id={user_id}",
                )
            )
        except Exception:
            pass

    def _create_product(self) -> None:
        if not self.state.auth.has_permission(
            self.state.current_user,
            PERM_PRODUCT_MANAGE
        ):
            messagebox.showwarning(
                "Không đủ quyền",
                "Bạn không có quyền tạo sản phẩm."
            )
            return

        ProductFormWindow(
            self,
            self.state,
            on_created=self._load_products
        )

    def _delete_user(self) -> None:
        if not self.state.auth.has_permission(
            self.state.current_user,
            PERM_USER_MANAGE
        ):
            messagebox.showwarning(
                "Không đủ quyền",
                "Bạn không có quyền xóa người dùng."
            )
            return

        selected_item = self.user_tree.focus()

        if not selected_item:
            messagebox.showinfo(
                "Chọn người dùng",
                "Vui lòng chọn người dùng để xóa."
            )
            return

        try:
            user_id = int(selected_item)
            user = self.auth.get_user(user_id)

            if not user:
                messagebox.showerror("Lỗi", "Không tìm thấy người dùng.")
                return

            current_user_id = self.state.current_user.get("id")

            if user_id == current_user_id:
                messagebox.showwarning(
                    "Không được phép",
                    "Bạn không thể xóa chính tài khoản đang đăng nhập."
                )
                return

            if user.get("role_code") == "ADMIN":
                messagebox.showwarning(
                    "Không được phép",
                    "Không thể xóa tài khoản quản trị viên."
                )
                return

            confirm = messagebox.askyesno(
                "Xác nhận",
                f"Bạn có chắc muốn xóa người dùng {user['username']}?"
            )

            if not confirm:
                return

            self.auth.delete_user(
                user_id,
                deleted_by=current_user_id
            )

            messagebox.showinfo(
                "Thành công",
                f"Đã xóa người dùng {user['username']}."
            )

        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))

        self._load_users()

    def _delete_product(self) -> None:
        if not self.state.auth.has_permission(
            self.state.current_user,
            PERM_PRODUCT_MANAGE
        ):
            messagebox.showwarning(
                "Không đủ quyền",
                "Bạn không có quyền xóa sản phẩm."
            )
            return

        selected_item = self.product_tree.focus()

        if not selected_item:
            messagebox.showinfo(
                "Chọn sản phẩm",
                "Vui lòng chọn sản phẩm để xóa."
            )
            return

        confirm = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc muốn xóa sản phẩm này?"
        )

        if not confirm:
            return

        try:
            product_id = int(selected_item)

            self.product.delete_product(
                product_id,
                deleted_by=self.state.current_user.get("id")
            )

            messagebox.showinfo(
                "Thành công",
                "Đã xóa sản phẩm."
            )

        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))

        self._load_products()

    def _refresh_all(self) -> None:
        self._load_users()
        self._load_products()

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def _center_child_window(
        self,
        child: tk.Toplevel,
        width: int,
        height: int
    ) -> None:
        child.update_idletasks()

        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        x = parent_x + max((parent_width - width) // 2, 0)
        y = parent_y + max((parent_height - height) // 2, 0)

        child.geometry(f"{width}x{height}+{x}+{y}")