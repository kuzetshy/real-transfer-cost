from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    # Simulated user pacing: 0.5 to 2.0 seconds between requests
    wait_time = between(0.5, 2.0)

    PAIRS = [
        ("EUR", "CZK"),
        ("CZK", "EUR"),
        ("USD", "CZK"),
        ("CZK", "USD"),
    ]

    @task(3)
    def test_compare_endpoint(self):
        """Frequent scenario: user executes transfer cost comparison."""
        from_curr, to_curr = random.choice(self.PAIRS)
        amount = random.randint(100, 50000)
        self.client.get(
            f"/api/v1/compare?from_currency={from_curr}&to_currency={to_curr}&amount={amount}",
            name="/api/v1/compare"
        )

    @task(1)
    def test_history_endpoint(self):
        """Less frequent scenario: user views the historical rate chart."""
        self.client.get(
            "/api/v1/rates/history?base=EUR&target=CZK&days=30",
            name="/api/v1/rates/history"
        )

    @task(2)
    def test_current_rate_endpoint(self):
        """Mid-market rate lookup with in-memory caching test."""
        from_curr, to_curr = random.choice(self.PAIRS)
        self.client.get(
            f"/api/v1/rates?from_currency={from_curr}&to_currency={to_curr}",
            name="/api/v1/rates"
        )