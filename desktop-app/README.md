# Tauri + Svelte Desktop Application

A desktop application that provides a user interface for viewing and managing ride data. Communicates with the web-api to store and retrieve ride information.

## Prerequisites
- Node.js
- Rust toolchain
- Tauri CLI

## Installation
```bash
npm install
```

## Development
```bash
npm run tauri dev
```

## Build
```bash
npm run tauri build
```

## Important Note
This application requires the web-api to be running at http://localhost:8000 for full functionality. Make sure to start the web-api service before launching the desktop application.
