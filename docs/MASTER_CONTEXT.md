# 🏛️ UAE LEGAL AGENT - MASTER KONTEXT

**Rýchly Referenčný Návod**

---

## 🎯 Čo je to?

**AI-powered legal analysis system** pre právny systém SAE:
- ⚖️ Analýza právnych prípadov
- 📚 Citovanie UAE zákonov
- 🎯 Generovanie alternatívnych stratégií
- 📊 Risk & cost assessment
- 💬 Slovenský output pre klientov

**Technológia:** Claude Sonnet 4.5 API + RAG + ChromaDB

---

## 🚀 Rýchly Štart

```bash
# 1. Clone
git clone https://github.com/rauschiccsk/uae-legal-agent.git
cd uae-legal-agent

# 2. Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure
copy .env.example .env
# Pridaj CLAUDE_API_KEY do .env

# 4. Test
pytest tests/ -v

# Hotovo! ✅
```

---

## 📋 Kľúčové Súbory

| Súbor | Účel | Umiestnenie |
|------|------|-------------|
| **INIT_CONTEXT.md** | Kompletný project context | `docs/` |
| **project_file_access.json** | URL manifest | `docs/` |
| **SYSTEM_PROMPT.md** | Claude inštrukcie | `docs/` |
| **config.py** | Project configuration | `root` |
| **main.py** | CLI entry point | `root` |
| **claude_client.py** | Claude API wrapper | `utils/` |
| **vector_db.py** | ChromaDB interface | `utils/` |
| **pdf_processor.py** | PDF extraction | `utils/` |
| **.env** | API keys (LOCAL ONLY!) | root |

---

## 💾 Tech Stack

```yaml
AI: Claude Sonnet 4.5 (Anthropic API)
Backend: Python 3.11+
RAG: ChromaDB + Embeddings
PDF: PyMuPDF (fitz) for text extraction
Config: Pydantic Settings, python-dotenv
Testing: pytest (97.6% coverage)
CLI: argparse-based main.py
```

---

## 🏗️ Architektúra

```
PDF Document
    ↓
PDF Processor (PyMuPDF)
    ↓
Text Chunks
    ↓
ChromaDB (Vector Store)
    ↓
Semantic Search
    ↓
Claude API + Context
    ↓
Legal Analysis
    ↓
Slovak Output
```

---

## 📊 Stav Vývoja

**Aktuálna Fáza:** Phase 1 - Core Modules Implementation  
**Progress:** 5/9 modules completed (56%)  
**Test Coverage:** 80/82 tests passing (97.6%)  
**Free Credit:** ~$4.50 USD zostáva

**Moduly Status:**
- ✅ logger.py: 8/8 tests (100%)
- ✅ text_processing.py: 14/14 tests (100%)
- ✅ config.py: 18/18 tests (100%)
- ✅ pdf_processor.py: 19/19 tests (100%)
- ✅ claude_client.py: 21/23 tests (91%)
- 🚧 vector_db.py: Implementation ready, needs tests
- 📅 embeddings.py: Planned
- 📅 api/endpoints.py: Planned
- 📅 Integration tests: Planned

**Fázy:**
1. **Phase 0: Setup** ✅ (Complete)
2. **Phase 1: Core Modules** 🔥 (In Progress - 56%)
3. **Phase 2: Vector DB Integration** 📅 (Next)
4. **Phase 3: API & Production** 📅 (Planned)

---

## 📁 Project Structure

```
uae-legal-agent/
├── config.py                ✅ Project configuration (root)
├── main.py                  ✅ CLI entry point
├── docs/                    # Documentation
│   ├── INIT_CONTEXT.md
│   ├── MASTER_CONTEXT.md
│   ├── SYSTEM_PROMPT.md
│   └── sessions/            # Development sessions
├── utils/                   # Core modules
│   ├── claude_client.py     ✅ Claude API wrapper
│   ├── config.py            ⚠️  Generic template (unused)
│   ├── logger.py            ✅ Logging utility
│   ├── pdf_processor.py     ✅ PDF text extraction
│   ├── text_processing.py   ✅ Text cleaning
│   └── vector_db.py         🚧 ChromaDB interface
├── scripts/                 # Utility scripts
│   ├── generate_project_access.py
│   └── dev_chat.py
├── tests/                   # Test suite (80/82 passing)
│   ├── test_claude_api.py   ✅ 21/23 tests
│   ├── test_pdf_processor.py ✅ 19/19 tests
│   ├── test_config.py       ✅ 18/18 tests
│   └── ...
├── data/
│   ├── documents/           📁 Legal PDFs
│   └── chroma_db/           📁 Vector database
├── .env                     🔒 API keys (gitignored)
└── requirements*.txt        📦 Dependencies
```

