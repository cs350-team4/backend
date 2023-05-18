import jwt
from fastapi.testclient import TestClient

from api.main import decode_jwt
from api.settings import settings


def generate_manager_token(priv_key: str, name: str) -> str:
    return jwt.encode({"name": name, "sub": "manager"}, priv_key, algorithm="ES256")


def generate_token(
    client: TestClient, username: str = "aziz", password: str = "password"
) -> dict:
    # TODO: Add `optional` field
    response = client.post(
        "/auth/generateToken", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["auth_token"]

    payload = decode_jwt(data["auth_token"])
    assert payload is not None

    assert payload["name"] == username
    assert payload["iat"]
    assert "sub" not in payload or payload["sub"] == "client"

    return payload


def generate_token_invalid(
    client: TestClient, username: str = "aziz", password: str = "notpassword"
) -> None:
    # TODO: Add `optional` field
    response = client.post(
        "/auth/generateToken", json={"username": username, "password": password}
    )
    assert response.status_code == 403, response.text


def public_key(client: TestClient) -> str:
    response = client.get("/auth/publicKey")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["publicKey"] == settings.PUBLIC_KEY
    return data["publicKey"]
