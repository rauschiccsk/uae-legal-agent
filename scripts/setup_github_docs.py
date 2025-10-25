"""
UAE Legal Agent - GitHub Documentation Generator
Vytvorí všetky potrebné dokumentačné súbory pre GitHub
"""
from pathlib import Path
from datetime import datetime


def create_github_docs():
    """Vytvorí kompletné GitHub dokumenty"""

    print("=" * 70)
    print("📚 UAE Legal Agent - GitHub Documentation Generator")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    base_dir = Path(".")
    docs_dir = base_dir / "docs"
    sessions_dir = docs_dir / "sessions"

    # Ensure directories exist
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # ==================== INIT_CONTEXT.md ====================
    print("📝 Creating INIT_CONTEXT.md...")

    init_context = """# UAE Legal Agent - Project Context

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
venv\\Scripts\\activate  # Windows
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
"""

    with open(docs_dir / "INIT_CONTEXT.md", "w", encoding="utf-8") as f:
        f.write(init_context)
    print("✅ INIT_CONTEXT.md created")

    # ==================== project_file_access.json ====================
    print("📝 Creating project_file_access.json...")

    project_files = """{
  "project": "uae-legal-agent",
  "repository": "https://github.com/rauschiccsk/uae-legal-agent",
  "description": "AI-powered legal analysis system for UAE law",
  "files": {
    "documentation": {
      "init_context": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md",
      "readme": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/README.md",
      "latest_session": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/sessions/2025-10-25_session.md"
    },
    "source_code": {
      "claude_client": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/src/core/claude_client.py",
      "config": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/src/core/config.py",
      "api_main": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/src/api/main.py"
    },
    "tests": {
      "api_test": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/tests/test_claude_api.py"
    },
    "configuration": {
      "requirements_minimal": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/requirements-minimal.txt",
      "requirements_ultraminimal": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/requirements-ultraminimal.txt",
      "env_example": "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/.env.example"
    }
  },
  "quick_load": {
    "description": "Paste these two URLs to Claude for full project context",
    "urls": [
      "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md",
      "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json"
    ]
  }
}"""

    with open(docs_dir / "project_file_access.json", "w", encoding="utf-8") as f:
        f.write(project_files)
    print("✅ project_file_access.json created")

    # ==================== SESSION NOTE ====================
    print("📝 Creating session note...")

    session_note = f"""# UAE Legal Agent - Development Session
**Date:** 2025-10-25  
**Session:** Initial Setup & Claude API Integration  
**Duration:** ~2 hours  
**Developer:** Zoltán Rauscher  

## 🎯 Session Goals

1. Create new project for UAE Legal Agent
2. Setup Claude API integration
3. Test API connection
4. Establish GitHub documentation structure

## 📋 Tasks Completed

### 1. Project Generation ✅
**Task:** Create complete project structure  
**Method:** Python generator script (`create_legal_agent_project.py`)  
**Result:**
- 25 directories created
- 15 base files generated
- ~500 lines of initial code
- Complete .gitignore and documentation

**Time:** ~3 seconds (vs. 30-60 min manual) ⚡

### 2. Environment Setup ✅
**Task:** Python virtual environment & dependencies  
**Challenges:**
- ❌ Full requirements.txt failed (ChromaDB needs Rust compiler)
- ❌ Minimal requirements failed (httptools needs C++ compiler)
- ✅ Ultra-minimal requirements SUCCESS!

**Solution:**
```bash
pip install anthropic python-dotenv pydantic pydantic-settings
```

**Installed packages:** 4 core packages only  
**Time:** ~10 seconds

### 3. Claude API Integration ✅
**Task:** Setup and test Anthropic Claude API  
**Steps:**
1. Registered on console.anthropic.com (already had account via Claude MAX)
2. Created API key: `iccforai-claude-api-key`
3. Configured .env file
4. Tested connection

**Test Result:**
```
✅ API Connection: PASSED
✅ Slovak Response: PASSED
📊 Tokens: 40 input, 69 output (109 total)
💰 Cost: $0.001155
💳 Free Credit: $4.9988 remaining
```

**Response from Claude:**
> "Ahoj! Áno, samozrejme môžem odpovedať po slovensky.
> Spojenie funguje výborne. Som pripravený komunikovať s ICC Komárno Legal Agent v slovenčine."

### 4. GitHub Documentation ✅
**Task:** Prepare GitHub repository structure  
**Created:**
- INIT_CONTEXT.md - Complete project context
- project_file_access.json - File URL mappings
- This session note - 2025-10-25_session.md

## 🔧 Technical Decisions

### 1. Claude API vs. Chat Interface
**Decision:** Use Claude API directly  
**Reasoning:**
- Pay-as-you-go pricing (~$3-5/month)
- No 40k token reload between chats
- Persistent conversation history in database
- Per-case tracking
- Full automation capability

**Cost Comparison:**
- Chat Interface: $20/month flat + 40k tokens per chat reload
- API: $0.001 per query average = ~$3/month for 100 queries

### 2. Minimal Dependencies Strategy
**Decision:** Start with bare minimum packages  
**Reasoning:**
- Windows 32-bit Python has compilation issues
- ChromaDB (RAG) requires Rust compiler
- uvicorn[standard] requires C++ compiler
- Can add complex dependencies later when needed

**Current Stack:**
- anthropic (Claude API)
- python-dotenv (config)
- pydantic (settings)

**Deferred:**
- ChromaDB → Phase 2 (RAG pipeline)
- FastAPI → Phase 2 (API server)
- SQLAlchemy → Phase 2 (database)

### 3. Project Structure
**Decision:** Separate project from NEX Genesis Server  
**Reasoning:**
- Different domain (Legal vs. ERP)
- Different dependencies
- Easier maintenance
- Reusable for other UAE cases

## 📊 Metrics

### Time Investment
- Project generation: 3 seconds
- Dependencies troubleshooting: 20 minutes
- API setup & testing: 15 minutes
- Documentation: 30 minutes
- **Total:** ~65 minutes

### Token Usage
- Test queries: 109 tokens
- Cost: $0.001155
- Free credit used: 0.023%
- Remaining: $4.9988

### Files Created
- Python files: 15
- Markdown docs: 3
- Config files: 4
- Total: 22 files

## 🐛 Issues Encountered

### Issue 1: ChromaDB Installation Failed
**Error:** `Rust compiler required`  
**Solution:** Removed from requirements, deferred to Phase 2

### Issue 2: httptools Compilation Failed
**Error:** `Microsoft Visual C++ 14.0 required`  
**Solution:** Used ultra-minimal requirements without uvicorn[standard]

### Issue 3: Claude API 500 Error (initial)
**Error:** `Internal server error`  
**Cause:** API key verification issue  
**Solution:** Diagnostics confirmed key was valid, retry succeeded

## 💡 Lessons Learned

1. **Project Generator ROI:** 3 seconds vs. 30-60 minutes = 600× speedup
2. **Minimal Viable Setup:** Start with bare minimum, add complexity incrementally
3. **Windows 32-bit Constraints:** Many Python packages require compilation, avoid when possible
4. **Claude API Efficiency:** Much more token-efficient than chat interface for automation

## 🚀 Next Steps

### Immediate (Next Session)
1. Create GitHub repository: `rauschiccsk/uae-legal-agent`
2. Initial commit & push
3. Test legal analysis with real UAE case

### Phase 1: Legal Analysis Prototype
1. Manual UAE law input (Federal Law references)
2. Test case analysis with Money Laundering case
3. Generate alternative strategies
4. Risk assessment

### Phase 2: RAG Pipeline
1. Collect UAE law texts (Federal Laws)
2. Setup ChromaDB (resolve Rust compiler issue)
3. Implement semantic search
4. Integration with Claude client

### Phase 3: API Development
1. FastAPI endpoints
2. Database integration
3. Case management system
4. Per-case token tracking

## 📝 Notes

- Project successfully generated using automation script
- Claude API works perfectly with Slovak language
- Cost is minimal ($0.001 per typical query)
- Documentation structure mirrors NEX Genesis Server approach
- Ready for GitHub push and continued development

## 🔗 Related Resources

- **Anthropic Console:** https://console.anthropic.com
- **Claude API Docs:** https://docs.anthropic.com
- **Project Generator:** `create_legal_agent_project.py`
- **NEX Genesis Server:** Reference project structure

---

**Session End:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** ✅ Setup Complete, Ready for Development  
**Next Session:** Legal Analysis Prototype
"""

    with open(sessions_dir / "2025-10-25_session.md", "w", encoding="utf-8") as f:
        f.write(session_note)
    print("✅ 2025-10-25_session.md created")

    # ==================== GITHUB SETUP GUIDE ====================
    print("📝 Creating GitHub setup guide...")

    github_guide = """# GitHub Repository Setup Guide

## 🎯 Quick Setup

### 1. Create GitHub Repository

Go to: https://github.com/new

**Settings:**
- Repository name: `uae-legal-agent`
- Description: `AI-powered legal analysis system for UAE law`
- Visibility: Private (or Public if you prefer)
- ❌ DO NOT initialize with README (we have one)
- ❌ DO NOT add .gitignore (we have one)
- ❌ DO NOT add license (add later if needed)

Click **"Create repository"**

### 2. Initialize Git & Push

```bash
# Make sure you're in project directory
cd c:\\Development\\uae-legal-agent

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: UAE Legal Agent setup with Claude API integration"

# Add remote (replace 'rauschiccsk' with your GitHub username)
git remote add origin https://github.com/rauschiccsk/uae-legal-agent.git

# Push to GitHub
git push -u origin main
```

### 3. Verify Upload

Go to: https://github.com/rauschiccsk/uae-legal-agent

You should see:
- ✅ All files uploaded
- ✅ README.md displayed
- ✅ docs/ directory with documentation
- ✅ src/ directory with code

### 4. Test Context Loading

Try loading project in new Claude conversation:

```
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json
```

## 🔒 Security Checklist

Before pushing, verify:

- ✅ `.env` file is in `.gitignore`
- ✅ No API keys in committed files
- ✅ `.gitignore` includes all sensitive patterns
- ✅ `requirements.txt` doesn't expose internal URLs

## 📝 After Setup

1. Update repository description
2. Add topics: `ai`, `legal-tech`, `claude-api`, `uae`, `python`
3. Add README badge (optional)
4. Enable GitHub Actions (future)

## 🔗 URL Reference

After push, your URLs will be:

**Documentation:**
- INIT_CONTEXT: `https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md`
- File Access: `https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json`
- Latest Session: `https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/sessions/2025-10-25_session.md`

**Source Code:**
- Claude Client: `https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/src/core/claude_client.py`
- Config: `https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/src/core/config.py`

## ✅ Success Criteria

Your setup is complete when:

- [ ] GitHub repository is created
- [ ] All files pushed successfully
- [ ] INIT_CONTEXT.md loads in browser
- [ ] project_file_access.json contains valid URLs
- [ ] Claude can load project context via URLs
- [ ] No sensitive data exposed

---

Happy coding! 🚀
"""

    with open(docs_dir / "GITHUB_SETUP.md", "w", encoding="utf-8") as f:
        f.write(github_guide)
    print("✅ GITHUB_SETUP.md created")

    # ==================== SUMMARY ====================
    print("\n" + "=" * 70)
    print("✅ GITHUB DOCUMENTATION COMPLETE!")
    print("=" * 70)
    print("\n📂 Created files:")
    print("   ✅ docs/INIT_CONTEXT.md")
    print("   ✅ docs/project_file_access.json")
    print("   ✅ docs/sessions/2025-10-25_session.md")
    print("   ✅ docs/GITHUB_SETUP.md")

    print("\n🚀 Next steps:")
    print("   1. Review docs/GITHUB_SETUP.md")
    print("   2. Create GitHub repository")
    print("   3. Push initial commit")
    print("   4. Test context loading URLs")

    print("\n🔗 Quick URLs (after GitHub push):")
    print("   https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md")
    print("   https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json")
    print("\n")


if __name__ == "__main__":
    try:
        create_github_docs()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")