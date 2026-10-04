# Automated Logistics & Inventory Workflow Engine

An ACID-compliant backend transactional inventory engine engineered in **Python** and **SQL**, designed for automated stock reservation, multi-warehouse dispatch allocation, and discrepancy ledger auditing.

---

## Key Engineering Capabilities
- **Transactional Stock Management:** Atomic two-phase stock reservation (`reserve` -> `dispatch`) preventing race conditions and inventory overselling.
- **Automated Dispatch Routing:** Fulfills multi-item orders against warehouse availability with automatic allocation rollbacks on shortfall.
- **Audit & Variance Engine:** Automates variance reconciliation between physical warehouse scans and system ledgers, assigning severity levels (`LOW`, `MEDIUM`, `CRITICAL`).
- **Comprehensive Unit Testing:** Integrated standard `unittest` test suite validating concurrency constraints and edge cases.

---

## Tech Stack
- **Language:** Python 3.10+
- **Database:** SQLite / PostgreSQL (relational schemas with strict foreign keys & check constraints)
- **Architecture:** Modular Engine (Inventory, Dispatch, Reconciliation)
- **Testing:** Python `unittest` framework

---

## Directory Structure
```
logistics-workflow-engine/
├── engine/
│   ├── __init__.py
│   ├── db.py               # Database schemas & connection manager
│   ├── inventory.py        # Atomic stock management
│   ├── dispatch.py         # Order allocation & dispatch workflow
│   └── reconciliation.py   # Physical audit & variance detection
├── tests/
│   └── test_engine.py      # Automated unit tests
├── cli.py                  # Interactive CLI simulation runner
├── requirements.txt
└── README.md
```

---

## Quickstart Guide

### 1. Run the Interactive Simulation
```bash
# Clone the repository
git clone https://github.com/Subramanya-J/projects.git
cd projects/logistics-workflow-engine

# Execute the CLI workflow runner
python cli.py
```

### 2. Run the Automated Test Suite
```bash
python -m unittest tests/test_engine.py -v
```
