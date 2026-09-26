# URL Shortener API

A RESTful URL shortening API built with **Flask, PostgreSQL, SQLAlchemy, JWT authentication, and automated testing**.

The application allows authenticated users to create, retrieve, update, delete, and monitor shortened URLs. It also supports URL expiration, access statistics, request rate limiting, and secure short-code generation.

---

## Features

* **URL Shortening** — Generate a unique 6-character short code for a long URL.
* **URL Validation** — Validate submitted URLs before storing them.
* **JWT Authentication** — Protect URL management endpoints using JSON Web Tokens.
* **User Ownership** — Associate shortened URLs with the authenticated user.
* **CRUD Operations** — Create, retrieve, update, and delete shortened URLs.
* **URL Expiration** — Optionally specify an expiration date for a shortened URL.
* **Access Statistics** — Track how many times a shortened URL has been accessed.
* **Rate Limiting** — Limit requests to protected endpoints to help prevent abuse.
* **Secure Short-Code Generation** — Use Python's `secrets` module to generate unpredictable short codes.
* **Database Migrations** — Manage database schema changes using Flask-Migrate and Alembic.
* **Error Handling** — Return appropriate HTTP responses for invalid requests and server errors.
* **Automated Tests** — Test API behavior using pytest.
* **Environment Configuration** — Keep database credentials and secret keys outside the source code using environment variables.

---

## Technology Stack

| Technology         | Purpose                         |
| ------------------ | ------------------------------- |
| Python             | Programming language            |
| Flask              | Web framework                   |
| PostgreSQL         | Relational database             |
| Flask-SQLAlchemy   | Database ORM                    |
| SQLAlchemy         | Database toolkit and ORM        |
| Flask-JWT-Extended | JWT authentication              |
| Flask-Limiter      | API rate limiting               |
| Flask-Migrate      | Database migrations             |
| Alembic            | Migration engine                |
| psycopg            | PostgreSQL database driver      |
| pytest             | Automated testing               |
| python-dotenv      | Environment variable management |
| secrets            | Secure short-code generation    |

---

## Project Structure

```text
URL-shortening/
│
├── app/
│   ├── __init__.py        # Flask application setup and configuration
│   ├── models.py          # Database models
│   └── routes.py          # API endpoints and request handling
│
├── migrations/            # Database migration files
│   ├── versions/
│   └── ...
│
├── tests/                 # Automated API tests
│
├── .env.example           # Example environment variables
├── .gitignore
├── README.md
├── requirements.txt       # Python dependencies
└── run.py                 # Application entry point
```

---

# Database Models

## User

The `User` model stores information about registered users.

Main fields include:

* `user_id` — Primary key
* `email` — Unique user email
* `password` — User password
* `created_at` — Account creation timestamp

---

## ShortURL

The `ShortURL` model stores shortened URLs.

Main fields include:

* `id` — Primary key
* `url` — Original destination URL
* `shortCode` — Generated short identifier
* `createdAt` — Creation timestamp
* `updatedAt` — Last update timestamp
* `accessCount` — Number of accesses
* `expiresAt` — Optional expiration timestamp
* `user_id` — User who owns the shortened URL

---

# Authentication

URL management endpoints require a valid **JWT access token**.

The general authentication flow is:

```text
Register
   ↓
Login
   ↓
Receive JWT access token
   ↓
Include token in Authorization header
   ↓
Access protected URL endpoints
```

Example:

```http
Authorization: Bearer <access_token>
```

This prevents unauthenticated users from accessing protected operations.

Authentication and resource ownership are separate concerns: possessing a valid token does not automatically mean a user can modify another user's URL.

---

# API Endpoints

## Authentication

### Register

```http
POST /register
```

Creates a new user account.

Example request:

```json
{
    "email": "user@example.com",
    "password": "your-password"
}
```

---

### Login

```http
POST /login
```

Authenticates a user and returns a JWT access token.

Example request:

```json
{
    "email": "user@example.com",
    "password": "your-password"
}
```

---

# URL Management

All URL management operations require authentication.

## Create a Short URL

```http
POST /shorten
```

Creates a shortened URL.

Example request:

```json
{
    "url": "https://www.example.com/a/very/long/url"
}
```

An optional expiration date can also be supplied:

```json
{
    "url": "https://www.example.com/a/very/long/url",
    "expiresAt": "2026-12-31T23:59:59"
}
```

Example response:

```json
{
    "id": 1,
    "url": "https://www.example.com/a/very/long/url",
    "shortCode": "7M4bAF",
    "createdAt": "2026-09-26T12:00:00",
    "expiresAt": "2026-12-31T23:59:59"
}
```

---

## Get a Shortened URL

```http
GET /shorten/<shortCode>
```

Retrieves information about a shortened URL.

Example:

```http
GET /shorten/7M4bAF
```

---

## Update a Shortened URL

```http
PUT /shorten/<shortCode>
```

Updates the destination URL associated with a short code.

Example:

```json
{
    "url": "https://www.example.com/new/destination"
}
```

A valid JWT belonging to the URL owner is required.

---

## Delete a Shortened URL

```http
DELETE /shorten/<shortCode>
```

Deletes a shortened URL.

A valid JWT belonging to the URL owner is required.

