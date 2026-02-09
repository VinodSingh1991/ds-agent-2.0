# Setup Guide - Disposable UI Agent

This guide will help you set up and configure the Disposable UI Agent API.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git (optional)

## Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### Step 2: Configure OpenAI API Key

**Option A: Using .env file (Recommended)**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

**Option B: Using Environment Variables**

Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
```

Windows (CMD):
```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

Linux/Mac:
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

### Step 3: Generate Chunks and Build Index

```bash
# Generate chunks from dataset
python generate_chunks.py

# Build FAISS vector index
python build_vector_index.py
```

### Step 4: Start the API Server

```bash
python start_api.py --reload
```

The server will start at http://localhost:8000

### Step 5: Test the API

Open your browser to http://localhost:8000/docs to see the interactive API documentation.

Or run the test script:
```bash
python test_api.py
```

## Detailed Setup

### 1. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Required
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional
OPENAI_MODEL=gpt-4o-2024-08-06
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000
```

### 2. Verify Installation

Check that all dependencies are installed:

```bash
python -c "import fastapi, openai, faiss, sentence_transformers; print('✅ All dependencies installed')"
```

### 3. Build RAG Index

The RAG (Retrieval-Augmented Generation) index is required for the agent to work:

```bash
# Step 1: Generate chunks
cd api
python generate_chunks.py

# Expected output:
# ✅ Generated 150+ chunks
# ✅ Saved to dataset/enhanced_chunks.json

# Step 2: Build vector index
python build_vector_index.py

# Expected output:
# ✅ Index built successfully!
# ✅ Saved to vector_index/enhanced_layouts.faiss
```

### 4. Start the Server

**Development mode (with auto-reload):**
```bash
python start_api.py --reload
```

**Production mode:**
```bash
python start_api.py
```

**Custom port:**
```bash
python start_api.py --port 8080
```

### 5. Verify Server is Running

**Method 1: Health Check**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "version": "1.0.0"
}
```

**Method 2: Browser**
Open http://localhost:8000/docs

## VS Code Setup (Recommended)

### Debug Configuration

The project includes VS Code debug configurations. To use them:

1. Open the project in VS Code
2. Press `F5`
3. Select "Debug API Server"
4. Server starts in debug mode with breakpoints enabled

See [.vscode/QUICK_START.md](.vscode/QUICK_START.md) for more details.

### Tasks

Run common tasks with `Ctrl+Shift+P` → "Tasks: Run Task":

- **Start API Server** - Launch server
- **Test API** - Run tests
- **Build Vector Index** - Rebuild RAG index
- **Full Setup** - Complete setup from scratch

## Testing

### Test the API

```bash
cd api
python test_api.py
```

### Test Individual Endpoints

**Generate Layout:**
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

**Reindex RAG:**
```bash
curl -X POST http://localhost:8000/reindex \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

## Troubleshooting

### Error: "OpenAI API key required"

**Solution:**
1. Check that `.env` file exists in project root
2. Verify `OPENAI_API_KEY` is set correctly
3. Restart the server after setting the key

### Error: "Vector index not found"

**Solution:**
```bash
cd api
python generate_chunks.py
python build_vector_index.py
```

### Error: "Port 8000 already in use"

**Solution:**

Windows:
```powershell
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

Linux/Mac:
```bash
lsof -i :8000
kill -9 <PID>
```

Or use a different port:
```bash
python start_api.py --port 8080
```

### Error: "Module not found"

**Solution:**
```bash
cd api
pip install -r requirements.txt
```

## Next Steps

1. **Read the API documentation**: http://localhost:8000/docs
2. **Try the examples**: See `api/example_usage.py`
3. **Debug with VS Code**: Press F5 to start debugging
4. **Customize**: Modify `api/dataset/` files to add your own patterns

## Additional Resources

- **API Usage Guide**: [api/API_USAGE.txt](api/API_USAGE.txt)
- **Testing Guide**: [api/TESTING_GUIDE.txt](api/TESTING_GUIDE.txt)
- **Reindex Endpoint**: [api/REINDEX_ENDPOINT.md](api/REINDEX_ENDPOINT.md)
- **Debug Guide**: [.vscode/DEBUG_GUIDE.md](.vscode/DEBUG_GUIDE.md)
- **Quick Start**: [.vscode/QUICK_START.md](.vscode/QUICK_START.md)

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file

**Important:** Never commit your `.env` file to version control!

## Support

If you encounter issues:

1. Check the logs in `api/logs/api.log`
2. Review the troubleshooting section above
3. Ensure all prerequisites are met
4. Verify your OpenAI API key is valid

