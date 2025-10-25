# 🏛️ UAE Legal Agent

AI-powered legal analysis system pre právny systém Spojených arabských emirátov.

## 📋 Prehľad

UAE Legal Agent je expertný systém využívajúci Claude API pre:
- Analýzu právnych prípadov podľa UAE zákonov
- Generovanie alternatívnych právnych stratégií
- Risk assessment a cost estimation
- Citácie relevantných článkov zákonov

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Vytvor virtual environment
python -m venv venv

# Aktivuj
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Nainštaluj dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Vytvor `.env` súbor:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
MODEL_NAME=claude-sonnet-4-5-20250929
MAX_TOKENS=8000
```

### 3. Test API

```bash
python tests/test_claude_api.py
```

### 4. Run Server

```bash
uvicorn src.api.main:app --reload --port 8002
```

## 📂 Project Structure

```
uae-legal-agent/
├── src/               # Source code
│   ├── core/         # Core components (Claude client, config)
│   ├── api/          # FastAPI application
│   ├── rag/          # RAG pipeline
│   ├── agents/       # AI agent logic
│   ├── models/       # Pydantic models
│   └── db/           # Database models
├── data/             # Data storage
│   ├── laws/         # UAE law database
│   └── cases/        # Legal cases
├── tests/            # Test suite
├── docs/             # Documentation
└── config/           # Configuration files
```

## 🏗️ Architecture

- **Backend:** FastAPI (Python 3.11+)
- **AI:** Claude Sonnet 4.5 (Anthropic API)
- **RAG:** ChromaDB + Sentence Transformers
- **Database:** SQLite/PostgreSQL
- **Storage:** GitHub + Local files

## 📊 Features

- ✅ Case analysis with UAE law context
- ✅ Alternative strategy generation
- ✅ Per-case token tracking
- ✅ Cost estimation
- ✅ Conversation history
- ✅ Legal document processing
- 🚧 RAG pipeline (in progress)
- 🚧 Full API endpoints (in progress)

## 💰 Cost Tracking

```bash
# View token usage per case
python src/utils/token_report.py

# Estimate costs
python src/utils/cost_calculator.py --case-id abc-123
```

## 📚 Documentation

- [Setup Guide](docs/guides/setup.md)
- [API Documentation](docs/guides/api.md)
- [RAG Pipeline](docs/guides/rag.md)
- [Development Sessions](docs/sessions/)

## 👥 Team

- **Developer:** Zoltán Rauscher
- **Company:** ICC Komárno
- **Email:** [your-email]

## 📝 License

Proprietary - ICC Komárno

## 🔗 Links

- [Anthropic Console](https://console.anthropic.com)
- [Claude API Docs](https://docs.anthropic.com)
