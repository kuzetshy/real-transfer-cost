from fastapi import FastAPI
from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="Real Transfer Cost API",
    description="API для расчета реальной стоимости международных переводов",
    version="0.1.0"
)

# Подключаем роутер с префиксом /api
app.include_router(api_v1_router, prefix="/api")

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Real Transfer Cost API is running!"
    }
