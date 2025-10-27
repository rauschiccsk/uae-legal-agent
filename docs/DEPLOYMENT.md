# 🚀 Deployment Guide

## Quick Start (Windows 32-bit)

### 1. Install Pure Python Dependencies

```bash
pip install -r requirements-production.txt
```

**Why production requirements?**
- No compilation needed (no Rust, no C++)
- Pure Python packages only
- Works on Windows 32-bit
- 10-second install

### 2. Configure Environment

Create `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
MODEL_NAME=claude-sonnet-4-5-20250929
MAX_TOKENS=8000
```

### 3. Run Lite Server

**Option A: Batch Script (Recommended)**
```bash
RUN_SERVER.bat
```

**Option B: Direct Python**
```bash
python src/api/lite_server.py
```

**Option C: Uvicorn CLI**
```bash
uvicorn src.api.lite_server:app --host 0.0.0.0 --port 8002
```

### 4. Test API

Open browser: `http://localhost:8002/docs`

Or use curl:
```bash
curl http://localhost:8002/health
```

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "api_connected": true,
  "model": "claude-sonnet-4-5-20250929"
}
```

### Analyze Case
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "case_description": "Client wants to break lease contract early...",
  "relevant_laws": ["UAE Civil Code"],
  "client_goal": "Minimize penalties"
}
```

Response:
```json
{
  "analysis": "Detailná právna analýza...",
  "strategies": [
    "1. Negociácia s majiteľom",
    "2. Nájdenie náhradného nájomcu",
    "..."
  ],
  "risks": ["Risk 1", "Risk 2"],
  "estimated_cost": "AED 5,000",
  "tokens_used": 1250,
  "model": "claude-sonnet-4-5-20250929"
}
```

## Production Deployment

### Option 1: Windows Server

1. Install Python 3.11 (32-bit or 64-bit)
2. Clone repository
3. Run `RUN_SERVER.bat`
4. Configure IIS reverse proxy (optional)

### Option 2: Linux Server (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt  # Full version with ChromaDB

# Run with systemd
sudo systemctl start uae-legal-agent
```

### Option 3: Docker (Future)

```bash
docker build -t uae-legal-agent .
docker run -p 8002:8002 --env-file .env uae-legal-agent
```

## Performance

- **Cold start:** ~500ms
- **Average request:** 2-5 seconds
- **Concurrent requests:** 10+ (async)
- **Memory:** ~150MB base + Claude API calls

## Troubleshooting

### Error: "No module named 'anthropic'"
```bash
pip install -r requirements-production.txt
```

### Error: "API key not found"
Check `.env` file exists and contains valid key

### Error: "Address already in use"
Port 8002 is occupied, change in code or use:
```bash
python src/api/lite_server.py --port 8003
```

## Cost Monitoring

Each request logs token usage. Monitor with:
```bash
curl http://localhost:8002/api/v1/stats
```

## Next Steps

- [ ] Add persistent token tracking (SQLite)
- [ ] Implement RAG pipeline (Phase 2)
- [ ] Add authentication
- [ ] Deploy to cloud (Azure/AWS)