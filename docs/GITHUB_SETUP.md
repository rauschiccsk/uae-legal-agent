# GitHub Repository Setup Guide

**UAE Legal Agent - Step-by-Step GitHub Setup**

---

## 🎯 Quick Setup Overview

```
1. Create documentation files (SYSTEM_PROMPT, MASTER_CONTEXT)
2. Initialize Git repository
3. Create GitHub repository
4. Connect local → remote
5. Push to GitHub
6. Verify URLs
```

**Estimated Time:** 10-15 minutes

---

## 📝 Step 1: Create Documentation Files

### 1.1 Create SYSTEM_PROMPT.md

```powershell
# V uae-legal-agent priečinku
notepad docs\SYSTEM_PROMPT.md
```

**Action:** Skopíruj celý obsah z Artifactu "SYSTEM_PROMPT.md" a ulož.

**Verify:**
```powershell
dir docs\SYSTEM_PROMPT.md
# Should show file exists
```

### 1.2 Create MASTER_CONTEXT.md

```powershell
notepad docs\MASTER_CONTEXT.md
```

**Action:** Skopíruj celý obsah z Artifactu "MASTER_CONTEXT.md" a ulož.

**Verify:**
```powershell
dir docs\MASTER_CONTEXT.md
# Should show file exists
```

### 1.3 Verify All Documentation

```powershell
dir docs\*.md
```

**Expected Output:**
```
INIT_CONTEXT.md         ✅
SYSTEM_PROMPT.md        ✅
MASTER_CONTEXT.md       ✅
GITHUB_SETUP.md         ✅
```

---

## 🔒 Step 2: Security Check

### 2.1 Verify .gitignore

```powershell
cat .gitignore
```

**Must include:**
```
# Environment variables
.env
.env.local
*.env

# API keys
*api_key*
*API_KEY*
```

### 2.2 Check .env is NOT in Git

```powershell
# This should show error (file not tracked)
git status .env
```

**Expected:** File should NOT be listed for commit

---

## 🔧 Step 3: Initialize Git

### 3.1 Initialize Repository

```powershell
# Make sure you're in project root
cd c:\Development\uae-legal-agent

# Initialize Git
git init
```

**Expected Output:**
```
Initialized empty Git repository in c:/Development/uae-legal-agent/.git/
```

### 3.2 Configure Git (if needed)

```powershell
# Set your Git username (if not set globally)
git config user.name "Zoltán Rauscher"
git config user.email "rausch@icc.sk"
```

### 3.3 Add All Files

```powershell
git add .
```

### 3.4 Verify Staging

```powershell
git status
```

**Critical Check:**
- ✅ `.env` should NOT be in the list
- ✅ All `.md` files should be staged
- ✅ All `.py` files should be staged
- ✅ `requirements*.txt` should be staged

**If .env appears:** STOP! Fix .gitignore first!

### 3.5 Create First Commit

```powershell
git commit -m "Initial commit: UAE Legal Agent setup with Claude API integration

- Complete project structure with docs/, src/, tests/, data/
- Claude API client implementation with legal system prompt
- Token tracking and cost calculation
- Comprehensive documentation (INIT_CONTEXT, SYSTEM_PROMPT, MASTER_CONTEXT)
- Session notes and GitHub setup guide
- Working API test (109 tokens, $0.001155 cost)
- Requirements for minimal and ultra-minimal setups"
```

**Expected Output:**
```
[main (root-commit) abc1234] Initial commit: ...
 XX files changed, XXXX insertions(+)
 create mode 100644 ...
```

---

## 🌐 Step 4: Create GitHub Repository

### 4.1 Go to GitHub

Open browser: https://github.com/new

### 4.2 Repository Settings

**Fill in:**
- **Repository name:** `uae-legal-agent`
- **Description:** `AI-powered legal analysis system for UAE law using Claude API`
- **Visibility:** 
  - ✅ **Private** (odporúčané pre legal cases)
  - ⚪ Public (ak chceš open-source)

**IMPORTANT - Do NOT initialize:**
- ❌ **DO NOT** add README.md (máš už vlastný)
- ❌ **DO NOT** add .gitignore (máš už vlastný)
- ❌ **DO NOT** add license (pridáš neskôr ak chceš)

### 4.3 Create Repository

Click **"Create repository"** button.

**GitHub will show you quick setup commands** - ignoruj ich, máme vlastné.

---

## 🔗 Step 5: Connect Local to Remote

### 5.1 Add Remote Origin

