# URL Shortener API

A lightweight and efficient URL shortening service built with Flask. This application allows you to convert long URLs into short, manageable codes that are easy to share and track.

## What It Is

This URL Shortener is a RESTful API service that:
- Generates unique short codes for long URLs
- Stores URL mappings in a SQLite database
- Tracks access statistics for each shortened URL
- Provides full CRUD operations (Create, Read, Update, Delete)
- Uses cryptographically secure random code generation

## Features

- **URL Shortening**: Convert long URLs into short, unique codes (6 characters by default)
- **URL Retrieval**: Get the original URL using the short code
- **URL Updates**: Modify existing shortened URLs
- **URL Deletion**: Remove shortened URLs from the system
- **Access Tracking**: Monitor how many times a shortened URL has been accessed
- **Collision Prevention**: Ensures all generated short codes are unique
- **Timestamp Tracking**: Automatic tracking of creation and update times
- **Error Handling**: Comprehensive error responses for invalid requests

## Architecture

### Project Structure

```
url-shortening/
├── app/
│   ├── __init__.py          # Flask app factory and configuration
│   ├── models.py            # Database models (ShortURL)
│   └── routes.py            # API endpoints and business logic
├── tests/                   # Test suite (to be added)
├── .env.example             # Example environment configuration
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

**Note**: The following are generated at runtime and excluded from Git:
- `.venv/` - Virtual environment (recreated via `python -m venv .venv`)
- `instance/data.db` - SQLite database (created automatically on first run)
- `__pycache__/` - Python bytecode cache
- `.env` - Your local environment variables (use `.env.example` as template)

### Technology Stack

- **Framework**: Flask 3.1.3
- **Database**: SQLite (via Flask-SQLAlchemy 3.1.1)
- **ORM**: SQLAlchemy 2.0.52
- **Environment**: Python 3.x with virtual environment
- **Code Generation**: Python `secrets` module for cryptographically secure random codes

### Database Schema

**ShortURL Model**:
- `id` (Integer, Primary Key): Unique identifier
- `url` (Text, Not Null): Original long URL
- `shortCode` (String, Not Null): Generated short code (6 characters)
- `createdAt` (DateTime, Not Null): Creation timestamp (UTC)
- `updatedAt` (DateTime, Not Null): Last update timestamp (UTC)
- `accessCount` (Integer, Not Null): Number of times accessed

## API Endpoints

### 1. Create Shortened URL

**POST** `/shorten`

Create a new shortened URL.

**Request Body**:
```json
{
  "url": "https://www.example.com/very/long/url/that/needs/shortening"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "url": "https://www.example.com/very/long/url/that/needs/shortening",
  "shortCode": "aB3xYz",
  "createdAt": "2026-09-10T14:30:00.000000",
  "updatedAt": "2026-09-10T14:30:00.000000"
}
```

### 2. Get Original URL

**GET** `/shorten/<shortCode>`

Retrieve the original URL using a short code.

**Response** (200 OK):
```json
{
  "id": 1,
  "url": "https://www.example.com/very/long/url/that/needs/shortening",
  "createdAt": "2026-09-10T14:30:00.000000",
  "updatedAt": "2026-09-10T14:30:00.000000"
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "URL parameter is required"
}
```

### 3. Update Shortened URL

**PUT** `/shorten/<shortCode>`

Update the destination URL for an existing short code.

**Request Body**:
```json
{
  "url": "https://www.example.com/new/destination"
}
```

**Response** (200 OK):
```json
{
  "url": "https://www.example.com/new/destination"
}
```

### 4. Delete Shortened URL

**DELETE** `/shorten/<shortCode>`

Remove a shortened URL from the system.

**Response** (200 OK):
```json
{
  "success": true
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "URL parameter is not found"
}
```

### 5. Get URL Statistics

**GET** `/shorten/<shortCode>/stats`

Retrieve statistics for a shortened URL, including access count.

**Response** (200 OK):
```json
{
  "id": 1,
  "url": "https://www.example.com/very/long/url/that/needs/shortening",
  "shortCode": "aB3xYz",
  "createdAt": "2026-09-10T14:30:00.000000",
  "updatedAt": "2026-09-10T14:30:00.000000",
  "accessCount": 42
}
```

## Technologies Used

- **Flask**: Lightweight WSGI web application framework
- **Flask-SQLAlchemy**: Flask extension for SQLAlchemy ORM
- **SQLite**: Embedded relational database
- **python-dotenv**: Environment variable management
- **secrets**: Cryptographically strong random number generation
- **Werkzeug**: WSGI utility library

## How to Run

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "url shortening"
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `.env` file** from the example:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```
   
   The `.env` file should contain:
   ```env
   DATABASE_URL=sqlite:///instance/data.db
   ```

6. **Run the application**:
   ```bash
   python run.py
   ```

7. **Access the API**:
   The server will start at `http://127.0.0.1:5000`

## Example Requests/Responses

### Using cURL

**Create a shortened URL**:
```bash
curl -X POST http://127.0.0.1:5000/shorten \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.github.com/user/repository\"}"
```

**Get original URL**:
```bash
curl http://127.0.0.1:5000/shorten/aB3xYz
```

**Update URL**:
```bash
curl -X PUT http://127.0.0.1:5000/shorten/aB3xYz \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.github.com/user/new-repository\"}"
```

**Get statistics**:
```bash
curl http://127.0.0.1:5000/shorten/aB3xYz/stats
```

**Delete URL**:
```bash
curl -X DELETE http://127.0.0.1:5000/shorten/aB3xYz
```

### Using Python Requests

```python
import requests

# Create shortened URL
response = requests.post(
    "http://127.0.0.1:5000/shorten",
    json={"url": "https://www.example.com/long/url"}
)
data = response.json()
short_code = data["shortCode"]
print(f"Short code: {short_code}")

# Get original URL
response = requests.get(f"http://127.0.0.1:5000/shorten/{short_code}")
print(response.json())

# Get statistics
response = requests.get(f"http://127.0.0.1:5000/shorten/{short_code}/stats")
print(f"Access count: {response.json()['accessCount']}")
```

## Future Improvements

### Short-term Enhancements
- [ ] **Custom Short Codes**: Allow users to specify their own custom short codes
- [ ] **URL Validation**: Add validation to ensure URLs are properly formatted
- [ ] **Redirect Endpoint**: Add a redirect endpoint that automatically redirects to the original URL
- [ ] **Expiration Dates**: Implement URL expiration with configurable TTL
- [ ] **Rate Limiting**: Prevent abuse with request rate limiting

### Medium-term Features
- [ ] **Analytics Dashboard**: Web interface for viewing URL statistics
- [ ] **Click Tracking**: Track detailed analytics (referrer, user agent, geographic location)
- [ ] **User Authentication**: Multi-user support with API keys
- [ ] **QR Code Generation**: Generate QR codes for shortened URLs
- [ ] **Bulk Operations**: Support for creating/managing multiple URLs at once

### Long-term Goals
- [ ] **PostgreSQL Support**: Migration to PostgreSQL for better scalability
- [ ] **Caching Layer**: Redis integration for improved performance
- [ ] **Docker Deployment**: Containerization for easy deployment
- [ ] **API Documentation**: Interactive API documentation with Swagger/OpenAPI
- [ ] **Link Preview**: Generate preview cards for shared links
- [ ] **Password Protection**: Optional password protection for sensitive URLs
- [ ] **Custom Domains**: Support for custom short domains
- [ ] **A/B Testing**: Support for multiple destination URLs with traffic splitting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using Flask**
