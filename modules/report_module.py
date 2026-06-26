from __future__ import annotations

from typing import Any

from sieu_thi_mini_app.database.db import Database


class ReportModule:
    def __init__(self, db: Database) -> None:
        self.db = db

    def revenue_report(self, start_date: str | None = None, end_date: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT id, invoice_no, total_amount, status, created_at FROM invoices"
        params: list[Any] = []
        if start_date or end_date:
            query += " WHERE 1=1"
            if start_date:
                query += " AND DATE(created_at) >= DATE(?)"
                params.append(start_date)
            if end_date:
                query += " AND DATE(created_at) <= DATE(?)"
                params.append(end_date)
        query += " ORDER BY created_at DESC"
        return self.db.fetch_all(query, params)

    def best_selling_report(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.db.fetch_all(
            """
            SELECT p.sku,
                   p.name,
                   SUM(ii.quantity) AS total_quantity,
                   SUM(ii.line_total) AS total_revenue
            FROM invoice_items ii
            JOIN products p ON p.id = ii.product_id
            GROUP BY p.id
            ORDER BY total_quantity DESC
            LIMIT ?
            """,
            (limit,),
        )

    def inventory_report(self, low_stock_only: bool = False) -> list[dict[str, Any]]:
        query = """
            SELECT p.sku,
                   p.name,
                   IFNULL(i.quantity, 0) AS quantity,
                   p.min_stock,
                   CASE WHEN IFNULL(i.quantity, 0) <= p.min_stock THEN 1 ELSE 0 END AS low_stock
            FROM products p
            LEFT JOIN inventory i ON i.product_id = p.id
            WHERE p.is_active = 1
            """
        if low_stock_only:
            query += " AND IFNULL(i.quantity, 0) <= p.min_stock"
        query += " ORDER BY p.name"
        return self.db.fetch_all(query)
