from __future__ import annotations

from typing import Any

from sieu_thi_mini_app.database.db import Database


class ProductModule:
    def __init__(self, db: Database) -> None:
        self.db = db

    def list_categories(self, active_only: bool = True) -> list[dict[str, Any]]:
        query = "SELECT id, code, name, description, is_active FROM categories"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        return self.db.fetch_all(query)

    def create_category(self, code: str, name: str, description: str | None) -> int:
        cursor = self.db.execute(
            "INSERT INTO categories (code, name, description, is_active) VALUES (?, ?, ?, 1)",
            (code.strip().upper(), name.strip(), description),
        )
        return int(cursor.lastrowid)

    def update_category(self, category_id: int, name: str, description: str | None, is_active: bool) -> None:
        self.db.execute(
            "UPDATE categories SET name = ?, description = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name.strip(), description, int(is_active), category_id),
        )

    def list_products(self, search: str | None = None, active_only: bool = True) -> list[dict[str, Any]]:
        query = """
            SELECT p.id,
                   p.sku,
                   p.barcode,
                   p.name,
                   c.name AS category,
                   p.unit,
                   p.cost_price,
                   p.sale_price,
                   p.min_stock,
                   p.is_active,
                   IFNULL(i.quantity, 0) AS quantity
            FROM products p
            JOIN categories c ON c.id = p.category_id
            LEFT JOIN inventory i ON i.product_id = p.id
            """
        params: list[Any] = []
        where_clauses: list[str] = []
        if active_only:
            where_clauses.append("p.is_active = 1")
        if search:
            where_clauses.append("(p.sku LIKE ? OR p.name LIKE ? OR c.name LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " ORDER BY p.name"
        return self.db.fetch_all(query, params)

    def get_product(self, product_id: int) -> dict[str, Any] | None:
        return self.db.fetch_one(
            """
            SELECT p.id,
                   p.sku,
                   p.barcode,
                   p.name,
                   p.category_id,
                   c.name AS category,
                   p.unit,
                   p.cost_price,
                   p.sale_price,
                   p.min_stock,
                   p.is_active,
                   IFNULL(i.quantity, 0) AS quantity
            FROM products p
            JOIN categories c ON c.id = p.category_id
            LEFT JOIN inventory i ON i.product_id = p.id
            WHERE p.id = ?
            """,
            (product_id,),
        )

    def create_product(
        self,
        sku: str,
        barcode: str | None,
        name: str,
        category_id: int,
        unit: str,
        cost_price: float,
        sale_price: float,
        min_stock: int,
    ) -> int:
        cursor = self.db.execute(
            """
            INSERT INTO products (sku, barcode, name, category_id, unit, cost_price, sale_price, min_stock, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (sku.strip(), barcode, name.strip(), category_id, unit.strip(), cost_price, sale_price, min_stock),
        )
        product_id = int(cursor.lastrowid)
        self.db.execute(
            "INSERT OR IGNORE INTO inventory (product_id, quantity, updated_by) VALUES (?, 0, NULL)",
            (product_id,),
        )
        return product_id

    def update_product(
        self,
        product_id: int,
        sku: str,
        barcode: str | None,
        name: str,
        category_id: int,
        unit: str,
        cost_price: float,
        sale_price: float,
        min_stock: int,
        is_active: bool,
    ) -> None:
        self.db.execute(
            """
            UPDATE products
            SET sku = ?,
                barcode = ?,
                name = ?,
                category_id = ?,
                unit = ?,
                cost_price = ?,
                sale_price = ?,
                min_stock = ?,
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                sku.strip(),
                barcode,
                name.strip(),
                category_id,
                unit.strip(),
                cost_price,
                sale_price,
                min_stock,
                int(is_active),
                product_id,
            ),
        )

    def list_inventory(self, low_stock_only: bool = False) -> list[dict[str, Any]]:
        query = """
            SELECT p.id,
                   p.sku,
                   p.name,
                   IFNULL(i.quantity, 0) AS quantity,
                   p.min_stock,
                   p.sale_price
            FROM products p
            LEFT JOIN inventory i ON i.product_id = p.id
            WHERE p.is_active = 1
            """
        if low_stock_only:
            query += " AND IFNULL(i.quantity, 0) <= p.min_stock"
        query += " ORDER BY p.name"
        return self.db.fetch_all(query)

    def set_inventory_quantity(self, product_id: int, quantity: int, updated_by: int | None = None) -> None:
        self.db.execute(
            """
            INSERT INTO inventory (product_id, quantity, updated_at, updated_by)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
            ON CONFLICT(product_id) DO UPDATE SET quantity = excluded.quantity, updated_at = excluded.updated_at, updated_by = excluded.updated_by
            """,
            (product_id, quantity, updated_by),
        )

    def delete_product(self, product_id: int, deleted_by: int | None = None) -> None:
        # soft-delete product
        self.db.execute(
            "UPDATE products SET is_active = 0, updated_at = CURRENT_TIMESTAMP, updated_by = ? WHERE id = ?",
            (deleted_by, product_id),
        )
        self.db.execute(
            "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, description) VALUES (?, ?, ?, ?, ?)",
            (deleted_by, "delete_product", "product", product_id, f"Xóa sản phẩm id={product_id}"),
        )
