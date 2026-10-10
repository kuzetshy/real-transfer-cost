# Real Transfer Cost 💸

An open-source financial comparison platform and RESTful API that calculates the true cost of international money transfers, uncovering hidden exchange rate markups and service fees across providers.

---

## 🌟 Key Features

* **High-Precision Calculations:** Backed by native `Decimal` arithmetic to eliminate floating-point precision loss.
* **Smart Rate Caching:** In-memory `TTLCache` minimizes outbound third-party API latency.
* **Automated Data Harvesting:** Background scheduler powered by `APScheduler` fetches and batch-upserts daily mid-market rates.
* **Historical Rate Volatility:** Interactive time-series visualization (`7D`, `30D`, `90D`) built with Recharts.
* **Modular Full-Stack Architecture:** Decoupled backend (FastAPI) and modern single-page frontend (React 19, TypeScript, Tailwind CSS).
* **High Performance:** Stress-tested with Locust, sustaining 100+ concurrent users with 0% failure rate and <5ms median response time.
* **Containerized Deployment:** Orchestrated multi-container setup via Docker Compose with an optimized multi-stage Nginx build for static serving.

---

## 🛠 Tech Stack

### Backend
* **Language & Framework:** Python 3.12+, FastAPI
* **Database & ORM:** PostgreSQL 16, SQLAlchemy 2.0 (Async), `asyncpg`, Alembic
* **Background Tasks:** APScheduler
* **Caching & Precision:** `cachetools` (`TTLCache`), native `Decimal`

### Frontend
* **Core:** React 19, TypeScript, Vite
* **Styling & Layout:** Tailwind CSS
* **Data Visualization:** Recharts
* **Icons:** Lucide React

### Infrastructure & QA
* **Containerization:** Docker, Docker Compose, Nginx (Alpine)
* **Testing:** Pytest, `pytest-asyncio`, RESPX (API mocking)
* **Load Testing:** Locust

---

## 📂 Project Structure

```text
real-transfer-cost/
├── app/
│   ├── api/v1/          # Versioned REST endpoints (/compare, /rates, /rates/history)
│   ├── core/            # App configuration and settings
│   ├── db/              # SQLAlchemy models & async engine session setup
│   ├── schemas/         # Pydantic validation and serialization schemas
│   └── services/        # Domain logic (Calculator, Providers, Scheduler, History)
├── frontend/
│   ├── src/
│   │   ├── api/         # Backend API client
│   │   ├── components/  # Modular React components (TransferForm, ProviderCard, Chart)
│   │   ├── types/       # TypeScript type declarations
│   │   └── App.tsx      # Main application view
│   ├── Dockerfile       # Multi-stage production build (Node.js -> Nginx)
│   └── package.json
├── migrations/          # Asynchronous Alembic database migrations
├── scripts/             # Database seeding utilities (e.g., seed_history.py)
├── tests/               # Backend unit and integration test suite
├── docker-compose.yml   # Multi-service composition (Postgres, Backend, Frontend)
├── Dockerfile           # Backend container definition
├── locustfile.py        # Performance and load testing scenarios
└── requirements.txt     # Python runtime dependencies


Quick Start(Docker Compose)
The easiest way to run the entire stack (Database, API backend, and React web client) is with Docker Compose:
git clone [https://github.com/kuzetshy/real-transfer-cost.git](https://github.com/kuzetshy/real-transfer-cost.git)
cd real-transfer-cost

# Build and start all services
docker compose up --build

Once initialized, the services will be accessible at:
Web Client: http://localhost:3000
Interactive API Docs (Swagger): http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc


Local Development Setup
1. Database & Backend
Virtual Environment & Dependencies:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Environment Configuration:
Create a .env file in the project root:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=transfer_cost_db
POSTGRES_PORT=5433
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/transfer_cost_db

Start PostgreSQL:
docker compose up -d postgres

Run Migrations & Seed Historical Data:
alembic upgrade head
python -m scripts.seed_history

Start API Server:
uvicorn app.main:app --reload --port 8000


2. Frontend Web Client
Install Dependencies & Start Vite Server:
cd frontend
npm install
npm run dev

Open http://localhost:5173 in your browser.


API Overview

Method          Endpoint                Description
GET             /api/v1/compare         Compare transfer quotes sorted by highest recipient payout.
GET             /api/v1/rates           Fetch current mid-market exchange rate for a given currency pair.
GET             /api/v1/rates/history   Retrieve historical rates within a specified date window.
GET             /                       API health check and operational status.


Testing & Verification
Unit & Integration Tests
Ensure the PostgreSQL container is active (docker compose up -d postgres), then execute:
pytest -v

Load Testing
To run performance simulations:
locust -f locustfile.py
Access the dashboard at http://localhost:8089. Benchmarks demonstrate a 0% failure rate and a ~2 ms median response time under 100 concurrent virtual users.
