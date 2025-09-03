# Unitest-API

## How to Run


### 1. Install dependencies (Recommended: Use Python venv)

Create and activate a virtual environment:

```sh
python -m venv venv
```

On Windows (PowerShell):
```sh
.\venv\Scripts\Activate.ps1
```

On Windows (cmd):
```sh
venv\Scripts\activate.bat
```

On Linux/macOS:
```sh
source venv/bin/activate
```

Then install dependencies:
```sh
pip install -r requirements.txt
```

### 2. Start the API server

```sh
python main.py
```

The API will be available at [http://localhost:8000](http://localhost:8000).

You can test endpoints using the included `UnitTestGenerator.postman_collection.json` or interact with the OpenAPI docs at [http://localhost:8000/docs](http://localhost:8000/docs).

---


## Run with Docker

### Option 1: Docker Compose (Recommended)

1. Make sure `docker-compose.yml` and `Dockerfile` exist in the project root.
2. Start the service:

```sh
docker-compose up --build
```

This will build and run the API, mapping port 8000.

### Option 2: Manual Docker Build

1. Build the Docker image:
```sh
docker build -t unitest-api .
```
2. Run the Docker container:
```sh
docker run -p 8000:8000 unitest-api
```

---

## Files
- `main.py`: FastAPI server entry point
- `requirements.txt`: Python dependencies
- `UnitTestGenerator.postman_collection.json`: Postman collection for API testing
- `Dockerfile`: Docker build instructions

---

## Troubleshooting
- If you see `failed to read dockerfile: open Dockerfile: no such file or directory`, ensure the file is named `Dockerfile` (not `DockerFile`) and is in the project root.
- For other issues, check the logs and ensure all dependencies are installed.
