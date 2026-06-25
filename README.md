# QueueStorm Ticket Classification Service

A simple, robust, production-ready web service built with FastAPI to automatically classify customer support tickets for a digital finance company.

## Architecture

- **Framework:** FastAPI (Python 3.12)
- **Validation:** Pydantic models for strict schema compliance
- **Business Logic:** Rule-based keyword/regex matching engine separated into clean modules
- **Safety:** Independent safety layer blocking PI/OTP requests in agent summaries
- **Deployment:** Docker & Render-ready

## Folder Structure

- `app/main.py`: App entrypoint
- `app/api/`: Endpoint definitions (`/health`, `/sort-ticket`)
- `app/models/`: Pydantic schemas and Enums
- `app/services/`: Core logic (classification, summarization, safety)
- `app/utils/`: Shared constants and rules
- `tests/`: Comprehensive test suite

## Installation

```bash
# Clone the repository
git clone <repository_url>
cd <repository>

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env`. The default settings use rule-based logic.

```
LLM_ENABLED=false
LOG_LEVEL=INFO
```

## Running Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Usage

```bash
docker build -t queuestorm .
docker run -p 8000:8000 queuestorm
```

## API Examples

### Health Check

```bash
curl http://localhost:8000/health
```

### Classify Ticket

```bash
curl -X POST "http://localhost:8000/sort-ticket" \
     -H "Content-Type: application/json" \
     -d '{
           "ticket_id": "T-001",
           "channel": "app",
           "locale": "en",
           "message": "I sent 3000 taka to a wrong number this morning, please help me get it back"
         }'
```

## Testing

Run tests locally with pytest:

```bash
pytest tests/ -v
```
