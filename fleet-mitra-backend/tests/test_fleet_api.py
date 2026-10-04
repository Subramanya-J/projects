import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_create_and_get_vehicle():
    payload = {
        "vin": "VINTEST999888777",
        "license_plate": "KA-04-AB-1234",
        "make": "Ashok Leyland",
        "model": "Dost+",
        "year": 2023,
        "current_odometer_km": 15200.5
    }
    res = client.post("/api/v1/vehicles", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["vin"] == payload["vin"]
    v_id = data["id"]

    # Verify Retrieval
    get_res = client.get(f"/api/v1/vehicles/{v_id}")
    assert get_res.status_code == 200
    assert get_res.json()["license_plate"] == payload["license_plate"]

def test_inspection_pass_and_fail():
    # 1. Create vehicle
    v_res = client.post("/api/v1/vehicles", json={
        "vin": "VININSPECT12345",
        "license_plate": "KA-20-ZZ-4321",
        "make": "Tata",
        "model": "Intra",
        "year": 2022
    })
    v_id = v_res.json()["id"]

    # 2. Passed Inspection
    insp_pass = client.post("/api/v1/inspections", json={
        "vehicle_id": v_id,
        "inspector_name": "Senior Inspector Ramesh",
        "brakes_ok": True,
        "tires_ok": True,
        "engine_oil_ok": True,
        "lights_ok": True,
        "remarks": "Clean pass"
    })
    assert insp_pass.status_code == 201
    assert insp_pass.json()["passed"] is True

    # 3. Failed Inspection -> triggers maintenance
    insp_fail = client.post("/api/v1/inspections", json={
        "vehicle_id": v_id,
        "inspector_name": "Senior Inspector Ramesh",
        "brakes_ok": False,
        "tires_ok": True,
        "engine_oil_ok": True,
        "lights_ok": True,
        "remarks": "Brake pad worn out"
    })
    assert insp_fail.status_code == 201
    assert insp_fail.json()["passed"] is False

    # Check vehicle status changed
    updated_v = client.get(f"/api/v1/vehicles/{v_id}").json()
    assert updated_v["status"] == "maintenance"

def test_telemetry_ingest():
    v_res = client.post("/api/v1/vehicles", json={
        "vin": "VINTELEM98765",
        "license_plate": "KA-19-XY-9876",
        "make": "Eicher",
        "model": "Pro 2049",
        "year": 2024
    })
    v_id = v_res.json()["id"]

    telem_payload = {
        "vehicle_id": v_id,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "speed_kmh": 48.5,
        "fuel_pct": 82.0,
        "engine_temp_c": 88.0
    }
    t_res = client.post("/api/v1/telemetry", json=telem_payload)
    assert t_res.status_code == 201
    assert t_res.json()["speed_kmh"] == 48.5

    # Get latest
    latest_res = client.get(f"/api/v1/telemetry/{v_id}/latest")
    assert latest_res.status_code == 200
    assert latest_res.json()["engine_temp_c"] == 88.0
