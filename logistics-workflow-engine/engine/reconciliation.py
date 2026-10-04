from engine.db import get_db_connection

class InventoryAuditRunner:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def audit_physical_count(self, warehouse: str, sku: str, physical_count: int) -> dict:
        """Compares physical warehouse audit counts against system ledgers."""
        with get_db_connection(self.db_path) as conn:
            with conn:
                row = conn.execute(
                    "SELECT quantity_on_hand FROM inventory WHERE warehouse_code = ? AND sku = ?",
                    (warehouse, sku)
                ).fetchone()

                system_count = row["quantity_on_hand"] if row else 0
                variance = physical_count - system_count

                if variance == 0:
                    severity = "NONE"
                elif abs(variance) < 5:
                    severity = "LOW"
                elif abs(variance) <= 20:
                    severity = "MEDIUM"
                else:
                    severity = "CRITICAL"

                cursor = conn.execute('''
                    INSERT INTO discrepancy_audit_log
                    (warehouse_code, sku, system_count, physical_count, variance, severity)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (warehouse, sku, system_count, physical_count, variance, severity))

                return {
                    "audit_id": cursor.lastrowid,
                    "warehouse": warehouse,
                    "sku": sku,
                    "system_count": system_count,
                    "physical_count": physical_count,
                    "variance": variance,
                    "severity": severity,
                    "discrepancy_flagged": variance != 0
                }

    def get_audit_summary(self):
        with get_db_connection(self.db_path) as conn:
            rows = conn.execute('''
                SELECT severity, count(*) as count
                FROM discrepancy_audit_log
                GROUP BY severity
            ''').fetchall()
            return {r["severity"]: r["count"] for r in rows}
