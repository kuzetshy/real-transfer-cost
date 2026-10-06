# Real Transfer Cost 💸

An open-source financial API and web client to calculate and compare real international transfer costs, revealing hidden markup fees and service charges.

## 🌟 Features
* **Accurate Calculations**: Uses `Decimal` for precision to eliminate floating-point errors.
* **Smart Caching**: In-memory `TTLCache` minimizes external API calls.
* **Background Worker**: Configured with `APScheduler` to fetch and batch-upsert daily rates automatically.
* **Flexible History**: Fetch historical exchange rates with custom date-range filtering.
* **High Performance**: Tested with Locust to handle 100+ concurrent users with 0% failure rate and <5ms median latency.

## 📂 Project Structure

```text
real-transfer-cost/
├── app/
│   ├── api/v1/          # Versioned API routes (/compare, /rates, /rates/history)
│   ├── core/            # Configuration & environment settings
│   ├── db/              # Database models (ExchangeRateHistory) & session maker
│   ├── schemas/         # Pydantic validation schemas
│   └── services/        # Business logic (Calculator, Providers, Scheduler, History)
├── frontend/            # React 19 + TypeScript + Vite + Tailwind CSS client
├── migrations/          # Alembic asynchronous migrations
├── scripts/             # CLI utility scripts (e.g., seed_history.py)
├── tests/               # Unit and integration test suite (Pytest)
├── docker-compose.yml   # PostgreSQL container setup
├── locustfile.py        # Locust load testing scenarios
└── requirements.txt     # Python dependencies

## Getting Started (Backend)
Clone & Set Up Virtual Environment:

git clone https://github.com/kuzetshy/real-transfer-cost.git
cd real-transfer-cost

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Environment Configuration:
Create a .env file in the project root:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=transfer_cost_db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/transfer_cost_db

Start Database & Run Migrations:
# Start PostgreSQL in background
docker compose up -d

# Apply database migrations
alembic upgrade head

# (Optional) Seed 30-day historical rates
python -m scripts.seed_history

Run Development Server:
uvicorn app.main:app --reload

Interactive API documentation will be available at:
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc


API Endpoints

Method          Endpoint                Description 
GET             /api/v1/compare         Compare transfer offers across providers sorted by recipient payout.
GET             /api/v1/rates           Fetch current mid-market rate for a currency pair.
GET             /api/v1/rates/history   Historical exchange rate points from DB


Frontend Client:
The frontend application is built with React 19, TypeScript, Vite, and Tailwind CSS.

Running the Frontend
Open a new terminal window: 
cd frontend
npm install
npm run dev

Open http://localhost:5173 in your browser to access the interactive transfer cost calculator.


Testing
Unit & Integration Testing
Run the Pytest suite to verify financial calculations and rollback DB sessions:
pytest -v

Load Testing:
Stress testing is performed using Locust:
locust -f locustfile.py

Open http://localhost:8089 to simulate user traffic. Current benchmark with 100 concurrent users demonstrates a 0% failure rate and a median response time of ~2 ms.