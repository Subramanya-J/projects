from engine.db import get_db_connection
from engine.inventory import InventoryManager

class DispatchWorkflowEngine:
    def __init__(self, db_path=None):
        self.db_path = db_path
        self.inv = InventoryManager(db_path)

    def create_order(self, order_id: str, customer: str, destination: str, items: list[dict]):
        with get_db_connection(self.db_path) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO orders (order_id, customer_name, destination_hub, status) VALUES (?, ?, ?, 'PENDING')",
                    (order_id, customer, destination)
                )
                for itm in items:
                    conn.execute(
                        "INSERT INTO order_items (order_id, sku, quantity) VALUES (?, ?, ?)",
                        (order_id, itm["sku"], itm["qty"])
                    )

    def allocate_order(self, order_id: str, preferred_warehouse: str = "BLR-01") -> bool:
        """Attempts to allocate all items in the order from the warehouse."""
        with get_db_connection(self.db_path) as conn:
            with conn:
                items = conn.execute(
                    "SELECT sku, quantity FROM order_items WHERE order_id = ?",
                    (order_id,)
                ).fetchall()
                if not items:
                    return False

                # Verify availability for all items before reserving
                for row in items:
                    stock = self.inv.get_stock_level(preferred_warehouse, row["sku"])
                    if not stock or stock["available"] < row["quantity"]:
                        return False

                # Reserve stock atomically
                for row in items:
                    success = self.inv.reserve_stock_atomic(preferred_warehouse, row["sku"], row["quantity"])
                    if not success:
                        raise RuntimeError(f"Race condition encountered reserving {row['sku']}")
                    conn.execute(
                        "UPDATE order_items SET allocated_warehouse = ? WHERE order_id = ? AND sku = ?",
                        (preferred_warehouse, order_id, row["sku"])
                    )

                conn.execute("UPDATE orders SET status = 'ALLOCATED' WHERE order_id = ?", (order_id,))
                return True

    def dispatch_order(self, order_id: str) -> bool:
        """Finalizes fulfillment: deducts both on_hand and reserved stock atomically."""
        with get_db_connection(self.db_path) as conn:
            with conn:
                order = conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
                if not order or order["status"] != "ALLOCATED":
                    return False

                items = conn.execute(
                    "SELECT sku, quantity, allocated_warehouse FROM order_items WHERE order_id = ?",
                    (order_id,)
                ).fetchall()

                for row in items:
                    conn.execute('''
                        UPDATE inventory
                        SET quantity_on_hand = quantity_on_hand - ?,
                            quantity_reserved = quantity_reserved - ?,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE warehouse_code = ? AND sku = ?
                    ''', (row["quantity"], row["quantity"], row["allocated_warehouse"], row["sku"]))

                conn.execute("UPDATE orders SET status = 'DISPATCHED' WHERE order_id = ?", (order_id,))
                return True
