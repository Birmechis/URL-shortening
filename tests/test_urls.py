from app.models import ShortURL
from datetime import datetime, timezone
from app import db

def test_create_short_url(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json={
            "url": "http://example.com",
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "shortCode" in data

def test_missing_url(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json={}
    )

    assert response.status_code == 400

def test_invalid_url(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json={
            "url": "hello",
        }
    )

    assert response.status_code == 400

def test_url_must_be_string(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json={
            "url": 12345
        }
    )

    assert response.status_code == 400

def test_redirect(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json={
            "url": "http://example.com",
        }
    )

    data = response.get_json()

    short_code = data["shortCode"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302

    assert response.location == "http://example.com"

def test_access_count_increment(app):

    client = app.test_client()
    response = client.post(
        '/shorten',
        json={"url": "http://example.com"}
    )

    assert response.status_code == 201

    data = response.get_json()
    short_code = data["shortCode"]

    response = client.get(
        f"/shorten/{short_code}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data['accessCount'] == 0

    response = client.get(
        f"{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302

    response = client.get(
        f"/shorten/{short_code}",
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data['accessCount'] == 1

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

def test_unknown_short_code(app):

    client = app.test_client()

    response = client.get(
        "/doesnotexist",
        follow_redirects=False
    )

    assert response.status_code == 404

def test_statistics(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json={
            "url": "http://example.com",
        }
    )

    assert response.status_code == 201

    data = response.get_json()
    short_code = data["shortCode"]

    response = client.get(f"/shorten/{short_code}/stats")

    assert response.status_code == 200

    data = response.get_json()

    assert data['shortCode'] == short_code
    assert data['url'] == "http://example.com"
    assert data['accessCount'] == 0

def test_update_url(app):
    client = app.test_client()

    response = client.post(
        '/shorten',
        json={"url": "http://example.com"}
    )
    assert response.status_code == 201

    data = response.get_json()
    short_code = data["shortCode"]

    response = client.put(
        f"/shorten/{short_code}",
        json={"url": "http://example.com"}
    )
    assert response.status_code == 200

    data = response.get_json()

    assert data['url'] == "http://example.com"
    assert data['shortCode'] == short_code

def test_delete_url(app):
    client = app.test_client()

    response = client.post(
        '/shorten',
        json={"url": "http://example.com"}
    )

    assert response.status_code == 201

    data = response.get_json()
    short_code = data["shortCode"]

    response = client.delete(f"/shorten/{short_code}")

    assert response.status_code == 200

    data = response.get_json()

    assert data['success'] is True

    response = client.get(f"/shorten/{short_code}")

    assert response.status_code == 404

def test_short_url_without_expiration(app):

    client = app.test_client()

    response = client.post(
        "/shorten",
        json = {"url": "http://example.com"}
    )

    assert response.status_code == 201

    data = response.get_json()
    short_code = data['shortCode']

    assert data['expiresAt'] is None

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.location == "http://example.com"

def test_short_url_with_future_expiration(app):

    client = app.test_client()

    response = client.post(
        "/shorten",
        json ={
            "url": "http://example.com",
            "expiresAt": "2099-01-01T12:00:00"
        }
    )

    assert response.status_code == 201

    data = response.get_json()
    short_code = data['shortCode']

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )
    assert response.status_code == 302
    assert response.location == "http://example.com"

def test_invalid_expiration_date(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json = {
            "url": "http://example.com",
            "expiresAt": "tomorrow"
        }
    )

    assert response.status_code == 400

def test_already_expired_date(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json = {
            "url": "http://example.com",
            "expiresAt": "2020-01-01T12:00:00"
        }
    )

    assert response.status_code == 400

def test_short_url_expired(app):

    client = app.test_client()

    response = client.post(
        '/shorten',
        json = {
            "url": "http://example.com",
        }
    )

    assert response.status_code == 201

    data = response.get_json()
    short_code = data['shortCode']

    short_url = ShortURL.query.filter_by(shortCode=short_code).first()

    short_url.expiresAt = datetime(2020,1,1,tzinfo=timezone.utc)
    db.session.commit()

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 410

def test_rate_limit(app):

    client = app.test_client()

    for _ in range(3):
        response = client.post(
            '/shorten',
            json={
                "url": "http://example.com",
            }
        )
        assert response.status_code == 201

    response = client.post(
        '/shorten',
        json={
            "url": "http://example.com",
        }
    )

    assert response.status_code == 429