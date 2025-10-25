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

**Technológia:** Claude Sonnet 4.5 API + RAG + FastAPI

---

## 🚀 Rýchly Štart

```bash
# 1. Clone
git clone https://github.com/rauschiccsk/uae-legal-agent.git
cd uae-legal-agent

# 2. Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements-ultraminimal.txt

# 3. Configure
copy .env.example .env
# Pridaj ANTHROPIC_API_KEY do .env

# 4. Test
python tests\test_claude_api.py

# Hotovo! ✅
```

---

## 📋 Kľúčové Súbory

| Súbor | Účel | Umiestnenie |
|------|------|-------------|
| **INIT_CONTEXT.md** | Kompletný project context | `docs/` |
| **project_file_access.json** | URL manifest | `docs/` |
| **SYSTEM_PROMPT.md** | Claude inštrukcie | `docs/` |
| **claude_client.py** | Claude API wrapper | `src/core/` |
| **test_claude_api.py** | API connection test | `tests/` |
| **.env** | API keys (LOCAL ONLY!) | root |

---

## 💾 Tech Stack

```yaml
AI: Claude Sonnet 4.5 (Anthropic API)
Backend: Python 3.11+ (32-bit compatible)
RAG: ChromaDB + Sentence Transformers (planned)
API: FastAPI (planned)
Database: SQLite (planned)
Config: python-dotenv, Pydantic
```

---

## 🏗️ Architektúra

```
Case Context + Query
        ↓
    Claude API
   (UAE Legal Expert)
        ↓
   Analysis Response
 (3-5 Alternatives)
        ↓
   Slovak Output
```

**Budúcnosť (RAG):**
```
Query → RAG Search → UAE Laws → Claude → Analysis
```

---

## 📊 Stav Vývoja

**Aktuálna Fáza:** Phase 0 Complete, Phase 1 Next  
**Progress:** Setup 100%, Legal Analysis 0%  
**Free Credit:** ~$4.99 USD zostáva

**Fázy:**
1. **Phase 0: Setup** ✅ (Complete) - 1 deň
2. **Phase 1: Prototype** 🔥 (Next) - 2-3 dni
3. **Phase 2: RAG Pipeline** 📅 (Planned) - 1-2 týždne
4. **Phase 3: Production** 📅 (Planned) - 1-2 týždne

---

## 📁 Project Structure

```
uae-legal-agent/
├── docs/                    # Documentation
│   ├── INIT_CONTEXT.md
│   ├── MASTER_CONTEXT.md
│   ├── SYSTEM_PROMPT.md
│   └── sessions/
├── src/
│   ├── core/
│   │   ├── claude_client.py  ✅ Core AI client
│   │   └── config.py         ✅ Settings
│   ├── api/                  🚧 FastAPI (planned)
│   ├── rag/                  🚧 Vector search (planned)
│   └── agents/               🚧 AI logic (planned)
├── data/
│   ├── laws/                 📁 UAE law database
│   └── cases/                📁 Legal cases
├── tests/
│   └── test_claude_api.py    ✅ Working
├── .env                      🔒 API keys (gitignored)
└── requirements-*.txt        📦 Dependencies
```

---

## 🎯 Kritériá Úspechu

**Phase 0 (DONE):**
- ✅ Claude API funguje
- ✅ Token tracking
- ✅ Cost calculation
- ✅ Slovak responses
- ✅ GitHub repository

**Phase 1 (NEXT):**
- 🎯 Legal analysis prototype
- 🎯 Alternative strategy generation
- 🎯 Risk assessment
- 🎯 Test s real UAE case

---

## 💰 API Costs

**Claude Sonnet 4.5:**
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Free credit: $5 ($4.99 zostáva)

**Typical Query:**
- ~2,500 input + 1,200 output = ~$0.026
- 100 queries = ~$2.60/month
- **Super lacné!** 💪

---

## 🔧 Bežné Úlohy

### Načítaj Project Context
```
URL1: https://raw.githubusercontent.com/.../INIT_CONTEXT.md
URL2: https://raw.githubusercontent.com/.../project_file_access.json
```

### Test Claude API
```bash
python tests\test_claude_api.py
```

### Legal Analysis (budúce)
```python
from src.core.claude_client import ClaudeClient

client = ClaudeClient()
result = client.analyze_case(
    case_context="...",
    legal_context="...",
    query="Aké sú alternatívy k väzbe?"
)
```

### Check Token Usage
```bash
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
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
MODEL_NAME=claude-sonnet-4-5-20250929
MAX_TOKENS=8000
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
- Use `requirements-ultraminimal.txt` (pure Python)
- ChromaDB requires Rust (skip for now)
- FastAPI needs C++ (skip for now)

---

## 📈 Roadmap

**Week 1:** ✅ Setup complete  
**Week 2:** 🎯 Legal analysis prototype  
**Week 3-4:** RAG pipeline + UAE laws  
**Week 5-6:** FastAPI + Database  
**Week 7+:** Production deployment  

---

**Verzia:** 1.0.0  
**Aktualizované:** 2025-10-25  
**Stav:** Active Development

🏛️ **AI Legal Expert. UAE Law Specialist. Slovak Output.** ⚖️