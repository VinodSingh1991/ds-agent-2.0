# Disposable UI Agent

> **Generate structured UI layouts from natural language queries using LLMs and RAG**

A FastAPI-based system that automatically generates complete, structured UI layouts from natural language queries. Powered by OpenAI GPT-4 and FAISS vector search.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd api
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

**Don't have an API key?** See [OPENAI_API_KEY_SETUP.md](OPENAI_API_KEY_SETUP.md)

### 3. Build RAG Index
```bash
python generate_chunks.py
python build_vector_index.py
```

### 4. Start Server
```bash
python start_api.py --reload
```

### 5. Test It!
Open http://localhost:8000/docs

## 💡 What It Does

**Input:** Natural language query + your data
```json
{
  "query": "show me all leads",
  "data": [
    {"id": 1, "name": "Acme Corp", "revenue": 75000}
  ]
}
```

**Output:** Complete, structured UI layout
```json
{
  "layout_type": "list",
  "sections": [...],
  "data": [...],
  "metadata": {...}
}
```

## 🎯 Key Features

- ✅ **Natural Language Queries** - "show me all leads", "display contacts"
- ✅ **RAG-Powered** - Retrieves similar patterns from vector store
- ✅ **Structured Outputs** - Type-safe JSON layouts
- ✅ **Multiple Layout Types** - List, detail, dashboard, table, grid, form, timeline
- ✅ **CRM Objects** - Leads, contacts, deals, cases, accounts
- ✅ **Batch Generation** - Generate multiple layouts at once
- ✅ **Reindex Endpoint** - Rebuild RAG index on-demand
- ✅ **Auto-reload** - Hot reload during development

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[OPENAI_API_KEY_SETUP.md](OPENAI_API_KEY_SETUP.md)** - How to configure your API key
- **[api/API_USAGE.txt](api/API_USAGE.txt)** - API usage examples
- **[api/REINDEX_ENDPOINT.md](api/REINDEX_ENDPOINT.md)** - Reindex endpoint documentation
- **[.vscode/QUICK_START.md](.vscode/QUICK_START.md)** - VS Code debugging guide

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Generate UI layout from query |
| `/generate-batch` | POST | Generate multiple layouts |
| `/reindex` | POST | Rebuild RAG vector index |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

## 🏗️ Architecture

```
User Query → Query Analyzer → Candidate Retriever (RAG) → Layout Generator → UI Layout
                                        ↓
                                  FAISS Vector Store
```

**Components:**
- **QueryAnalyzer** - Extracts intent, object type, filters
- **CandidateRetriever** - RAG-based retrieval of similar patterns
- **LayoutGenerator** - Generates final layout using GPT-4
- **EnhancedVectorStore** - FAISS-based semantic search

## 🎓 Examples

### Generate a Layout
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me all leads",
    "data": [
      {"id": 1, "name": "Acme Corp", "revenue": 75000}
    ]
  }'
```

### Batch Generation
```bash
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "show me all leads",
      "display contacts",
      "sales dashboard"
    ]
  }'
```

### Rebuild RAG Index
```bash
curl -X POST http://localhost:8000/reindex \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

## 🐛 Debugging with VS Code

1. Press `F5`
2. Select "Debug API Server"
3. Set breakpoints
4. Test endpoints

See [.vscode/QUICK_START.md](.vscode/QUICK_START.md) for details.

## 🧪 Testing

```bash
cd api
python test_api.py        # Test all endpoints
python test_reindex.py    # Test reindex endpoint
```

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **OpenAI GPT-4** - LLM with structured outputs
- **FAISS** - Vector similarity search
- **Sentence Transformers** - Text embeddings
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## 📁 Project Structure

```
disposable-ui-agent/
├── api/
│   ├── agent/              # Agent components
│   │   ├── query_analyzer.py
│   │   ├── candidate_retriever.py
│   │   └── layout_generator.py
│   ├── api/                # FastAPI app
│   │   └── main.py
│   ├── core/               # Core utilities
│   │   └── enhanced_vector_store.py
│   ├── dataset/            # Training data
│   └── vector_index/       # FAISS index
├── .vscode/                # VS Code config
├── .env.example            # Environment template
└── README.md               # This file
```

## ⚠️ Important Notes

1. **API Key Required** - You must set `OPENAI_API_KEY` to use this system
2. **Data Not Fetched** - The agent only generates layouts; you provide the data
3. **RAG Index Required** - Run `build_vector_index.py` before starting
4. **Costs** - Each request costs ~$0.01-0.06 in OpenAI API fees

## 🔒 Security

- ✅ `.env` file in `.gitignore`
- ✅ Never commit API keys
- ✅ Use environment variables
- ✅ CORS configured (update for production)

## 🚧 Troubleshooting

### "OpenAI API key required"
See [OPENAI_API_KEY_SETUP.md](OPENAI_API_KEY_SETUP.md)

### "Vector index not found"
```bash
cd api
python generate_chunks.py
python build_vector_index.py
```

### "Port 8000 already in use"
```bash
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more troubleshooting.

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please read the setup guide first.

---

**Ready to start?** Follow the [SETUP_GUIDE.md](SETUP_GUIDE.md) or [OPENAI_API_KEY_SETUP.md](OPENAI_API_KEY_SETUP.md)

