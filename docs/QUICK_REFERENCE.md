# 🚀 UAE Legal Agent - Quick Reference

**Fast access to common commands and workflows**

---

## 🎯 Most Used Commands

### Legal Query (Interactive)
```bash
cd C:\Deployment\uae-legal-agent
python scripts\legal_query.py
```

### Legal Query (Single)
```bash
python scripts\legal_query.py --query "Your legal question here"
```

### Test Search
```bash
python tests\test_search.py
```

### Check API Keys
```bash
python scripts\check_api_key.py
```

### Deploy/Reindex Documents
```bash
python scripts\deploy_openai_embeddings.py --force
```

---

## 📊 Current Status

```yaml
Documents: 3 UAE law PDFs
Chunks: 552 indexed
Store: data/simple_vector_store/uae_legal_docs.pkl
Size: ~5 MB
Status: ✅ OPERATIONAL
```

---

## 🔑 API Keys Location

**File:** `C:\Deployment\uae-legal-agent\.env`

```bash
CLAUDE_API_KEY=sk-ant-api03-...     # Must start with sk-ant-
OPENAI_API_KEY=sk-proj-...          # For embeddings
```

---

## 💰 Costs

```
Per Query: ~$0.015 USD
Monthly (100 queries): ~$1.50
Monthly (500 queries): ~$7.50
```

---

## 🎓 Example Queries

```
"What are the penalties for theft?"
"Money laundering laws in UAE"
"Criminal procedures for arrest"
"AML compliance requirements"
"What is the bail process?"
"Penalties for financial crimes"
```

---

## 🐛 Troubleshooting

### API Key Error
```bash
python scripts\check_api_key.py
# Check .env file for correct keys
```

### Search Returns Nothing
```bash
# Check store exists
dir data\simple_vector_store\

# Rebuild if needed
python scripts\deploy_openai_embeddings.py --force
```

### Slow Performance
```
Normal times:
- Load store: <1s
- Search: <50ms
- Claude analysis: 2-3s
- Total: <5s
```

---

## 📁 Important Files

```
scripts/legal_query.py          → Main CLI tool
utils/vector_store_simple.py    → Vector database
utils/claude_client.py          → Claude API
scripts/deploy_openai_embeddings.py → Deployment
.env                            → API keys (SECRET!)
```

---

## 🚀 Git Workflow

```bash
cd C:\Deployment\uae-legal-agent

# Check status
git status

# Pull latest
git pull

# After changes
git add .
git commit -m "Your message"
git push
```

---

## 📞 Resources

- **GitHub:** github.com/rauschiccsk/uae-legal-agent
- **Claude Console:** console.anthropic.com
- **OpenAI Console:** platform.openai.com

---

## ✅ Quick Health Check

```bash
# 1. API keys valid?
python scripts\check_api_key.py

# 2. Store loaded?
python tests\test_search.py

# 3. RAG working?
python scripts\legal_query.py --query "test"
```

All green = System healthy! ✅

---

**Version:** 1.0.0 | **Updated:** 2025-10-31