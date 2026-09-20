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