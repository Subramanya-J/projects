from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class VehicleCreate(BaseModel):
    vin: str = Field(..., example="1HGCR2F83HA123456")
    license_plate: str = Field(..., example="KA-01-MJ-9999")
    make: str = Field(..., example="Tata")
    model: str = Field(..., example="Ace Gold")
    year: int = Field(..., ge=2000, le=2030, example=2023)
    current_odometer_km: Optional[float] = 0.0

class VehicleResponse(VehicleCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class InspectionCreate(BaseModel):
    vehicle_id: int
    inspector_name: str
    brakes_ok: bool = True
    tires_ok: bool = True
    engine_oil_ok: bool = True
    lights_ok: bool = True
    remarks: Optional[str] = None

class InspectionResponse(InspectionCreate):
    id: int
    inspection_date: datetime
    passed: bool

    class Config:
        from_attributes = True

class TelemetryIngest(BaseModel):
    vehicle_id: int
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    speed_kmh: float = Field(..., ge=0.0, le=250.0)
    fuel_pct: float = Field(..., ge=0.0, le=100.0)
    engine_temp_c: float = Field(..., ge=-40.0, le=150.0)

class TelemetryResponse(TelemetryIngest):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class FleetSummary(BaseModel):
    total_vehicles: int
    active_vehicles: int
    maintenance_vehicles: int
    total_inspections: int
    fleet_health_score_pct: float
