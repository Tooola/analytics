"""Generate demo data for the Open Analytics AI platform.

Usage:
    cd backend
    python -m scripts.generate_demo_data
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

API_BASE = "http://localhost:8000"
APP_SLUG = "demo-app"
DATASET_SLUG = "demo-sales"


def wait_for_api(timeout: int = 30) -> bool:
    """Wait until the API is reachable."""
    import time

    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{API_BASE}/api/v1/health", timeout=2)
            if r.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False


def register_application() -> str:
    """Register a demo application and return the API key."""
    print("Registering demo application...")
    r = requests.post(
        f"{API_BASE}/api/v1/applications",
        json={
            "name": "Demo App",
            "description": "Demo application for testing analytics",
            "status": "active",
        },
        timeout=10,
    )
    if r.status_code == 409:
        print("  Application 'Demo App' already exists. Regenerating API key...")
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from app.core.database import SessionLocal
        from app.repositories.application_repo import ApplicationRepository
        db = SessionLocal()
        try:
            repo = ApplicationRepository(db)
            demo_app = repo.get_by_slug(APP_SLUG)
            if demo_app:
                api_key = repo.regenerate_key(demo_app)
                print(f"  API Key regenerated: {api_key}")
                return api_key
        finally:
            db.close()

    r.raise_for_status()
    data = r.json()
    api_key = data.get("api_key")
    print(f"  Application registered: {data['slug']}")
    print(f"  API Key: {api_key}")
    return api_key


def register_dataset(api_key: str) -> None:
    """Register a demo dataset with field definitions."""
    print("Registering demo dataset...")
    r = requests.post(
        f"{API_BASE}/api/v1/datasets",
        json={
            "application_slug": APP_SLUG,
            "name": "Demo Sales",
            "slug": DATASET_SLUG,
            "description": "Sample sales data for analytics testing",
            "fields": [
                {"name": "date", "technical_type": "date", "semantic_type": "date", "required": True},
                {"name": "product", "technical_type": "string", "semantic_type": "product", "required": True},
                {"name": "quantity", "technical_type": "integer", "semantic_type": "quantity", "unit": "units", "required": True},
                {"name": "unit_price", "technical_type": "float", "semantic_type": "cost", "unit": "USD", "required": True},
                {"name": "revenue", "technical_type": "float", "semantic_type": "revenue", "unit": "USD", "required": True},
                {"name": "cost", "technical_type": "float", "semantic_type": "cost", "unit": "USD", "required": True},
            ],
        },
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    if r.status_code == 409:
        print(f"  Dataset '{DATASET_SLUG}' already registered. Proceeding...")
        return
    r.raise_for_status()
    print(f"  Dataset registered: {DATASET_SLUG}")


def generate_sales_data(num_rows: int = 200) -> list[dict]:
    """Generate realistic sales data with trends and anomalies."""
    products = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Tool Z"]
    base_date = datetime(2024, 1, 1)
    data = []

    for i in range(num_rows):
        date = base_date + timedelta(days=random.randint(0, 364))
        product = random.choice(products)

        # Base price varies by product
        base_prices = {"Widget A": 25.0, "Widget B": 35.0, "Gadget X": 120.0, "Gadget Y": 85.0, "Tool Z": 45.0}
        base_price = base_prices[product]

        # Add some trend: prices increase slightly over time
        trend_factor = 1 + (i / num_rows) * 0.1

        quantity = random.randint(1, 50)
        unit_price = round(base_price * trend_factor * random.uniform(0.9, 1.1), 2)
        revenue = round(quantity * unit_price, 2)
        cost = round(revenue * random.uniform(0.4, 0.7), 2)

        # Inject some anomalies (high revenue days)
        if random.random() < 0.05:
            quantity = random.randint(80, 150)
            revenue = round(quantity * unit_price, 2)
            cost = round(revenue * 0.3, 2)

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "revenue": revenue,
            "cost": cost,
        })

    return data


def send_data(api_key: str, data: list[dict]) -> None:
    """Send data to the analytics platform."""
    print(f"Sending {len(data)} rows of demo data...")
    r = requests.post(
        f"{API_BASE}/api/v1/analyze",
        json={
            "application": APP_SLUG,
            "dataset": DATASET_SLUG,
            "analysis": ["summary", "trend", "anomaly"],
            "include_ai": True,
            "data": data,
        },
        headers={"X-API-Key": api_key},
        timeout=60,
    )
    r.raise_for_status()
    result = r.json()
    print(f"  Analysis completed: {result.get('analysis_id', 'N/A')}")
    print(f"  Insights generated: {len(result.get('insights', []))}")
    if result.get("ai_interpretation"):
        print(f"  AI interpretation: available")


def run_analysis(api_key: str, data: list[dict]) -> None:
    """Run an additional analysis to populate more results."""
    print("Running additional analysis...")
    r = requests.post(
        f"{API_BASE}/api/v1/analyze",
        json={
            "application": APP_SLUG,
            "dataset": DATASET_SLUG,
            "analysis": ["summary", "trend"],
            "include_ai": False,
            "data": data[:100],
        },
        headers={"X-API-Key": api_key},
        timeout=60,
    )
    r.raise_for_status()
    print("  Second analysis completed")


def main() -> None:
    print("=" * 60)
    print("  Open Analytics AI — Demo Data Generator")
    print("=" * 60)
    print()

    if not wait_for_api():
        print("ERROR: Cannot reach API. Make sure the backend is running:")
        print("  cd backend && uvicorn app.main:app --reload")
        sys.exit(1)

    print("API is reachable.\n")

    api_key = register_application()
    register_dataset(api_key)

    data = generate_sales_data(200)
    send_data(api_key, data)
    run_analysis(api_key, data)

    print()
    print("=" * 60)
    print("  Demo data generated successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"  1. Open Streamlit dashboard: http://localhost:8501")
    print(f"  2. Use API key: {api_key}")
    print(f"  3. Explore Analytics and AI Playground pages")


if __name__ == "__main__":
    main()
