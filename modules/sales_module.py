from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sieu_thi_mini_app.database.db import Database


@dataclass(frozen=True)
class InvoiceItem:
    product_id: int
    quantity: int
    unit_price: float


class SalesModule:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _generate_invoice_no(self) -> str:
        date_code = datetime.now().strftime("%Y%m%d")
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS total FROM invoices WHERE DATE(created_at) = DATE('now')",
            (),
        )
        sequence = int(row["total"] or 0) + 1
        return f"INV{date_code}-{sequence:03d}"

    def create_invoice(
        self,
        cashier_id: int,
        items: list[InvoiceItem],
        discount_amount: float,
        payment_method: str,
        payment_amount: float,
    ) -> int:
        if not items:
            raise ValueError("Giỏ hàng trống")
        subtotal = sum(item.quantity * item.unit_price for item in items)
        if discount_amount < 0 or discount_amount > subtotal:
            raise ValueError("Chiết khấu không hợp lệ")
        total_amount = subtotal - discount_amount
        if payment_amount < total_amount:
            raise ValueError("Số tiền thanh toán chưa đủ")

        invoice_no = self._generate_invoice_no()
        with self.db.transaction():
            cursor = self.db.execute(
                """
                INSERT INTO invoices (invoice_no, cashier_id, subtotal, discount_amount, total_amount, status)
                VALUES (?, ?, ?, ?, ?, 'paid')
                """,
                (invoice_no, cashier_id, subtotal, discount_amount, total_amount),
            )
            invoice_id = int(cursor.lastrowid)
            self.db.execute_many(
                """
                INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (invoice_id, item.product_id, item.quantity, item.unit_price, item.quantity * item.unit_price)
                    for item in items
                ],
            )
            for item in items:
                current = self.db.fetch_one(
                    "SELECT quantity FROM inventory WHERE product_id = ?",
                    (item.product_id,),
                )
                current_quantity = int(current["quantity"] if current else 0)
                remaining = current_quantity - item.quantity
                if remaining < 0:
                    raise ValueError("Tồn kho không đủ")
                self.db.execute(
                    "UPDATE inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?",
                    (remaining, item.product_id),
                )
            self.db.execute(
                "INSERT INTO payments (invoice_id, method, amount) VALUES (?, ?, ?)",
                (invoice_id, payment_method.strip(), payment_amount),
            )
        return invoice_id

    def list_invoices(self, search: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT id, invoice_no, subtotal, discount_amount, total_amount, status, created_at
            FROM invoices
            """
        params: list[Any] = []
        if search:
            query += " WHERE invoice_no LIKE ?"
            params.append(f"%{search}%")
        query += " ORDER BY created_at DESC"
        return self.db.fetch_all(query, params)

    def get_invoice_by_id(self, invoice_id: int) -> dict[str, Any] | None:
        return self.db.fetch_one(
            """
            SELECT id, invoice_no, cashier_id, subtotal, discount_amount, total_amount, status, created_at
            FROM invoices
            WHERE id = ?
            """,
            (invoice_id,),
        )

    def get_invoice_items(self, invoice_id: int) -> list[dict[str, Any]]:
        return self.db.fetch_all(
            """
            SELECT ii.product_id,
                   p.sku,
                   p.name AS product_name,
                   ii.quantity,
                   ii.unit_price,
                   ii.line_total
            FROM invoice_items ii
            JOIN products p ON p.id = ii.product_id
            WHERE ii.invoice_id = ?
            """,
            (invoice_id,),
        )
