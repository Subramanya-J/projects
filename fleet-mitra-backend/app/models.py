from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String(50), unique=True, index=True, nullable=False)
    license_plate = Column(String(20), unique=True, index=True, nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String(20), default="active")  # active, maintenance, inactive
    current_odometer_km = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspections = relationship("InspectionLog", back_populates="vehicle", cascade="all, delete-orphan")
    telemetry_logs = relationship("TelemetryRecord", back_populates="vehicle", cascade="all, delete-orphan")


class InspectionLog(Base):
    __tablename__ = "inspection_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    inspector_name = Column(String(100), nullable=False)
    inspection_date = Column(DateTime, default=datetime.utcnow)
    brakes_ok = Column(Boolean, default=True)
    tires_ok = Column(Boolean, default=True)
    engine_oil_ok = Column(Boolean, default=True)
    lights_ok = Column(Boolean, default=True)
    passed = Column(Boolean, default=True)
    remarks = Column(Text, nullable=True)

    vehicle = relationship("Vehicle", back_populates="inspections")


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed_kmh = Column(Float, nullable=False)
    fuel_pct = Column(Float, nullable=False)
    engine_temp_c = Column(Float, nullable=False)

    vehicle = relationship("Vehicle", back_populates="telemetry_logs")
