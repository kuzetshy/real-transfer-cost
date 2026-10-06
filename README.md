# 💸 Real Transfer Cost API

An asynchronous, transparent currency transfer comparison engine built with **Python 3.13**, **FastAPI**, **PostgreSQL**, and **SQLAlchemy 2.0 (async)**. 

It calculates and reveals true cross-border transfer fees (including hidden mid-market exchange markups) across popular payment providers (Wise, Revolut, Czech Bank) for Czech Koruna (`CZK`), Euro (`EUR`), and US Dollar (`USD`).

---

## 🚀 Tech Stack

- **Framework**: FastAPI (Async REST API)
- **Database**: PostgreSQL 16 (via Docker Compose)
- **ORM & Migrations**: SQLAlchemy 2.0 (asyncio + asyncpg) & Alembic
- **External Data**: Frankfurter API (via `httpx` async client)
- **Caching**: `cachetools` (TTLCache in-memory layer)
- **Financial Precision**: Python `Decimal` (preventing floating-point roundoff issues)
- **Testing**: `pytest`, `pytest-asyncio`, `respx` (100% test pass rate)

---

## 📦 Project Architecture

```text
real-transfer-cost/
├── app/
│   ├── api/v1/          # Versioned API routes (/compare, /rates, /rates/history)
│   ├── core/            # Configuration & environment settings
│   ├── db/              # Database models (Base, ExchangeRateHistory) & session maker
│   ├── schemas/         # Pydantic validation schemas
│   └── services/        # Business logic (Calculator, Providers, RatesClient, HistoryService)
├── migrations/          # Alembic asynchronous migrations
├── scripts/             # CLI utility scripts (seed_history.py)
├── tests/               # Unit and integration test suite
├── docker-compose.yml   # PostgreSQL container setup
└── requirements.txt

Getting Started!
Clone & Set Up Virtual Environment:

git clone [https://github.com/kuzetshy/real-transfer-cost.git](https://github.com/kuzetshy/real-transfer-cost.git)
cd real-transfer-cost

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 


Environment Configuration
Create a .env file in the project root:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=transfer_cost_db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/transfer_cost_db

Start Database & Run Migrations
# 1. Start PostgreSQL in background
docker compose up -d

# 2. Apply database migrations
alembic upgrade head

# 3. (Optional) Seed 30-day historical rates
python -m scripts.seed_history

Run Development Server
uvicorn app.main:app --reload

Interactive API documentation will be available at:
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc


API Endpoints:
Method      Endpoint                Description 
GET         /api/v1/compare         Compare transfer offers across providers sorted by recipient payout
GET         /api/v1/rates           Fetch current mid-market rate for a currency pair
GET         /api/v1/rates/history   Historical exchange rate points from DB for frontend charts


Testing
pytest -v
All unit tests for financial calculations and integration tests with rollback DB sessions should pass.


## Frontend Client

The frontend application is built with React 19, TypeScript, Vite, and Tailwind CSS.

### Running the Frontend

```bash
cd frontend
npm install
npm run dev

Open http://localhost:5173 to access the interactive transfer cost calculator.

##Load Testing 
locust -f locustfile.py

Open http://localhost:8089 to simulate user traffic. Current benchmark with 100 concurrent users demonstrates 0% failure rate and a median response time of 2 ms.