---

## 🎯 Kritériá Úspechu

**Phase 0 (DONE):**
- ✅ Claude API funguje
- ✅ Token tracking
- ✅ Cost calculation
- ✅ Slovak responses
- ✅ GitHub repository

**Phase 1 (IN PROGRESS - 56%):**
- ✅ Logger module with comprehensive tests
- ✅ Text processing utilities
- ✅ Configuration management
- ✅ PDF extraction and parsing
- ✅ Claude API wrapper with retry logic
- 🚧 Vector DB integration (implementation ready)
- 📅 Embeddings generation
- 📅 End-to-end integration tests

**Phase 2 (NEXT):**
- 🎯 Complete Vector DB with tests
- 🎯 Document chunking strategy
- 🎯 Semantic search implementation
- 🎯 RAG pipeline integration

---

## 💰 API Costs

**Claude Sonnet 4.5:**
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Free credit: $5 ($4.50 zostáva)

**Typical Query:**
- ~2,500 input + 1,200 output = ~$0.026
- 100 queries = ~$2.60/month
- **Super lacné!** 💪

---

## 🔧 Bežné Úlohy

### Načítaj Project Context
```
URL1: https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md
URL2: https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json
```

### Test Modules
```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_pdf_processor.py -v

# With coverage
pytest tests/ --cov=utils --cov-report=html
```

### Legal Analysis
```python
from utils.claude_client import ClaudeClient
from config import settings

client = ClaudeClient(api_key=settings.CLAUDE_API_KEY)
result = client.analyze_legal_case(
    case_context="...",
    legal_context="...",
    query="Aké sú alternatívy k väzbe?"
)

# Result includes: response, input_tokens, output_tokens, cost_usd
```

### Process PDF Document
```python
from utils.pdf_processor import process_legal_pdf

result = process_legal_pdf("path/to/uae_law.pdf")
# Returns: text, metadata, structured_content, errors
```

### Vector DB Operations
```python
from utils.vector_db import VectorDB

db = VectorDB(collection_name="uae_laws")
db.initialize_db()

# Add document
db.add_document(text="Article 1...", metadata={"law": "31/2021"})

# Search
results = db.search(query="money laundering", n_results=5)
```

### Check Token Usage
```bash
# View API logs
cat logs\api_usage.jsonl
```

---

## 📞 Zdroje

- **GitHub:** https://github.com/rauschiccsk/uae-legal-agent
- **Lokálne:** c:\Development\uae-legal-agent
- **Context URL:** https://raw.githubusercontent.com/.../INIT_CONTEXT.md
- **Developer:** Zoltán Rauscher (ICC Komárno)
- **Anthropic Console:** https://console.anthropic.com

---

## 🎓 Use Cases

### Real Case - Money Laundering
```yaml
Klient: Andros Business FZE
Obvinenie: Money laundering
Suma: AED 2,500,000
Status: Bail posted, awaiting trial
Documents: FIU report, bail order, court receipts

Query: "Aké sú alternatívy k väzbe?"

Expected Output:
- 3-5 alternative strategies
- Federal Law citations
- Risk assessment (Low/Med/High)
- Timeline estimates
- Cost estimates
```

---

## ⚙️ Configuration

### .env Template
```bash
CLAUDE_API_KEY=sk-ant-api03-your-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.7

CHROMA_PERSIST_DIRECTORY=data/chroma_db
CHROMA_COLLECTION_NAME=uae_legal_docs

DATA_DIR=data
LOGS_DIR=logs
DOCUMENTS_DIR=data/documents
```

### API Rate Limits
- Free tier: 50 requests/min
- Plenty for legal analysis use case

---

## 🔍 Troubleshooting

### API 500 Error
- Check API key validity
- Verify no extra spaces in .env
- Try new API key from console

### Token Limits
- Max per request: 200k tokens context window
- Chunk long documents if needed

### Dependencies Issues
- Use `requirements.txt` (all deps)
- ChromaDB requires build tools on some systems
- PyMuPDF may need manual install on 32-bit Windows

### Import Errors
- Check config.py in root (not utils/config.py)
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

---

## 📈 Roadmap

**Week 1:** ✅ Setup + Core modules (56% done)  
**Week 2:** 🎯 Vector DB + Tests (next)  
**Week 3-4:** RAG pipeline + Integration  
**Week 5-6:** API endpoints + Production  
**Week 7+:** Deployment + Documentation  

---

**Verzia:** 1.1.0  
**Aktualizované:** 2025-10-30  
**Stav:** Active Development - Phase 1 (56%)

🏛️ **AI Legal Expert. UAE Law Specialist. Slovak Output.** ⚖️