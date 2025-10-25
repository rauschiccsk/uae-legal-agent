# UAE Legal Agent - Project Context

**Project:** UAE Legal Agent  
**Repository:** https://github.com/rauschiccsk/uae-legal-agent  
**Created:** 2025-10-25  
**Author:** Zoltán Rauscher  
**Company:** ICC Komárno  
**Status:** Active Development  

## 🎯 Project Overview

AI-powered legal analysis system špecializovaný na právny systém Spojených arabských emirátov (UAE).

### Purpose
Automatizácia právnej analýzy UAE prípadov pomocou Claude API s RAG (Retrieval Augmented Generation) pre presné citácie zákonov a generovanie alternatívnych právnych stratégií.

### Key Features
- ✅ Legal case analysis s UAE law context
- ✅ Alternative strategy generation (3-5 options)
- ✅ Per-case token tracking & cost estimation
- ✅ Conversation history persistence
- 🚧 RAG pipeline (ChromaDB + embeddings) - in progress
- 🚧 FastAPI REST endpoints - in progress
- 🚧 Database integration - in progress

## 🏗️ Architecture

### Technology Stack
- **Backend:** Python 3.11+ (32-bit compatible)
- **AI Engine:** Claude Sonnet 4.5 (Anthropic API)
- **RAG:** ChromaDB + Sentence Transformers (planned)
- **API:** FastAPI (planned)
- **Database:** SQLite/PostgreSQL (planned)
- **Storage:** GitHub + Local files

### Core Components

```
uae-legal-agent/
├── src/
│   ├── core/
│   │   ├── claude_client.py        ✅ Claude API wrapper (COMPLETE)
│   │   └── config.py               ✅ Configuration management
│   ├── api/                        🚧 FastAPI application (planned)
│   ├── rag/                        🚧 RAG pipeline (planned)
│   └── agents/                     🚧 AI agent logic (planned)
├── data/
│   ├── laws/                       📁 UAE law database
│   └── cases/                      📁 Legal cases storage
├── tests/                          ✅ Test suite (basic)
└── docs/                           ✅ Documentation
```

## 📊 Current Status

### Phase 0: Setup & Foundation - COMPLETE ✅
**Progress:** 100%

**Completed Tasks:**
- ✅ Project structure created (25 directories, 15 files)
- ✅ Python virtual environment setup
- ✅ Claude API integration & testing
- ✅ Basic configuration management
- ✅ Token tracking & cost calculation
- ✅ Git repository initialized
- ✅ Documentation framework

**Test Results:**
```
✅ Claude API Connection: PASSED
✅ Slovak language response: PASSED
✅ Token tracking: PASSED (109 tokens, $0.001155)
✅ Free credit remaining: $4.9988
```

### Phase 1: Legal Analysis Prototype - NEXT
**Progress:** 0%

**Planned Tasks:**
1. Test legal analysis s real UAE case
2. Manual law input (Federal Law references)
3. Alternative strategy generation
4. Risk assessment implementation

### Phase 2: RAG Pipeline - PLANNED
**Progress:** 0%

**Planned Tasks:**
1. UAE law database collection
2. Text chunking & embeddings
3. ChromaDB vector store setup
4. Semantic search implementation

### Phase 3: API Development - PLANNED
**Progress:** 0%

**Planned Tasks:**
1. FastAPI endpoints
2. Case management system
3. Database integration
4. Authentication & authorization

## 🔑 API Keys & Configuration

### Required Environment Variables (.env)
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...      # Claude API key
MODEL_NAME=claude-sonnet-4-5-20250929   # Claude model
MAX_TOKENS=8000                          # Max response tokens
```

### API Pricing
- **Input:** $3 per 1M tokens
- **Output:** $15 per 1M tokens
- **Free credit:** $5 starting credit
- **Estimated monthly cost:** $3-5 USD (100 queries)

## 📚 Documentation Structure

### Main Documents
- `README.md` - Project overview & quick start
- `INIT_CONTEXT.md` - This document (project context)
- `project_file_access.json` - File URLs for Claude context loading

### Guides (docs/guides/)
- Setup guide (planned)
- API documentation (planned)
- RAG pipeline guide (planned)

### Session Notes (docs/sessions/)
- `2025-10-25_session.md` - Initial setup & Claude API testing

## 🎓 Development Methodology

### GitHub-Based Context Loading
Single-URL loading pattern pre Claude conversations:
```
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json
```

### Session Documentation
- Každá development session má markdown note
- Progress tracking per phase
- Token usage logging
- Decision documentation

## 🚀 Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/rauschiccsk/uae-legal-agent.git
cd uae-legal-agent
```

### 2. Setup Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements-ultraminimal.txt
```

### 3. Configure API Key
```bash
copy .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 4. Test Connection
```bash
python tests/test_claude_api.py
```

### 5. Load Project Context
```
Paste these URLs to Claude:
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json
```

## 💡 Next Steps

1. ✅ Create GitHub repository
2. ✅ Push initial commit
3. 🎯 Test legal analysis prototype
4. 📊 Collect UAE law texts
5. 🔧 Build RAG pipeline
6. 🌐 Implement FastAPI endpoints

## 📞 Contact

**Developer:** Zoltán Rauscher  
**Company:** ICC Komárno  
**Project Start:** October 25, 2025  

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
