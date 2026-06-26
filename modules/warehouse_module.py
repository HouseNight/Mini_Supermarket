from __future__ import annotations
from datetime import datetime
from typing import Any

from sieu_thi_mini_app.database.db import Database


class WarehouseModule:
    def __init__(self, db: Database) -> None:
        self.db = db

    def list_suppliers(self) -> list[dict[str, Any]]:
        return self.db.fetch_all(
            "SELECT id, code, name, phone, email, address, is_active FROM suppliers WHERE is_active = 1 ORDER BY name"
        )

    def create_supplier(self, code: str, name: str, phone: str | None, email: str | None, address: str | None) -> int:
        cursor = self.db.execute(
            "INSERT INTO suppliers (code, name, phone, email, address, is_active) VALUES (?, ?, ?, ?, ?, 1)",
            (code.strip().upper(), name.strip(), phone, email, address),
        )
        return int(cursor.lastrowid)

    def list_receipts(self) -> list[dict[str, Any]]:
        return self.db.fetch_all(
            """
            SELECT r.id,
                   r.receipt_no,
                   s.name AS supplier,
                   r.total_amount,
                   r.note,
                   r.created_at
            FROM receipts r
            LEFT JOIN suppliers s ON s.id = r.supplier_id
            ORDER BY r.created_at DESC
            """
        )

    def create_receipt(self, supplier_id: int | None, total_amount: float, note: str | None) -> int:
        cursor = self.db.execute(
            "INSERT INTO receipts (receipt_no, supplier_id, total_amount, note) VALUES (?, ?, ?, ?)",
            (self._generate_receipt_no(), supplier_id, total_amount, note),
        )
        return int(cursor.lastrowid)

    def create_receipt_with_items(self, supplier_id: int | None, items: list[dict[str, Any]], created_by: int | None = None, note: str | None = None) -> int:
        if not items:
            raise ValueError("Không có mặt hàng để nhập")
        total = sum(int(it["quantity"]) * float(it["unit_cost"]) for it in items)
        receipt_no = self._generate_receipt_no()
        with self.db.transaction():
            cursor = self.db.execute(
                "INSERT INTO receipts (receipt_no, supplier_id, created_by, total_amount, note) VALUES (?, ?, ?, ?, ?)",
                (receipt_no, supplier_id, created_by, total, note),
            )
            receipt_id = int(cursor.lastrowid)
            self.db.execute_many(
                "INSERT INTO receipt_items (receipt_id, product_id, quantity, unit_cost) VALUES (?, ?, ?, ?)",
                [(receipt_id, int(it["product_id"]), int(it["quantity"]), float(it["unit_cost"])) for it in items],
            )
            for it in items:
                pid = int(it["product_id"])
                q = int(it["quantity"])
                current = self.db.fetch_one("SELECT quantity FROM inventory WHERE product_id = ?", (pid,))
                current_q = int(current["quantity"]) if current else 0
                new_q = current_q + q
                self.db.execute(
                    "INSERT INTO inventory (product_id, quantity, updated_at, updated_by) VALUES (?, ?, CURRENT_TIMESTAMP, ?) ON CONFLICT(product_id) DO UPDATE SET quantity = excluded.quantity, updated_at = excluded.updated_at, updated_by = excluded.updated_by",
                    (pid, new_q, created_by),
                )
            # audit log
            self.db.execute(
                "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, description) VALUES (?, ?, ?, ?, ?)",
                (created_by, "create_receipt", "receipt", receipt_id, f"Nhập hàng {receipt_no} tổng {total:,.0f}"),
            )
        return receipt_id

    def get_receipt_items(self, receipt_id: int) -> list[dict[str, Any]]:
        return self.db.fetch_all(
            "SELECT ri.id, p.sku, p.name AS product_name, ri.quantity, ri.unit_cost FROM receipt_items ri JOIN products p ON p.id = ri.product_id WHERE ri.receipt_id = ?",
            (receipt_id,),
        )

    def list_inventory(self) -> list[dict[str, Any]]:
        return self.db.fetch_all(
            """
            SELECT p.id,
                   p.sku,
                   p.name,
                   IFNULL(i.quantity, 0) AS quantity,
                   p.min_stock,
                   p.sale_price
            FROM products p
            LEFT JOIN inventory i ON i.product_id = p.id
            ORDER BY p.name
            """
        )

    def adjust_stock(self, product_id: int, quantity: int) -> None:
        self.db.execute(
            """
            INSERT INTO inventory (product_id, quantity, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(product_id) DO UPDATE SET quantity = excluded.quantity, updated_at = excluded.updated_at
            """,
            (product_id, quantity),
        )

    def _generate_receipt_no(self) -> str:
        row = self.db.fetch_one(
        "SELECT MAX(id) AS max_id FROM receipts"
        )

        next_id = (row["max_id"] or 0) + 1

        today = datetime.now().strftime("%Y%m%d")

        return f"REC-{today}-{next_id:06d}"

    def delete_supplier(self, supplier_id: int, deleted_by: int | None = None) -> None:
        # soft-delete supplier
        self.db.execute(
            "UPDATE suppliers SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (supplier_id,),
        )
        self.db.execute(
            "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, description) VALUES (?, ?, ?, ?, ?)",
            (deleted_by, "delete_supplier", "supplier", supplier_id, f"Xóa nhà cung cấp id={supplier_id}"),
        )

