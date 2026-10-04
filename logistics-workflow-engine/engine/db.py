import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv("LOGISTICS_DB_PATH", "logistics.db")

@contextmanager
def get_db_connection(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()

def init_schema(db_path=None):
    with get_db_connection(db_path) as conn:
        with conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS products (
                    sku TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    reorder_threshold INTEGER NOT NULL DEFAULT 20
                );

                CREATE TABLE IF NOT EXISTS inventory (
                    warehouse_code TEXT NOT NULL,
                    sku TEXT NOT NULL,
                    quantity_on_hand INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
                    quantity_reserved INTEGER NOT NULL DEFAULT 0 CHECK (quantity_reserved >= 0),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (warehouse_code, sku),
                    FOREIGN KEY (sku) REFERENCES products(sku)
                );

                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    destination_hub TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, ALLOCATED, DISPATCHED, CANCELLED
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    order_id TEXT NOT NULL,
                    sku TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    allocated_warehouse TEXT,
                    PRIMARY KEY (order_id, sku),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (sku) REFERENCES products(sku)
                );

                CREATE TABLE IF NOT EXISTS discrepancy_audit_log (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    warehouse_code TEXT NOT NULL,
                    sku TEXT NOT NULL,
                    system_count INTEGER NOT NULL,
                    physical_count INTEGER NOT NULL,
                    variance INTEGER NOT NULL,
                    severity TEXT NOT NULL, -- LOW, MEDIUM, CRITICAL
                    audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
