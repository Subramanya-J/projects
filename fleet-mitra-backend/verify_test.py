
import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Health check
res = client.get("/health")
assert res.status_code == 200, f"Health check failed: {res.status_code}"
assert res.json()["status"] == "online"

# 2. Vehicle creation
res = client.post("/api/v1/vehicles", json={
    "vin": "VIN_VERIFY_001",
    "license_plate": "KA-01-AB-1111",
    "make": "Tata",
    "model": "Ace",
    "year": 2023,
    "current_odometer_km": 1000.0
})
assert res.status_code == 201, f"Vehicle creation failed: {res.text}"
v_id = res.json()["id"]

# 3. Inspection
res = client.post("/api/v1/inspections", json={
    "vehicle_id": v_id,
    "inspector_name": "Ramesh",
    "brakes_ok": True,
    "tires_ok": True,
    "engine_oil_ok": True,
    "lights_ok": True
})
assert res.status_code == 201
assert res.json()["passed"] is True

# 4. Telemetry ingest
res = client.post("/api/v1/telemetry", json={
    "vehicle_id": v_id,
    "latitude": 12.9716,
    "longitude": 77.5946,
    "speed_kmh": 45.0,
    "fuel_pct": 90.0,
    "engine_temp_c": 85.0
})
assert res.status_code == 201
assert res.json()["speed_kmh"] == 45.0

# 5. Fleet summary analytics
res = client.get("/api/v1/analytics/fleet-status")
assert res.status_code == 200
assert res.json()["total_vehicles"] >= 1

print("Project 1: Verified and operational!")
