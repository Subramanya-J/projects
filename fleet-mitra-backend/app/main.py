from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import Base, engine, get_db
from app import models, schemas

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BSP FleetMitra - Telematics & Fleet Platform",
    description="Backend microservice for vehicle tracking, maintenance inspections, and high-frequency telemetry ingestion.",
    version="1.0.0"
)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "service": "BSP FleetMitra Telematics Engine",
        "version": "1.0.0"
    }

# ----------------- Vehicles -----------------
@app.post("/api/v1/vehicles", response_model=schemas.VehicleResponse, tags=["Vehicles"], status_code=201)
def create_vehicle(vehicle_in: schemas.VehicleCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Vehicle).filter(
        (models.Vehicle.vin == vehicle_in.vin) | (models.Vehicle.license_plate == vehicle_in.license_plate)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle with this VIN or License Plate already exists")
    
    vehicle = models.Vehicle(**vehicle_in.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

@app.get("/api/v1/vehicles", response_model=List[schemas.VehicleResponse], tags=["Vehicles"])
def list_vehicles(status: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Vehicle)
    if status:
        query = query.filter(models.Vehicle.status == status)
    return query.all()

@app.get("/api/v1/vehicles/{vehicle_id}", response_model=schemas.VehicleResponse, tags=["Vehicles"])
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

# ----------------- Inspections -----------------
@app.post("/api/v1/inspections", response_model=schemas.InspectionResponse, tags=["Inspections"], status_code=201)
def record_inspection(insp_in: schemas.InspectionCreate, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == insp_in.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    passed = all([insp_in.brakes_ok, insp_in.tires_ok, insp_in.engine_oil_ok, insp_in.lights_ok])
    
    inspection = models.InspectionLog(
        **insp_in.model_dump(),
        passed=passed
    )
    if not passed:
        vehicle.status = "maintenance"
    
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection

# ----------------- Telemetry -----------------
@app.post("/api/v1/telemetry", response_model=schemas.TelemetryResponse, tags=["Telemetry"], status_code=201)
def ingest_telemetry(telem_in: schemas.TelemetryIngest, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == telem_in.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    record = models.TelemetryRecord(**telem_in.model_dump())
    
    # Overheating detection
    if telem_in.engine_temp_c > 105.0:
        vehicle.status = "maintenance"
        
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@app.get("/api/v1/telemetry/{vehicle_id}/latest", response_model=schemas.TelemetryResponse, tags=["Telemetry"])
def get_latest_telemetry(vehicle_id: int, db: Session = Depends(get_db)):
    record = db.query(models.TelemetryRecord)\
        .filter(models.TelemetryRecord.vehicle_id == vehicle_id)\
        .order_by(models.TelemetryRecord.timestamp.desc())\
        .first()
    if not record:
        raise HTTPException(status_code=404, detail="No telemetry available for this vehicle")
    return record

# ----------------- Analytics -----------------
@app.get("/api/v1/analytics/fleet-status", response_model=schemas.FleetSummary, tags=["Analytics"])
def get_fleet_summary(db: Session = Depends(get_db)):
    total = db.query(models.Vehicle).count()
    active = db.query(models.Vehicle).filter(models.Vehicle.status == "active").count()
    maintenance = db.query(models.Vehicle).filter(models.Vehicle.status == "maintenance").count()
    inspections_total = db.query(models.InspectionLog).count()
    inspections_passed = db.query(models.InspectionLog).filter(models.InspectionLog.passed == True).count()
    
    health_score = (inspections_passed / inspections_total * 100.0) if inspections_total > 0 else 100.0
    
    return {
        "total_vehicles": total,
        "active_vehicles": active,
        "maintenance_vehicles": maintenance,
        "total_inspections": inspections_total,
        "fleet_health_score_pct": round(health_score, 2)
    }
