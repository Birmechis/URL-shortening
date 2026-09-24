def register_user(client, email="user@example.com", password="password123"):
    return client.post(
        "/register",
        json={
            "email": email,
            "password": password
        }
    )

def login_user(client, email="user@example.com", password="password123"):
    return client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )

def test_register_user(client):

    response = register_user(client)

    assert response.status_code == 201

    data = response.get_json()

    assert "message" in data

def test_duplicate_email(client):

    register_user(client)

    response = register_user(client)

    assert response.status_code == 409

    data = response.get_json()

    assert "error" in data

def test_register_missing_fields(client):

    response = client.post(
        "/register",
        json={}
    )

    assert response.status_code == 400

def test_login_user(client):

    register_user(client)

    response = login_user(client)

    assert response.status_code == 200

    data = response.get_json()

    assert "access_token" in data

def test_login_wrong_password(client):

    register_user(client)

    response = login_user(
        client,
        password="wrongpassword"
    )

    assert response.status_code == 401

def test_login_unknown_user(client):

    response = login_user(
        client,
        email="doesnotexist@example.com"
    )

    assert response.status_code == 401

def test_shorten_requires_authentication(client):

  response = client.post(
      "/shorten",
      json={
          "url": "http://example.com"
      }
  )

  assert response.status_code == 401

def test_authenticated_user_can_create_url(client):

    register_user(client)

    login_response= login_user(client)

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    response = client.post(
        '/shorten',
        json={
            "url": "http://example.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "shortCode" in data

def test_created_url_belongs_to_user(client, app):

    register_user(client)

    login_response= login_user(client)

    token = login_response.get_json()["access_token"]

    response = client.post(
        '/shorten',
        json={
            "url": "http://example.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    short_code = data['shortCode']

    with app.app_context():
        from app.models import ShortURL

        short_url = ShortURL.query.filter_by(shortCode=short_code).first()

        assert short_url is not None
        assert short_url.user_id is not None

def test_user_cannot_modify_other_users_url(client):
    # user 1

    register_user(
        client,
        email='user1@example.com'
    )

    login_response= login_user(
        client,
        email='user1@example.com'
    )

    token1 = login_response.get_json()["access_token"]

    # user1 creates URL

    create_response = client.post(
        '/shorten',
        json={
            "url": "http://example.com"
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    assert create_response.status_code == 201

    short_code = create_response.get_json()["shortCode"]

    # user 2

    register_user(
        client,
        email = "user2@example.com"
    )

    login_response = login_user(
        client,
        email = "user2@example.com"
    )

    token2 = login_response.get_json()['access_token']

    # user creates URL
    create_response = client.put(
        f'/shorten/{short_code}',
        json={
            "url": "http://attacker.example.com"
        },
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    assert create_response.status_code == 403

def test_user_cannot_delete_other_users_url(client):
    # user 1

    register_user(
        client,
        email="owner1@example.com"
    )

    login_response= login_user(
        client,
        email='owner1@example.com'
    )

    token1 = login_response.get_json()['access_token']

    # user 1 creates URL

    create_response = client.post(
        '/shorten',
        json={
            "url": "http://example.com"
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    assert create_response.status_code == 201

    short_code = create_response.get_json()['shortCode']

    # user 2
    register_user(
        client,
        email="attacker@example.com"
    )

    login_response = login_user(
        client,
        email="attacker@example.com"
    )

    attacker_token = login_response.get_json()["access_token"]

    # user 2 tries to delete user 1's URL
    response = client.delete(
        f"/shorten/{short_code}",
        headers={
            "Authorization": f"Bearer {attacker_token}"
        }
    )

    assert response.status_code == 403

def test_user_can_modify_own_url(client):

    register_user(client)

    login_response = login_user(client)

    token = login_response.get_json()["access_token"]

    create_response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 201

    short_code = create_response.get_json()["shortCode"]

    response = client.put(
        f"/shorten/{short_code}",
        json={
            "url": "http://example.org"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["url"] == "http://example.org"

def test_user_can_delete_own_url(client):

    register_user(client)

    login_response = login_user(client)

    token = login_response.get_json()["access_token"]

    create_response = client.post(
        "/shorten",
        json={
            "url": "http://example.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 201

    short_code = create_response.get_json()["shortCode"]

    response = client.delete(
        f"/shorten/{short_code}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200