# Weather API

A small weather service built with **FastAPI**.  
It fetches current weather data from **OpenWeatherMap**, caches responses using **Redis**, stores raw responses as JSON files, and logs request metadata in **SQLite**.

---

## API

### GET `/weather`

Returns current weather data for a given city.

**Query parameters**
- `city` (string, required)

**Example**
```bash
curl "http://localhost:8000/weather?city=Tbilisi"
```

## Respomse

```json
{
  "city": "Tbilisi",
  "timestamp_utc": "2026-02-18T12:41:30.123456+00:00",
  "source": "cache",
  "data": {
    "...": "raw OpenWeatherMap response"
  }
}

```

```source``` indicates whether the data was returned from cache or fetched live.

## API Documentation
Swagger UI: http://localhost:8000/docs
OpenAPI schema: http://localhost:8000/openapi.json

## Configuration

Create a ```.env``` file in the project root:
```dotenv
OPENWEATHER_API_KEY=your_api_key_here
REDIS_URL=redis://redis:6379/0
DATA_DIR=data
SQLITE_PATH=/app/db/app.db
CACHE_TTL_SECONDS=300
HTTP_TIMEOUT_SECONDS=10
UNITS=metric
```

## Running the Application
### Requirements

1.Docker

2.Docker Compose

3.OpenWeatherMap API key

4.Start the service


* 1Docker

* Docker Compose

* OpenWeatherMap API key

* Start the service


## Start the service
```commandline
docker compose up --build
```

The API will be available at:

http://localhost:8000

## Testing the API
### Using curl
```commandline
curl "http://localhost:8000/weather?city=Tbilisi"
```


Call the same endpoint twice within 5 minutes — the second response should have:

```json
"source": "cache"
```

## Checking Logs

Weather requests fetched from the upstream API are logged in SQLite.

View recent logs:

```commandline
 sqlite3 db/app.db "SELECT city, timestamp_utc, file_path FROM logs ORDER BY id DESC LIMIT 10;"
  ```

## Running Unite tests
### Create virtual environment
```commandline
python -m venv .venv
```

### install dependencies:
```commandline
pip install -r requirements.txt
```

###Run unit test:
```commandline
python -m pytest -q
```