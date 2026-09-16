from uuid import uuid4

from fastapi.testclient import TestClient
from main import app

# Creates a reusable client to simulate HTTP requests against the FastAPI app.
client = TestClient(app)

# Generates a unique email for each test so no duplicate user is created.
def make_user_payload(email_suffix: str = "") -> dict[str, str]:
    unique = uuid4().hex
    return {
        "email": f"login{email_suffix or unique}@test.com",
        "password": "supersecret123",
    }

# Verifies that the root endpoint is available and returns the expected payload.
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Testing CI/CD pipeline with FastAPI"
    }

# Creates a user and checks that login succeeds with the correct password.
def test_login_success():
    user_payload = make_user_payload("-success")

    create_response = client.post("/users", json=user_payload)
    assert create_response.status_code == 201

    login_response = client.post("/login", json=user_payload)
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str)
    assert payload["access_token"]

# Creates a valid user and verifies that the API rejects a wrong password.
def test_login_invalid_password():
    user_payload = make_user_payload("-invalid")
    
    create_response = client.post("/users", json=user_payload)
    assert create_response.status_code == 201

    response = client.post("/login", json={"email": user_payload["email"], "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

# Verifies that project endpoints require authentication and isolate each user's projects.
def test_projects_are_private_to_authenticated_user():
    first_user = make_user_payload("-project-owner")
    second_user = make_user_payload("-other-owner")

    assert client.post("/users", json=first_user).status_code == 201
    assert client.post("/users", json=second_user).status_code == 201

    first_login = client.post("/login", json=first_user)
    second_login = client.post("/login", json=second_user)
    first_token = first_login.json()["access_token"]
    second_token = second_login.json()["access_token"]

    assert client.get("/projects").status_code == 401

    create_response = client.post(
        "/projects",
        json={"name": f"Private project {uuid4().hex}"},
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    first_projects = client.get(
        "/projects",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert first_projects.status_code == 200
    
    # Verifies that the first user can see their only project
    assert [project["id"] for project in first_projects.json()] == [project_id]

    second_projects = client.get(
        "/projects",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert second_projects.status_code == 200
    assert second_projects.json() == []

    other_project_response = client.get(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert other_project_response.status_code == 404