```powershell
# Replace 'rauschiccsk' with your GitHub username if different
git remote add origin https://github.com/rauschiccsk/uae-legal-agent.git
```

### 5.2 Verify Remote

```powershell
git remote -v
```

**Expected Output:**
```
origin  https://github.com/rauschiccsk/uae-legal-agent.git (fetch)
origin  https://github.com/rauschiccsk/uae-legal-agent.git (push)
```

### 5.3 Rename Branch to 'main'

```powershell
git branch -M main
```

---

## 🚀 Step 6: Push to GitHub

### 6.1 Push Initial Commit

```powershell
git push -u origin main
```

**Expected Output:**
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to X threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), XX.XX KiB | XX.XX MiB/s, done.
Total XX (delta X), reused X (delta X), pack-reused X
To https://github.com/rauschiccsk/uae-legal-agent.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

**If prompted for credentials:**
- Username: your GitHub username
- Password: **GitHub Personal Access Token** (not your password!)
  - Create token at: https://github.com/settings/tokens
  - Scopes needed: `repo` (full control)

---

## ✅ Step 7: Verify Upload

### 7.1 Check GitHub Repository

Open: https://github.com/rauschiccsk/uae-legal-agent

**You should see:**
- ✅ All files uploaded
- ✅ README.md displayed on homepage
- ✅ docs/ directory visible
- ✅ src/ directory visible
- ✅ Last commit message visible

### 7.2 Test Raw URLs

Open these URLs in browser (replace `rauschiccsk` with your username):

#### Documentation URLs:
```
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/SYSTEM_PROMPT.md
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/MASTER_CONTEXT.md
```

**Expected:** Each URL should display the file content (not 404)

#### Source Code URLs:
```
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/src/core/claude_client.py
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/src/core/config.py
```

**Expected:** Python source code displayed

#### Session Notes:
```
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/sessions/2025-10-25_session.md
```

**Expected:** Session notes displayed

---

## 🎨 Step 8: Customize Repository (Optional)

### 8.1 Add Topics

Go to: https://github.com/rauschiccsk/uae-legal-agent

Click **"⚙️ Settings"** → **"General"** → **"Topics"**

**Add topics:**
```
ai
legal-tech
claude-api
uae
python
natural-language-processing
legal-analysis
anthropic
fastapi
```

### 8.2 Update Description

Click **"About ⚙️"** → Edit

**Description:**
```
AI-powered legal analysis system for UAE law using Claude Sonnet 4.5 API. 
Generates alternative legal strategies, risk assessments, and cost estimates 
with precise Federal Law citations.
```

**Website:** (leave empty for now)

### 8.3 Add Repository Details

- [ ] Include in the home page: ✅ Yes
- [ ] Include Wiki: ❌ No (using docs/)
- [ ] Include Projects: ❌ No
- [ ] Include Discussions: ❌ No

---

## 📋 Step 9: Post-Setup Checklist

### Critical Checks:
- [ ] ✅ Repository created successfully
- [ ] ✅ All files pushed (verify on GitHub)
- [ ] ✅ .env file NOT in repository
- [ ] ✅ INIT_CONTEXT.md URL works
- [ ] ✅ project_file_access.json URL works
- [ ] ✅ SYSTEM_PROMPT.md URL works
- [ ] ✅ MASTER_CONTEXT.md URL works
- [ ] ✅ Session notes URL works
- [ ] ✅ README.md displays correctly
- [ ] ✅ Source code files visible

### Optional Enhancements:
- [ ] Topics added
- [ ] Description updated
- [ ] Repository settings configured
- [ ] Branch protection rules (for team projects)

---

## 🔄 Step 10: Test Context Loading

### 10.1 Open New Claude Chat

Start a new conversation at: https://claude.ai

### 10.2 Load Project Context

Paste these two URLs:
```
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/INIT_CONTEXT.md
https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main/docs/project_file_access.json
```

### 10.3 Expected Response

Claude should respond:
```
✅ UAE Legal Agent načítaný. Čo robíme?
```

**If successful:** Context loading works perfectly! ✨

---

## 🚨 Troubleshooting

### Problem 1: .env File Appears in Git

**Symptom:** `git status` shows .env  
**Solution:**
```powershell
# Remove from staging
git reset .env

# Add to .gitignore if not there
echo ".env" >> .gitignore

# Commit .gitignore
git add .gitignore
git commit -m "docs: Ensure .env is gitignored"
git push
```

### Problem 2: 404 on Raw URLs

