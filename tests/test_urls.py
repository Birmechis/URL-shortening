from datetime import datetime, timezone

from app import db
from app.models import ShortURL


def test_create_short_url(client, auth_headers):
    response = client.post(
        "/shorten",
        json={"url": "http://example.com"},
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "shortCode" in data


def test_missing_url(client, auth_headers):
    response = client.post(
        "/shorten",
        json={},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_invalid_url(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "hello"
        },
        headers=auth_headers
    )

    assert response.status_code == 400


def test_url_must_be_string(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": 12345
        },
        headers=auth_headers
    )

    assert response.status_code == 400


def test_redirect(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.location == "http://example.com"


def test_access_count_increment(client, auth_headers):
    response = client.post(
        "/shorten",
        json={"url": "http://example.com"},
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    response = client.get(
        f"/shorten/{short_code}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["accessCount"] == 0

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302

    response = client.get(
        f"/shorten/{short_code}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["accessCount"] == 1

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302

    response = client.get(
        f"/shorten/{short_code}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["accessCount"] == 2


def test_unknown_short_code(client):
    response = client.get(
        "/doesnotexist",
        follow_redirects=False
    )

    assert response.status_code == 404


def test_statistics(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    response = client.get(
        f"/shorten/{short_code}/stats",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["shortCode"] == short_code
    assert data["url"] == "http://example.com"
    assert data["accessCount"] == 0


def test_update_url(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    response = client.put(
        f"/shorten/{short_code}",
        json={
            "url": "http://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["url"] == "http://example.com"
    assert data["shortCode"] == short_code


def test_delete_url(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    response = client.delete(
        f"/shorten/{short_code}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True

    response = client.get(
        f"/shorten/{short_code}"
    )

    assert response.status_code == 404


def test_short_url_without_expiration(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    assert data["expiresAt"] is None

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.location == "http://example.com"


def test_short_url_with_future_expiration(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com",
            "expiresAt": "2099-01-01T12:00:00"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.location == "http://example.com"


def test_invalid_expiration_date(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com",
            "expiresAt": "tomorrow"
        },
        headers=auth_headers
    )

    assert response.status_code == 400


def test_already_expired_date(client, auth_headers):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com",
            "expiresAt": "2020-01-01T12:00:00"
        },
        headers=auth_headers
    )

    assert response.status_code == 400


def test_short_url_expired(client, auth_headers, app):
    response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data["shortCode"]

    with app.app_context():
        short_url = ShortURL.query.filter_by(
            shortCode=short_code
        ).first()

        assert short_url is not None

        short_url.expiresAt = datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc
        )

        db.session.commit()

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 410


def test_rate_limit(rate_limit_client):
    client = rate_limit_client

    client.post(
        "/register",
        json={
            "email": "ratelimit@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/login",
        json={
            "email": "ratelimit@example.com",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    for _ in range(3):
        response = client.post(
            "/shorten",
            json={"url": "http://example.com"},
            headers=headers
        )

        assert response.status_code == 201

    response = client.post(
        "/shorten",
        json={"url": "http://example.com"},
        headers=headers
    )

    assert response.status_code == 429