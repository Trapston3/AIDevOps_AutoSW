"""End-to-end API tests for the TabSplit FastAPI application."""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    """Hitting /health returns 200 with a body of ``{"status": "ok"}``."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_group_returns_201_and_integer_id(client: TestClient) -> None:
    """Creating a group returns 201 with an integer id and echoed fields."""
    payload = {"name": "Goa Trip", "members": ["alice", "bob"]}

    response = client.post("/groups", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["name"] == payload["name"]
    assert body["members"] == ["alice", "bob"]
    assert body["expenses"] == []


def test_get_missing_group_returns_404(client: TestClient) -> None:
    """Fetching a missing group returns 404 with GROUP_NOT_FOUND."""
    response = client.get("/groups/9999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "GROUP_NOT_FOUND",
            "message": "Group 9999 not found.",
        }
    }


def test_add_member_appends_to_group(client: TestClient) -> None:
    """Adding a member appends the name to the persisted group."""
    created = client.post("/groups", json={"name": "Flatmates"}).json()

    response = client.post(
        f"/groups/{created['id']}/members", json={"name": "carol"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["members"] == ["carol"]

    # The member is persisted in the store, not just echoed back.
    fetched = client.get(f"/groups/{created['id']}")
    assert fetched.json()["members"] == ["carol"]


def test_add_expense_with_zero_amount_returns_422(client: TestClient) -> None:
    """Adding an expense with amount == 0 fails with 422 INVALID_AMOUNT."""
    created = client.post("/groups", json={"name": "Dinner"}).json()
    expense = {"description": "Pizza", "amount": 0, "paid_by": "alice"}

    response = client.post(f"/groups/{created['id']}/expenses", json=expense)

    assert response.status_code == 422


def test_add_expense_with_negative_amount_returns_422(client: TestClient) -> None:
    """Adding an expense with amount < 0 fails with 422 INVALID_AMOUNT."""
    created = client.post("/groups", json={"name": "Dinner"}).json()
    expense = {"description": "Taxi", "amount": -12.5, "paid_by": "bob"}

    response = client.post(f"/groups/{created['id']}/expenses", json=expense)

    assert response.status_code == 422


def test_add_expense_to_missing_group_returns_404(client: TestClient) -> None:
    """Adding an expense to a missing group returns 404 GROUP_NOT_FOUND."""
    expense = {"description": "Fuel", "amount": 20.0, "paid_by": "alice"}

    response = client.post("/groups/9999/expenses", json=expense)

    assert response.status_code == 404