**Symptom:** Raw URLs return 404 Not Found  
**Cause:** File not pushed or wrong path  
**Solution:**
```powershell
# Verify files exist locally
dir docs\INIT_CONTEXT.md

# Check Git status
git status

# If files not committed
git add docs/
git commit -m "docs: Add missing documentation"
git push
```

### Problem 3: Push Rejected

**Symptom:** `error: failed to push some refs`  
**Cause:** Remote has changes you don't have locally  
**Solution:**
```powershell
# Pull first
git pull origin main --rebase

# Then push
git push origin main
```

### Problem 4: Authentication Failed

**Symptom:** Username/password authentication failed  
**Cause:** GitHub requires Personal Access Token  
**Solution:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Copy token
5. Use token as password when pushing

**Better Solution - Store Credentials:**
```powershell
git config --global credential.helper wincred
```

### Problem 5: Large Files Warning

**Symptom:** Warning about large files  
**Cause:** Accidentally added large data files  
**Solution:**
```powershell
# Add to .gitignore
echo "data/large_file.pdf" >> .gitignore

# Remove from Git (keep local)
git rm --cached data/large_file.pdf

# Commit
git commit -m "chore: Remove large file from Git"
git push
```

---

## 📚 Useful Git Commands

### Daily Workflow:
```powershell
# Pull latest changes
git pull

# Check status
git status

# Add specific file
git add path/to/file.py

# Add all changes
git add .

# Commit
git commit -m "type: message"

# Push
git push
```

### Branch Management:
```powershell
# Create new branch
git checkout -b feature/new-feature

# Switch branch
git checkout main

# List branches
git branch -a
```

### Viewing History:
```powershell
# View commit log
git log --oneline

# View changes
git diff

# View specific file history
git log -- path/to/file.py
```

---

## 🎓 Best Practices

### Commit Messages:
```
✅ Good:
feat: Add RAG pipeline for UAE law search
fix: Resolve token calculation bug in claude_client
docs: Update INIT_CONTEXT with Phase 1 status
test: Add integration test for legal analysis

❌ Bad:
changed stuff
update
fix
wip
```

### Commit Frequency:
- ✅ Commit after completing a feature
- ✅ Commit after fixing a bug
- ✅ Commit before switching tasks
- ❌ Don't commit broken code
- ❌ Don't commit secrets/keys

### Branch Strategy (for team):
```
main         ← Production-ready code
  ├─ develop ← Integration branch
       ├─ feature/legal-analysis
       ├─ feature/rag-pipeline
       └─ bugfix/token-calculation
```

---

## 🔗 Important URLs

### Your Repository:
```
GitHub: https://github.com/rauschiccsk/uae-legal-agent
Clone:  git@github.com:rauschiccsk/uae-legal-agent.git
Web:    https://rauschiccsk.github.io/uae-legal-agent (if Pages enabled)
```

### Documentation:
```
INIT_CONTEXT:     /main/docs/INIT_CONTEXT.md
SYSTEM_PROMPT:    /main/docs/SYSTEM_PROMPT.md
MASTER_CONTEXT:   /main/docs/MASTER_CONTEXT.md
FILE_ACCESS:      /main/docs/project_file_access.json
SESSION_NOTES:    /main/docs/sessions/2025-10-25_session.md
```

### Source Code:
```
Claude Client:    /main/src/core/claude_client.py
Config:           /main/src/core/config.py
Main API:         /main/src/api/main.py
```

---

## ✅ Success Criteria

Your GitHub setup is complete when:

- [x] GitHub repository created
- [x] All files pushed successfully
- [x] .env file NOT in repository
- [x] INIT_CONTEXT.md loads in browser
- [x] project_file_access.json contains valid URLs
- [x] SYSTEM_PROMPT.md loads correctly
- [x] MASTER_CONTEXT.md loads correctly
- [x] Session notes accessible
- [x] Claude can load project context via two URLs
- [x] No sensitive data exposed (API keys, client info)
- [x] README.md displays nicely on GitHub homepage

---

## 🎉 Congratulations!

Your UAE Legal Agent project is now on GitHub! 🚀

**Next Steps:**
1. ✅ Share raw URLs with your team
2. ✅ Start Phase 1 development (Legal Analysis Prototype)
3. ✅ Continue documenting progress in session notes
4. ✅ Update INIT_CONTEXT.md as project evolves

---

**Setup Guide Version:** 1.0.0  
**Last Updated:** 2025-10-25  
**Author:** Zoltán Rauscher (ICC Komárno)

🏛️ **Happy Coding!** ⚖️