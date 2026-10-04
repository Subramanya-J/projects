import unittest
import os
from engine.db import init_schema
from engine.inventory import InventoryManager
from engine.dispatch import DispatchWorkflowEngine
from engine.reconciliation import InventoryAuditRunner

TEST_DB = "test_logistics.db"

class TestLogisticsEngine(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_schema(TEST_DB)
        self.inv = InventoryManager(TEST_DB)
        self.disp = DispatchWorkflowEngine(TEST_DB)
        self.audit = InventoryAuditRunner(TEST_DB)

        # Seed catalog
        self.inv.add_product("SKU-100", "CAN Transceiver IC", "Semiconductors", 120.0, 10)
        self.inv.restock("W-NORTH", "SKU-100", 50)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_stock_reservation_and_fulfillment(self):
        stock = self.inv.get_stock_level("W-NORTH", "SKU-100")
        self.assertEqual(stock["on_hand"], 50)
        self.assertEqual(stock["available"], 50)

        # Create order
        self.disp.create_order("ORD-TEST-1", "Dexcel Client", "HUB-1", [
            {"sku": "SKU-100", "qty": 20}
        ])
        
        # Allocate
        res = self.disp.allocate_order("ORD-TEST-1", "W-NORTH")
        self.assertTrue(res)

        stock_after_alloc = self.inv.get_stock_level("W-NORTH", "SKU-100")
        self.assertEqual(stock_after_alloc["reserved"], 20)
        self.assertEqual(stock_after_alloc["available"], 30)

        # Dispatch
        disp_res = self.disp.dispatch_order("ORD-TEST-1")
        self.assertTrue(disp_res)

        stock_final = self.inv.get_stock_level("W-NORTH", "SKU-100")
        self.assertEqual(stock_final["on_hand"], 30)
        self.assertEqual(stock_final["reserved"], 0)

    def test_over_allocation_prevention(self):
        # Request more than on-hand stock
        self.disp.create_order("ORD-OVERFLOW", "Heavy Demand Ltd", "HUB-2", [
            {"sku": "SKU-100", "qty": 100}
        ])
        res = self.disp.allocate_order("ORD-OVERFLOW", "W-NORTH")
        self.assertFalse(res)

    def test_audit_discrepancy_alert(self):
        # 50 on-hand, physical count is 42 (missing 8 units)
        res = self.audit.audit_physical_count("W-NORTH", "SKU-100", physical_count=42)
        self.assertTrue(res["discrepancy_flagged"])
        self.assertEqual(res["variance"], -8)
        self.assertEqual(res["severity"], "MEDIUM")

if __name__ == "__main__":
    unittest.main()
