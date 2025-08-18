# UnitTest Generator API

Generate comprehensive unit tests for your code using local LLMs.

## Features

- Async API for generating unit tests
- Supports cancellation and status tracking
- Model selection via Ollama

## Requirements

- Docker
- Ollama running locally (default: `http://localhost:11434`)

## Quick Start (Docker Compose)

1. **Start Ollama**  
   Make sure Ollama is running locally:  
   [Ollama installation guide](https://ollama.com/download)

2. **Build and run the API**  
   In your project directory, run:
   ```sh
   docker compose up --build
   ```

3. **Access the API**  
   The API will be available at [http://localhost:8000](http://localhost:8000)

## Endpoints

- `GET /` — Welcome message
- `POST /generate/unit-test` — Start unit test generation
- `GET /status/{task_id}` — Check task status/result
- `POST /cancel/{task_id}` — Cancel a running task
- `GET /models` — List available models

## Development

To run locally (without Docker):

```sh
pip install -r requirements.txt
python main.py
```

## Environment Variables

- `OLLAMA_HOST` — Ollama server URL (default: `http://localhost:11434`)
- `RAGFLOW_BASE_URL` — Optional, for integrations

## License

MIT