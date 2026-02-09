# VS Code Debug Configuration Guide

This guide explains how to use the debug configurations for the Disposable UI Agent project.

## Available Debug Configurations

### 1. **Debug API Server** (Recommended)
- **What it does**: Starts the FastAPI server with auto-reload enabled
- **Use when**: You want to debug the API endpoints with hot reload
- **Port**: 8000
- **Auto-reload**: ✅ Yes
- **Breakpoints**: Works in all API code

**How to use:**
1. Press `F5` or click "Run and Debug" in VS Code
2. Select "Debug API Server" from the dropdown
3. Set breakpoints in `api/api/main.py` or other files
4. Make API requests to trigger breakpoints

### 2. **Debug API Server (No Reload)**
- **What it does**: Starts the FastAPI server without auto-reload
- **Use when**: Auto-reload interferes with debugging or you want stable breakpoints
- **Port**: 8000
- **Auto-reload**: ❌ No
- **Breakpoints**: More stable, won't reset on file changes

**How to use:**
1. Select "Debug API Server (No Reload)" from debug dropdown
2. Press `F5`
3. Server won't restart on file changes

### 3. **Debug start_api.py**
- **What it does**: Debugs the `start_api.py` script directly
- **Use when**: You want to debug the server startup process
- **Auto-reload**: ✅ Yes
- **Breakpoints**: Works in startup code

### 4. **Debug Test Script**
- **What it does**: Debugs the currently open Python file
- **Use when**: Testing individual scripts like `test_api.py`, `test_reindex.py`
- **Breakpoints**: Works in the current file

**How to use:**
1. Open a test file (e.g., `test_api.py`)
2. Select "Debug Test Script"
3. Press `F5`

### 5. **Debug Build Vector Index**
- **What it does**: Debugs the vector index building process
- **Use when**: Debugging RAG index creation issues
- **File**: `build_vector_index.py`

### 6. **Debug Generate Chunks**
- **What it does**: Debugs the chunk generation process
- **Use when**: Debugging chunk creation from dataset
- **File**: `generate_chunks.py`

## Quick Start

### Debugging API Endpoints

1. **Set a breakpoint** in `api/api/main.py`:
   ```python
   @app.post("/generate", response_model=GenerateResponse)
   async def generate_layout(request: GenerateRequest):
       logger.info(f"Generating layout for query: {request.query}")  # ← Click here to set breakpoint
   ```

2. **Start debugging**:
   - Press `F5`
   - Select "Debug API Server"

3. **Make a request**:
   - Open http://localhost:8000/docs
   - Try the `/generate` endpoint
   - Debugger will pause at your breakpoint

4. **Debug controls**:
   - `F10` - Step over
   - `F11` - Step into
   - `Shift+F11` - Step out
   - `F5` - Continue

### Debugging the Reindex Endpoint

1. Set breakpoint in the `/reindex` endpoint:
   ```python
   @app.post("/reindex", response_model=ReindexResponse)
   async def reindex_rag(request: ReindexRequest):
       logger.info(f"Reindexing RAG...")  # ← Breakpoint here
   ```

2. Start "Debug API Server"

3. Make a POST request to `/reindex`:
   ```bash
   curl -X POST http://localhost:8000/reindex \
     -H "Content-Type: application/json" \
     -d '{"force": false}'
   ```

### Debugging Test Scripts

1. Open `test_reindex.py`

2. Set breakpoint:
   ```python
   def test_reindex():
       print("Testing /reindex Endpoint")  # ← Breakpoint here
   ```

3. Select "Debug Test Script" and press `F5`

## Debug Features

### Variables Panel
- View all local and global variables
- Inspect request/response objects
- Check agent state

### Watch Expressions
Add expressions to watch:
- `request.query`
- `result['layout']`
- `vector_store.chunks`

### Debug Console
Execute Python code while paused:
```python
>>> request.query
'show me all leads'
>>> len(request.data)
2
```

### Call Stack
- See the full execution path
- Navigate between stack frames
- Inspect variables at each level

## Common Debugging Scenarios

### 1. API Request Not Working

**Breakpoint locations:**
- `api/api/main.py` - Endpoint function
- `agent/structured_ui_agent_v2.py` - Agent generate method
- `agent/layout_generator.py` - Layout generation logic

### 2. RAG Not Returning Results

**Breakpoint locations:**
- `agent/candidate_retriever.py` - Retrieval logic
- `core/enhanced_vector_store.py` - Search method

### 3. Layout Generation Issues

**Breakpoint locations:**
- `agent/layout_generator.py` - Generation logic
- `agent/query_analyzer.py` - Query analysis

## Tips

### 1. Use Conditional Breakpoints
Right-click on a breakpoint → "Edit Breakpoint" → Add condition:
```python
request.query == "show me all leads"
```

### 2. Log Points
Instead of `print()`, use log points:
- Right-click line → "Add Logpoint"
- Enter: `Query: {request.query}`

### 3. Exception Breakpoints
- Open "Breakpoints" panel
- Check "Raised Exceptions" to pause on any error

### 4. Debugging with Auto-reload
- Use "Debug API Server" for most cases
- If breakpoints keep resetting, use "Debug API Server (No Reload)"

## Troubleshooting

### Breakpoints Not Hitting

**Solution 1**: Check `justMyCode` setting
- In `launch.json`, ensure `"justMyCode": false`

**Solution 2**: Verify working directory
- Should be `${workspaceFolder}/api`

**Solution 3**: Check PYTHONPATH
- Should include `${workspaceFolder}/api`

### Port Already in Use

**Solution**: Kill existing server
```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Auto-reload Not Working

**Solution**: Use "Debug API Server" configuration
- Includes `--reload` flag
- Watches for file changes

## Environment Variables

Create a `.env` file in the workspace root:
```env
OPENAI_API_KEY=your_key_here
LOG_LEVEL=DEBUG
```

The debugger will automatically load these variables.

## Additional Resources

- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [FastAPI Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

