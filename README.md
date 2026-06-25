# QueueStorm Ticket Classification Service

A simple, robust, production-ready web service built with FastAPI to automatically classify customer support tickets for a digital finance company.

## Architecture

- **Framework:** FastAPI (Python 3.12)
- **Validation:** Pydantic models for strict schema compliance
- **Business Logic:** Gemini LLM (1.5 Flash) integration for intelligent classification with a deterministic rule-based (Regex word boundary) matching engine as an unbreakable fallback.
- **Safety:** Independent Python safety layer strictly verifying LLM outputs to block PI/OTP requests in agent summaries.
- **Deployment:** Vercel serverless routing, with Docker & Render fallback capabilities.

## Folder Structure

- `app/main.py`: App entrypoint
- `app/api/`: Endpoint definitions (`/health`, `/sort-ticket`)
- `app/models/`: Pydantic schemas and Enums
- `app/services/`: Core logic (LLM classification, fallback engine, safety verifier)
- `app/utils/`: Shared regex constants and rules
- `tests/`: Comprehensive edge-case test suite
- `vercel.json`: Vercel serverless deployment routing

## Installation

```bash
# Clone the repository
git clone <repository_url>
cd Mock-SUST

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env`. Enable the LLM by passing your Gemini API key. If the LLM is disabled or fails, the application automatically falls back to deterministic rule-based logic.

```
LLM_ENABLED=true
LLM_API_KEY=your_gemini_api_key
LOG_LEVEL=INFO
```

## Running Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Deployment

### Deploy to Vercel (Recommended)
This repository includes a `vercel.json` and is ready for 1-click deployment on Vercel:
1. Import this repository into Vercel via the dashboard.
2. Add the environment variables `LLM_ENABLED=true` and your `LLM_API_KEY`.
3. Deploy! Vercel will automatically resolve the Python dependencies and route traffic.

### Docker Usage
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
