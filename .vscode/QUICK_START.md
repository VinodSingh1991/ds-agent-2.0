# Quick Start Guide - VS Code Debug & Tasks

## 🚀 Quick Actions

### Start Debugging (F5)
1. Press `F5` or click the "Run and Debug" icon (▶️) in the sidebar
2. Select **"Debug API Server"** from the dropdown
3. Server starts at http://localhost:8000
4. API docs available at http://localhost:8000/docs

### Run Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- **Start API Server** - Start server in watch mode
- **Test API** - Run API tests
- **Test Reindex** - Test the reindex endpoint
- **Generate Chunks** - Generate chunks from dataset
- **Build Vector Index** - Build FAISS index
- **Open API Docs** - Open browser to API documentation
- **Full Setup** - Install deps + generate chunks + build index

## 📋 Common Workflows

### Workflow 1: Start Debugging the API

```
1. Press F5
2. Select "Debug API Server"
3. Set breakpoints in api/api/main.py
4. Open http://localhost:8000/docs
5. Test endpoints - debugger will pause at breakpoints
```

### Workflow 2: Debug a Specific Endpoint

```
1. Open api/api/main.py
2. Find your endpoint (e.g., /generate or /reindex)
3. Click left of line number to set breakpoint (red dot appears)
4. Press F5 → "Debug API Server"
5. Make request to endpoint
6. Use F10 (step over), F11 (step into), F5 (continue)
```

### Workflow 3: Test Changes with Auto-reload

```
1. Press F5 → "Debug API Server" (has --reload)
2. Make code changes
3. Save file (Ctrl+S)
4. Server automatically restarts
5. Test changes immediately
```

### Workflow 4: Run Tests

```
Method 1 (Task):
- Ctrl+Shift+P → "Tasks: Run Task" → "Test API"

Method 2 (Debug):
- Open test_api.py
- Press F5 → "Debug Test Script"
```

### Workflow 5: Rebuild RAG Index

```
Method 1 (Task):
- Ctrl+Shift+P → "Tasks: Run Task" → "Build Vector Index"

Method 2 (Debug):
- Press F5 → "Debug Build Vector Index"

Method 3 (API):
- Start server (F5)
- POST to http://localhost:8000/reindex
```

## 🎯 Debug Configurations Cheat Sheet

| Configuration | Use Case | Auto-reload | Port |
|--------------|----------|-------------|------|
| **Debug API Server** | Main development | ✅ Yes | 8000 |
| **Debug API Server (No Reload)** | Stable debugging | ❌ No | 8000 |
| **Debug start_api.py** | Debug startup | ✅ Yes | 8000 |
| **Debug Test Script** | Test individual files | N/A | N/A |
| **Debug Build Vector Index** | Debug RAG building | N/A | N/A |
| **Debug Generate Chunks** | Debug chunk generation | N/A | N/A |

## ⌨️ Keyboard Shortcuts

### Debugging
- `F5` - Start debugging / Continue
- `F9` - Toggle breakpoint
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out
- `Shift+F5` - Stop debugging
- `Ctrl+Shift+F5` - Restart debugging

### Tasks
- `Ctrl+Shift+P` → "Tasks: Run Task" - Show all tasks
- `Ctrl+Shift+B` - Run default build task

### Navigation
- `Ctrl+P` - Quick file open
- `Ctrl+Shift+F` - Search in files
- `F12` - Go to definition
- `Alt+F12` - Peek definition

## 🔧 Troubleshooting

### Problem: Port 8000 already in use

**Solution:**
```
1. Ctrl+Shift+P → "Tasks: Run Task" → "Check Port 8000"
2. Note the PID
3. Kill process: taskkill /F /PID <PID>
```

### Problem: Breakpoints not hitting

**Solution:**
1. Check you're using "Debug API Server" (not just running)
2. Verify breakpoint is in executed code path
3. Try "Debug API Server (No Reload)" for more stable breakpoints

### Problem: Module not found errors

**Solution:**
```
Ctrl+Shift+P → "Tasks: Run Task" → "Install Dependencies"
```

### Problem: Vector index not found

**Solution:**
```
Ctrl+Shift+P → "Tasks: Run Task" → "Full Setup"
```

## 📁 File Structure

```
.vscode/
├── launch.json          # Debug configurations
├── tasks.json           # Task definitions
├── settings.json        # Python settings
├── DEBUG_GUIDE.md       # Detailed debug guide
└── QUICK_START.md       # This file
```

## 🎓 Learning Path

### Beginner
1. Start with "Debug API Server" (F5)
2. Set simple breakpoints
3. Use F10 to step through code
4. Inspect variables in left panel

### Intermediate
1. Use conditional breakpoints
2. Add watch expressions
3. Use debug console to execute code
4. Try "Debug Test Script" for testing

### Advanced
1. Debug multi-stage processes (RAG building)
2. Use logpoints instead of print statements
3. Debug with exception breakpoints
4. Create custom tasks for your workflow

## 💡 Pro Tips

1. **Use the integrated terminal**: All tasks run in VS Code terminal
2. **Combine debugging + tasks**: Start server with task, debug with F5
3. **Watch expressions**: Add `request.query`, `result['layout']` to watch panel
4. **Debug console**: Execute Python while paused: `>>> len(chunks)`
5. **Logpoints**: Right-click line → "Add Logpoint" for non-intrusive logging

## 🔗 Quick Links

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Detailed Debug Guide: [DEBUG_GUIDE.md](DEBUG_GUIDE.md)
- Reindex Endpoint Docs: [../api/REINDEX_ENDPOINT.md](../api/REINDEX_ENDPOINT.md)

## 📞 Need Help?

1. Check [DEBUG_GUIDE.md](DEBUG_GUIDE.md) for detailed instructions
2. Review [../api/REINDEX_ENDPOINT.md](../api/REINDEX_ENDPOINT.md) for API docs
3. Check server logs in integrated terminal
4. Use debug console to inspect state

---

**Happy Debugging! 🐛🔨**

