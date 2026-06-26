from __future__ import annotations

from typing import Any

from sieu_thi_mini_app.database.db import Database
from sieu_thi_mini_app.utils.password_utils import hash_password, verify_password


class AuthUserModule:
    def __init__(self, db: Database) -> None:
        self.db = db

    def login(self, username: str, password: str) -> dict[str, Any]:
        row = self.db.fetch_one(
            """
            SELECT u.id,
                   u.username,
                   u.password_hash,
                   u.full_name,
                   u.email,
                   u.phone,
                   u.is_active,
                   r.code AS role_code,
                   r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE LOWER(u.username) = LOWER(?)
            """,
            (username.strip(),),
        )
        if row is None or not row["is_active"]:
            raise ValueError("Tên đăng nhập hoặc mật khẩu không đúng")
        if not verify_password(password, row["password_hash"]):
            raise ValueError("Tên đăng nhập hoặc mật khẩu không đúng")

        permissions = self.db.fetch_all(
            """
            SELECT p.code
            FROM permissions p
            JOIN role_permissions rp ON rp.permission_id = p.id
            JOIN roles r ON r.id = rp.role_id
            JOIN users u ON u.role_id = r.id
            WHERE u.id = ?
            """,
            (row["id"],),
        )
        row["permissions"] = [item["code"] for item in permissions]
        return row

    def list_users(self) -> list[dict[str, Any]]:
        return self.db.fetch_all(
            """
            SELECT u.id,
                   u.username,
                   u.full_name,
                   u.email,
                   u.phone,
                   u.is_active,
                   r.code AS role_code,
                   r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            ORDER BY u.username
            """
        )

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        return self.db.fetch_one(
            """
            SELECT u.id,
                   u.username,
                   u.full_name,
                   u.email,
                   u.phone,
                   u.is_active,
                   r.code AS role_code,
                   r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.id = ?
            """,
            (user_id,),
        )

    def create_user(
        self,
        username: str,
        password: str,
        full_name: str,
        email: str | None,
        phone: str | None,
        role_code: str,
    ) -> int:
        password_hash = hash_password(password)
        role = self.db.fetch_one("SELECT id FROM roles WHERE code = ?", (role_code,))
        if role is None:
            raise ValueError("Vai trò không hợp lệ")
        cursor = self.db.execute(
            """
            INSERT INTO users (username, password_hash, full_name, email, phone, role_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (username.strip().lower(), password_hash, full_name.strip(), email, phone, role["id"]),
        )
        return int(cursor.lastrowid)

    def update_user(
        self,
        user_id: int,
        full_name: str,
        email: str | None,
        phone: str | None,
        role_code: str,
        is_active: bool,
    ) -> None:
        role = self.db.fetch_one("SELECT id FROM roles WHERE code = ?", (role_code,))
        if role is None:
            raise ValueError("Vai trò không hợp lệ")
        self.db.execute(
            """
            UPDATE users
            SET full_name = ?,
                email = ?,
                phone = ?,
                role_id = ?,
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (full_name.strip(), email, phone, role["id"], int(is_active), user_id),
        )

    def list_roles(self) -> list[dict[str, Any]]:
        return self.db.fetch_all("SELECT code, name FROM roles ORDER BY name")

    def has_permission(self, user: dict[str, Any], permission: str) -> bool:
        return permission in user.get("permissions", [])

    def change_password(self, user_id: int, new_password: str, changed_by: int | None = None) -> None:
        password_hash = hash_password(new_password)
        self.db.execute(
            """
            UPDATE users
            SET password_hash = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE id = ?
            """,
            (password_hash, changed_by, user_id),
        )
        self.db.execute(
            "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, description) VALUES (?, ?, ?, ?, ?)",
            (changed_by, "change_password", "user", user_id, f"Đổi mật khẩu người dùng id={user_id}"),
        )

    def delete_user(self, user_id: int, deleted_by: int | None = None) -> None:
        # hard-delete user với xử lý FOREIGN KEY constraints
        with self.db.transaction():
            # Ghi log trước khi xóa
            self.db.execute(
                "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, description) VALUES (?, ?, ?, ?, ?)",
                (deleted_by, "delete_user", "user", user_id, f"Xóa người dùng id={user_id}"),
            )
            
            # Xóa/cập nhật các tham chiếu từ bảng khác
            # 1. Cập nhật audit_logs (set user_id = NULL)
            self.db.execute(
                "UPDATE audit_logs SET user_id = NULL WHERE user_id = ?",
                (user_id,),
            )
            
            # 2. Cập nhật receipts (set created_by = NULL)
            self.db.execute(
                "UPDATE receipts SET created_by = NULL WHERE created_by = ?",
                (user_id,),
            )
            
            # 3. Cập nhật inventory (set updated_by = NULL)
            self.db.execute(
                "UPDATE inventory SET updated_by = NULL WHERE updated_by = ?",
                (user_id,),
            )
            
            # 4. Cập nhật products (set created_by, updated_by = NULL)
            self.db.execute(
                "UPDATE products SET created_by = NULL WHERE created_by = ?",
                (user_id,),
            )
            self.db.execute(
                "UPDATE products SET updated_by = NULL WHERE updated_by = ?",
                (user_id,),
            )
            
            # 5. Cập nhật users table (set created_by, updated_by = NULL)
            self.db.execute(
                "UPDATE users SET created_by = NULL WHERE created_by = ?",
                (user_id,),
            )
            self.db.execute(
                "UPDATE users SET updated_by = NULL WHERE updated_by = ?",
                (user_id,),
            )
            
            # Cuối cùng, xóa người dùng
            self.db.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,),
            )
