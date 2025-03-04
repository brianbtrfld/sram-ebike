# E-Bike Telemetry App

This project provides a complete solution for processing and visualizing e-bike telemetry data. It consists of a web API backend and a desktop application frontend.

## Main Components

### 1. web-api
A FastAPI-based web service that handles ride data storage and processing. Provides REST endpoints for the desktop application to interact with ride data.

**Installation:**
```bash
cd web-api
pip install "fastapi[standard]"
pip install -r requirements.txt
```

**Usage:**
```bash
cd web-api
uvicorn app.main:app --reload
```

**Testing:**
```bash
cd web-api
pytest -v
```

The API will be available at http://localhost:8000

### 2. desktop-app
A Tauri + Svelte desktop application that provides a user interface for viewing and managing ride data. Communicates with the web-api to store and retrieve ride information.

**Prerequisites:**
- Node.js
- Rust toolchain
- Tauri CLI

**Installation:**
```bash
cd desktop-app
npm install
```

**Development:**
```bash
npm run tauri dev
```

**Build:**
```bash
npm run tauri build
```

## Important Note
The desktop application requires the web-api to be running at http://localhost:8000 for full functionality. Make sure to start the web-api service before launching the desktop application.

## Utilities

### utils-gpx
A Python utility for converting GPX files to JSON format with additional ride metrics. This tool can be used to process raw GPX data and calculate various statistics like distance, elevation gain, and speed metrics.

**Installation:**
```bash
cd utils-gpx
pip install -r requirements.txt
```

**Usage:**
```bash
python main.py ride.gpx -o ride.json
```