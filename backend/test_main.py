from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_create_account_success(client):
    account_data = {
        "bank_account_no": "ACCOUNT12345",
        "bank_name": "TestBank",
        "holder_name": "Test User",
        "account_type": "savings",
        "balance": 500.75,
        "currency": "INR",
    }
    response = client.post("/accounts/add", json=account_data)

    assert response.status_code == 201
    account = response.json()

    assert "id" in account
    assert isinstance(account["id"], int)
    assert account["bank_account_no"] == account_data["bank_account_no"]
    assert account["bank_name"] == account_data["bank_name"]
    assert account["holder_name"] == account_data["holder_name"]
    assert account["account_type"] == account_data["account_type"]
    assert account["balance"] == account_data["balance"]
    assert account["currency"] == account_data["currency"]
    assert "created_at" in account
    assert "updated_at" in account


def test_create_account_duplicate_bank_account_no(client):
    # First, create a valid account
    account_data_1 = {
        "bank_account_no": "UNIQUE12345",
        "bank_name": "Bank A",
        "holder_name": "User One",
        "account_type": "current",
        "balance": 100.0,
        "currency": "USD",
    }
    client.post(
        "/accounts/add", json=account_data_1
    )  # This should succeed and be cleaned up by fixture

    # Then, attempt to create another account with the same bank_account_no
    account_data_2 = {
        "bank_account_no": "UNIQUE12345",  # Duplicate
        "bank_name": "Bank B",
        "holder_name": "User Two",
        "account_type": "savings",
        "balance": 200.0,
        "currency": "EUR",
    }
    response = client.post("/accounts/add", json=account_data_2)

    assert response.status_code == 400
    assert response.json() == {"detail": "Account number already exists"}


def test_create_account_with_negative_balance(client):
    account_data = {
        "bank_account_no": "NEGATIVEBALANCE",
        "bank_name": "BadBank",
        "holder_name": "Risk Taker",
        "account_type": "savings",
        "balance": -100.0,  # Invalid
        "currency": "INR",
    }
    response = client.post("/accounts/add", json=account_data)

    assert response.status_code == 422  # Pydantic validation error
    # Assert specific detail message if possible, or check structure
    assert "detail" in response.json()
    assert any(
        "Balance shouldn't be less than 0" in error.get("msg", "")
        for error in response.json().get("detail", [])
    )
