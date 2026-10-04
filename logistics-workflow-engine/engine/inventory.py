from engine.db import get_db_connection

class InventoryManager:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def add_product(self, sku: str, name: str, category: str, unit_price: float, threshold: int = 20):
        with get_db_connection(self.db_path) as conn:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO products (sku, name, category, unit_price, reorder_threshold) VALUES (?, ?, ?, ?, ?)",
                    (sku, name, category, unit_price, threshold)
                )

    def restock(self, warehouse: str, sku: str, quantity: int):
        if quantity <= 0:
            raise ValueError("Restock quantity must be positive")
        with get_db_connection(self.db_path) as conn:
            with conn:
                conn.execute('''
                    INSERT INTO inventory (warehouse_code, sku, quantity_on_hand, quantity_reserved)
                    VALUES (?, ?, ?, 0)
                    ON CONFLICT(warehouse_code, sku) DO UPDATE SET
                    quantity_on_hand = quantity_on_hand + excluded.quantity_on_hand,
                    last_updated = CURRENT_TIMESTAMP
                ''', (warehouse, sku, quantity))

    def get_stock_level(self, warehouse: str, sku: str):
        with get_db_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT quantity_on_hand, quantity_reserved FROM inventory WHERE warehouse_code = ? AND sku = ?",
                (warehouse, sku)
            ).fetchone()
            if row:
                return {
                    "on_hand": row["quantity_on_hand"],
                    "reserved": row["quantity_reserved"],
                    "available": row["quantity_on_hand"] - row["quantity_reserved"]
                }
            return None

    def reserve_stock_atomic(self, warehouse: str, sku: str, qty: int) -> bool:
        """Atomic stock reservation with strict check to prevent overselling."""
        with get_db_connection(self.db_path) as conn:
            with conn:
                cursor = conn.execute('''
                    UPDATE inventory
                    SET quantity_reserved = quantity_reserved + ?
                    WHERE warehouse_code = ? AND sku = ?
                      AND (quantity_on_hand - quantity_reserved) >= ?
                ''', (qty, warehouse, sku, qty))
                return cursor.rowcount > 0
