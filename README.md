# Real Transfer Cost API 💸

A RESTful API service designed to calculate and compare the true costs of international money transfers across multiple providers (Wise, Revolut, Czech banks), accounting for fixed fees and hidden exchange rate markups.

---

## 🚀 Tech Stack

- **Framework:** Python 3.13, FastAPI, Uvicorn
- **Data Validation:** Pydantic v2
- **HTTP Client:** HTTPX (async requests)
- **Caching:** Cachetools (`TTLCache`)
- **Exchange Rates Provider:** [Frankfurter API](https://api.frankfurter.dev/v1) (official ECB reference rates)
- **Testing & Mocking:** Pytest, pytest-asyncio, respx

---

## 🏛️ Architectural Highlights

- **Strategy Pattern (`app/services/calculator.py`):** Encapsulated fee calculation logic per provider behind an abstract base class.
- **In-Memory Caching (`app/services/rates.py`):** Currency exchange rate caching with a 10-minute TTL to reduce latency and respect third-party rate limits.
- **Precision Financial Computing:** Standardized on Python's `Decimal` type across calculation modules to eliminate binary floating-point rounding errors.
- **Clean Layered Architecture:** Strict separation of routing concerns (`api`), validation models (`schemas`), and domain business logic (`services`).

---

## 🛠️ Getting Started

### 1. Environment Setup & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Run Development Server 
uvicorn app.main:app --reload

Interactive Swagger UI documentation will be available at: http://127.0.0.1:8000/docs


API Endpoints
Method      Endpoint            Description
GET         /                   service health check
GET         /api/v1/rates       Fetch current mid-market exchange rate
GET         /api/v1/compare     Compare transfer providers (sorted by best payout ) 

Example Request:
curl -X GET "[http://127.0.0.1:8000/api/v1/compare?amount=10000&from_currency=CZK&to_currency=EUR](http://127.0.0.1:8000/api/v1/compare?amount=10000&from_currency=CZK&to_currency=EUR)"


Running Tests
pytest -v


---

