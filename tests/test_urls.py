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

def test_redirect_creates_visit(client, auth_headers):

    register_response = client.post(
        '/register',
        json={
            "email": "analytics@example.com",
            "password": "password123"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        '/login',
        json={
            "email": "analytics@example.com",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    response = client.post(
        "/shorten",
        json={"url": "http://example.com"},
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

def test_multiple_redirects_count_visits(client, auth_headers):

    register_response = client.post(
        "/register",
        json={
            "email": "visits@example.com",
            "password": "password123"
        }
    )
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "visits@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200

    response = client.post(
        "/shorten",
        json={
            "url": "https://example.com"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    short_code = response.get_json()["shortCode"]

    # Visit three times
    for _ in range(3):
        response = client.get(
            f"/{short_code}",
            follow_redirects=False
        )

        assert response.status_code == 302

    # Get analytics
    response = client.get(
        f"/shorten/{short_code}/analytics",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["totalVisits"] == 3

def test_analytics_requires_authentication(app):
    client = app.test_client()

    # Register
    response = client.post(
        "/register",
        json={
            "email": "anonymous@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201

    # Login
    response = client.post(
        "/login",
        json={
            "email": "anonymous@example.com",
            "password": "password123"
        }
    )

    token = response.get_json()["access_token"]

    # Create URL
    response = client.post(
        "/shorten",
        json={
            "url": "https://example.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    short_code = response.get_json()["shortCode"]

    # Try analytics WITHOUT token
    response = client.get(
        f"/shorten/{short_code}/analytics"
    )

    assert response.status_code == 401

def test_user_cannot_access_another_users_analytics(app):
    client = app.test_client()

    # -------------------------
    # Create User A
    # -------------------------
    response = client.post(
        "/register",
        json={
            "email": "usera@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    # Login User A
    response = client.post(
        "/login",
        json={
            "email": "usera@example.com",
            "password": "password123"
        }
    )

    token_a = response.get_json()["access_token"]

    # User A creates URL
    response = client.post(
        "/shorten",
        json={
            "url": "https://example.com"
        },
        headers={
            "Authorization": f"Bearer {token_a}"
        }
    )

    assert response.status_code == 201

    short_code = response.get_json()["shortCode"]

    # -------------------------
    # Create User B
    # -------------------------
    response = client.post(
        "/register",
        json={
            "email": "userb@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    # Login User B
    response = client.post(
        "/login",
        json={
            "email": "userb@example.com",
            "password": "password123"
        }
    )

    token_b = response.get_json()["access_token"]

    response = client.get(
        f"/shorten/{short_code}/analytics",
        headers={
            "Authorization": f"Bearer {token_b}"
        }
    )

    assert response.status_code == 403

def test_analytics_returns_recent_visits(app):
    client = app.test_client()

    # Register
    response = client.post(
        "/register",
        json={
            "email": "recent@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201

    # Login
    response = client.post(
        "/login",
        json={
            "email": "recent@example.com",
            "password": "password123"
        }
    )

    token = response.get_json()["access_token"]

    # Create URL
    response = client.post(
        "/shorten",
        json={
            "url": "https://example.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    short_code = response.get_json()["shortCode"]

    # Visit URL
    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302

    # Analytics
    response = client.get(
        f"/shorten/{short_code}/analytics",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["totalVisits"] == 1
    assert "recentVisits" in data