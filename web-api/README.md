# FastAPI Web API

A FastAPI-based web service that handles ride data storage and processing. Provides REST endpoints for the desktop application to interact with ride data.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Testing
The project includes a comprehensive test suite covering models, routes, and services. Run the tests using:
```bash
pytest -v
```

This will run all tests with verbose output, showing the results of each individual test. The test suite includes:
- Model validation tests
- API endpoint tests
- Ride summary calculation tests

Note: This service is required to be running for the desktop application to function properly.