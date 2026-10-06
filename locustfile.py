from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    # Пауза между запросами пользователя от 0.5 до 2 секунд
    wait_time = between(0.5, 2.0)

    PAIRS = [
        ("EUR", "CZK"),
        ("CZK", "EUR"),
        ("USD", "CZK"),
        ("CZK", "USD"),
    ]

    @task(3)
    def test_compare_endpoint(self):
        """Частый кейс: пользователь считает перевод"""
        from_curr, to_curr = random.choice(self.PAIRS)
        amount = random.randint(100, 50000)
        self.client.get(
            f"/api/v1/compare?from_currency={from_curr}&to_currency={to_curr}&amount={amount}",
            name="/api/v1/compare"
        )

    @task(1)
    def test_history_endpoint(self):
        """Редкий кейс: пользователь открыл график за разные даты"""
        self.client.get(
            "/api/v1/rates/history?base=EUR&target=CZK&days=30",
            name="/api/v1/rates/history"
        )

    @task(2)
    def test_current_rate_endpoint(self):
        """Проверка кэша mid-market курса"""
        from_curr, to_curr = random.choice(self.PAIRS)
        self.client.get(
            f"/api/v1/rates?from_currency={from_curr}&to_currency={to_curr}",
            name="/api/v1/rates"
        )
        