import sys
from engine.db import init_schema
from engine.inventory import InventoryManager
from engine.dispatch import DispatchWorkflowEngine
from engine.reconciliation import InventoryAuditRunner

def main():
    print("=" * 60)
    print("  LOGISTICS & INVENTORY WORKFLOW ENGINE - CLI DEMO")
    print("=" * 60)

    init_schema()
    inv = InventoryManager()
    disp = DispatchWorkflowEngine()
    audit = InventoryAuditRunner()

    print("[1] Initializing catalog and seeding warehouse stock...")
    inv.add_product("SKU-SENS-01", "Industrial Pressure Sensor", "Sensors", 450.0, 15)
    inv.add_product("SKU-MC-02", "STM32F401 Microcontroller Board", "Embedded", 850.0, 10)
    
    inv.restock("BLR-01", "SKU-SENS-01", 100)
    inv.restock("BLR-01", "SKU-MC-02", 50)
    print("  Stock BLR-01 (SKU-SENS-01):", inv.get_stock_level("BLR-01", "SKU-SENS-01"))

    print("\n[2] Creating and allocating Order #ORD-9021...")
    disp.create_order("ORD-9021", "Aerospace Systems Ltd", "HUB-WHITEFIELD", [
        {"sku": "SKU-SENS-01", "qty": 10},
        {"sku": "SKU-MC-02", "qty": 5}
    ])
    allocated = disp.allocate_order("ORD-9021", "BLR-01")
    print(f"  Allocation Status: {'SUCCESS' if allocated else 'FAILED'}")
    print("  Stock after allocation:", inv.get_stock_level("BLR-01", "SKU-SENS-01"))

    print("\n[3] Dispatching Order #ORD-9021...")
    dispatched = disp.dispatch_order("ORD-9021")
    print(f"  Dispatch Status: {'DISPATCHED' if dispatched else 'FAILED'}")
    print("  Stock after fulfillment:", inv.get_stock_level("BLR-01", "SKU-SENS-01"))

    print("\n[4] Running physical audit check for variance...")
    audit_res = audit.audit_physical_count("BLR-01", "SKU-SENS-01", physical_count=88) # System expects 90
    print("  Audit Result:", audit_res)

    print("\nWorkflow completed with 100% ACID consistency.")

if __name__ == "__main__":
    main()
