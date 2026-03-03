# Smart Soil AI

## Overview
Smart Soil is a comprehensive solution combining an AI-powered FastAPI backend with a Flutter mobile application for real-time soil monitoring and crop prediction.

## Directory Structure
- `backend/`: Fast API server and Machine Learning models.
- `mobile_app/`: Flutter mobile application.

## How to Run

### 1. Backend (FastAPI)
The backend must be running for the mobile app to function correctly.

1.  Open a terminal.
2.  Navigate to the backend directory:
    ```powershell
    cd backend
    ```
3.  Run the server:
    ```powershell
    uvicorn main:app --reload --port 8000 --host 0.0.0.0
    ```
    *Note: `--host 0.0.0.0` allows the mobile emulator/device to access the server.*

### 2. Mobile App (Flutter)
1.  Open a **new** terminal (keep the backend running).
2.  Navigate to the mobile app directory:
    ```powershell
    cd mobile_app
    ```
3.  Install dependencies (if not already done):
    ```powershell
    flutter pub get
    ```
4.  Run the app:
    ```powershell
    flutter run
    ```

## Troubleshooting
- **"Error loading ASGI app"**: This means you are not in the `backend/` folder. Make sure to `cd backend` first.
- **"No pubspec.yaml file found"**: This means you are not in the `mobile_app/` folder. Make sure to `cd mobile_app` first.
