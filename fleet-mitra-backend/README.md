# BSP FleetMitra - Fleet Management & Telematics Platform

A high-performance backend microservice engineered in **Python (FastAPI)** and **SQLAlchemy** designed to manage commercial transport fleets, operational vehicle inspections, and continuous GPS/sensor telemetry streams.

---

## Key Engineering Capabilities
- **RESTful API Service:** Asynchronous endpoints built on FastAPI with Pydantic request/response schema validation.
- **Relational Data Persistence:** Structured relational entities for `Vehicles`, `InspectionLogs`, and `TelemetryRecords` with foreign-key constraints.
- **Automated Vehicle Health Logic:** Automated state switching (e.g. `active` -> `maintenance`) when critical safety thresholds or inspection criteria fail.
- **Continuous Telemetry Ingestion:** Validated intake for high-frequency GPS coordinates, vehicle speed, fuel metrics, and engine thermal readings.
- **Containerized Deployment:** Includes `Dockerfile` and `docker-compose.yml` configurations for deployment to modern container hosts.

---

## Tech Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI, Uvicorn
- **ORM / Database:** SQLAlchemy (SQLite default / PostgreSQL compatible)
- **Validation:** Pydantic v2
- **Testing:** PyTest, HTTPX TestClient
- **Containerization:** Docker, Docker Compose

---

## Directory Structure
```
fleet-mitra-backend/
├── app/
│   ├── __init__.py
│   ├── database.py       # Engine & session management
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic schemas & validation rules
│   └── main.py           # FastAPI routes & lifecycle
├── tests/
│   └── test_fleet_api.py # Automated integration tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Quickstart Guide

### 1. Local Setup
```bash
# Clone the repository
git clone https://github.com/Subramanya-J/projects.git
cd projects/fleet-mitra-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --port 8000
```
Visit the interactive Swagger UI at **http://localhost:8000/docs**.

### 2. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 3. Docker Deployment
```bash
docker compose up --build -d
```
