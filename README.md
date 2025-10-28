# UAE Legal Agent

AI-powered legal research assistant for UAE legislation using Claude and RAG.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd uae-legal-agent
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

5. Place UAE legal documents (PDF) in the `data/` directory

6. Run the agent:
```bash
python main.py
```

## Usage

The agent will process legal documents and answer questions about UAE legislation.

## Requirements

- Python 3.9+
- Anthropic API key
- UAE legal documents in PDF format