---

## Get URL Statistics

```http
GET /shorten/<shortCode>/stats
```

Returns information about the shortened URL, including its access count.

Example response:

```json
{
    "id": 1,
    "url": "https://www.example.com/a/very/long/url",
    "shortCode": "7M4bAF",
    "createdAt": "2026-09-26T12:00:00",
    "updatedAt": "2026-09-26T12:10:00",
    "accessCount": 10
}
```

---

# URL Expiration

A URL can optionally have an expiration time.

For example:

```json
{
    "url": "https://www.example.com",
    "expiresAt": "2026-12-31T23:59:59"
}
```

The API validates the expiration timestamp and prevents creation with an expiration time that has already passed.

Expired URLs should no longer be treated as active resources.

---

# Rate Limiting

Protected endpoints use request rate limiting to reduce excessive requests and API abuse.

For example, the URL creation endpoint is limited to:

```text
3 requests per minute
```

When the limit is exceeded, the API returns:

```http
429 Too Many Requests
```

---

# Short-Code Generation

Short codes are generated using Python's `secrets` module.

The generated codes use letters and numbers and are checked against existing records to prevent collisions.

Example:

```text
7M4bAF
x92KqP
A8zLm2
```

The database also provides uniqueness constraints for persisted short codes.

---

# Error Handling

The API returns appropriate HTTP status codes for common errors.

Examples include:

| Status Code | Meaning                                       |
| ----------- | --------------------------------------------- |
| `200`       | Request successful                            |
| `201`       | Resource created                              |
| `400`       | Invalid request                               |
| `401`       | Authentication required or token invalid      |
| `403`       | User is not authorized to modify the resource |
| `404`       | Resource not found                            |
| `429`       | Rate limit exceeded                           |
| `500`       | Internal server error                         |

Example:

```json
{
    "error": "Resource not found"
}
```

---

# Testing

The project uses **pytest** for automated testing.

Tests cover important API behavior including:

* User authentication
* JWT-protected endpoints
* URL creation
* URL validation
* URL retrieval
* URL updates
* URL deletion
* URL statistics
* URL expiration
* Rate limiting
* Invalid requests
* Authentication failures
* Resource ownership/authorization

Run the test suite with:

```bash
python -m pytest
```

To run with more detailed output:

```bash
python -m pytest -v
```

---

# Setup

## Prerequisites

Install:

* Python 3.10+
* PostgreSQL
* pip
* Git

---

## 1. Clone the repository

```bash
git clone https://github.com/Birmechis/URL-shortening.git
cd URL-shortening
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/url_shortener
JWT_SECRET_KEY=your-secret-key
```

Do **not** commit your `.env` file to GitHub.

---

# Database Setup

Create a PostgreSQL database for the application.

Then configure `DATABASE_URL` in `.env`.

Run the database migrations:

```bash
flask db upgrade
```

If migrations need to be created after a model change:

```bash
flask db migrate -m "describe your change"
```

Then apply them:

```bash
flask db upgrade
```

---

# Running the Application

Start the Flask development server:

```bash
python run.py
```

The API will normally be available at:

```text
http://127.0.0.1:5000
```

You can test the endpoints using **Postman**, `curl`, or another HTTP client.

---

# Example API Workflow

A typical workflow looks like this:

```text
1. Register
      ↓
2. Login
      ↓
3. Receive JWT access token
      ↓
4. Create shortened URL
      ↓
5. Receive short code
      ↓
6. Retrieve / update / delete the URL
      ↓
7. Check URL statistics
```

Example:

```text
Long URL
    ↓
https://example.com/some/very/long/path
    ↓
POST /shorten
    ↓
Short code
    ↓
7M4bAF
```

---

# Current Limitations

The project is currently focused on the backend API and does not yet include:

* A frontend dashboard
* Production deployment
* Docker containerization
* Redis caching
* Interactive Swagger/OpenAPI documentation
* QR code generation
* Custom domains
* Detailed click analytics
* Custom user-defined short codes

These are potential future improvements rather than current features.

---

# Future Improvements

Potential improvements include:

### API

* Add a public redirect endpoint
* Add pagination for user URLs
* Add more granular analytics
* Add custom short codes
* Improve API documentation with OpenAPI/Swagger

### Performance

* Add Redis caching
* Add database indexes where appropriate
* Improve handling of high-volume requests

### Deployment

* Dockerize the application
* Deploy the API to a cloud platform
* Use Gunicorn or another production WSGI server
* Add CI/CD with GitHub Actions

### Frontend

* Build a React dashboard
* Allow users to manage their shortened URLs
* Display click statistics and expiration information

---

# What I Learned

This project was built to develop practical backend development skills, including:

* Building REST APIs with Flask
* Designing relational database models
* Working with PostgreSQL
* Using SQLAlchemy ORM
* Managing database migrations
* Implementing JWT authentication
* Handling authorization and resource ownership
* Validating API input
* Implementing rate limiting
* Generating secure identifiers
* Writing automated API tests
* Managing environment variables
* Debugging backend and database issues

---

# License

This project is licensed under the MIT License.

---

## Author

**Birmachis Mulugeta**

GitHub: [Birmechis](https://github.com/Birmechis)
