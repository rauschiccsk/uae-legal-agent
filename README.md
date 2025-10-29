# UAE Legal Agent

AI-powered legal research assistant for UAE legislation using Claude and RAG.

## Features

- 🤖 AI-powered legal research using Claude API
- 📚 RAG (Retrieval-Augmented Generation) for accurate legal citations
- 📄 PDF document processing and indexing
- 🔍 Semantic search across UAE legal documents
- ⚙️ Configurable settings via environment variables

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

## Configuration

The application uses environment variables for configuration. See `.env.example` for available options:

- `ANTHROPIC_API_KEY` - Your Anthropic API key (required)
- `CLAUDE_MODEL` - Claude model to use (default: claude-3-5-sonnet-20241022)
- `DEBUG` - Enable debug mode (default: false)
- `DATA_DIR` - Directory for legal documents (default: ./data)
- `VECTOR_STORE_PATH` - Path for vector store (default: ./vector_store)

## Usage

Run the agent:
```bash
python main.py
```

The agent will:
1. Process legal documents from the `data/` directory
2. Build a vector store for semantic search
3. Start an interactive session for legal questions

## Project Structure

```
uae-legal-agent/
├── agents/          # AI agent implementations
├── data/            # Legal documents (PDF)
├── tests/           # Test suite
├── utils/           # Utility modules
│   └── config.py    # Configuration management
├── vector_store/    # Vector embeddings storage
├── main.py          # Application entry point
├── requirements.txt # Python dependencies
└── .env            # Environment configuration
```

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Requirements

- Python 3.9+
- Anthropic API key
- UAE legal documents in PDF format

## Development

### Config Module

The config module uses Pydantic V2 for validation and settings management. Key features:

- ✅ Environment variable loading with `.env` file support
- ✅ Type validation and coercion
- ✅ Path normalization and validation
- ✅ Debug mode support
- ✅ Comprehensive test coverage

### Git Workflow

Current branch: main
Working tree clean

For development:
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit with conventional commits: `git commit -m "feat: add feature"`
4. Push and create PR

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.