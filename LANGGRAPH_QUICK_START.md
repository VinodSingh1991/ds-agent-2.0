# LangGraph UI Agent - Quick Start Guide

## 🚀 Getting Started

### 1. Import the Agent

```python
from agent.langgraph_ui_agent import LangGraphUIAgent
```

### 2. Initialize

```python
# Option 1: Use environment variable
agent = LangGraphUIAgent()

# Option 2: Pass API key directly
agent = LangGraphUIAgent(api_key="your-openai-key")

# Option 3: Custom model
agent = LangGraphUIAgent(model="gpt-4o-2024-08-06")
```

### 3. Generate Layout

```python
# Prepare your data
leads_data = [
    {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
    {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"}
]

# Generate layout
layout = agent.generate(
    query="show me all leads",
    data=leads_data
)

# Use the layout
print(layout["layout_type"])
print(layout["sections"])
print(layout["data"])
```

---

## 📊 Complete Example

```python
from agent.langgraph_ui_agent import LangGraphUIAgent

# Initialize agent
agent = LangGraphUIAgent()

# Your data (from database, API, etc.)
data = [
    {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
    {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"},
    {"id": 3, "name": "Global Inc", "revenue": 50000, "status": "new"}
]

# Generate layout
layout = agent.generate(
    query="show me top leads by revenue",
    data=data,
    context={"user_id": "123", "preferences": {"theme": "dark"}}
)

# Result structure
{
    "layout_type": "list",
    "sections": [
        {
            "title": "Leads",
            "rows": [
                {
                    "components": [
                        {
                            "type": "ListCard",
                            "props": {...},
                            "binds_to": "name"
                        }
                    ]
                }
            ]
        }
    ],
    "data": [...],
    "metadata": {...}
}
```

---

## 🔄 Migration from Original Agent

### Before (StructuredUIAgent)
```python
from agent.structured_ui_agent_v2 import StructuredUIAgent

agent = StructuredUIAgent()
layout = agent.generate(query="...", data=[...])
```

### After (LangGraphUIAgent)
```python
from agent.langgraph_ui_agent import LangGraphUIAgent

agent = LangGraphUIAgent()
layout = agent.generate(query="...", data=[...])
```

**✅ Same interface! Just change the import!**

---

## 🎯 Key Features

### 1. Same Components
- ✅ QueryAnalyzer - Analyzes queries
- ✅ CandidateRetriever - Retrieves patterns from vector store
- ✅ LayoutGenerator - Generates final layout

### 2. Same Logic
- ✅ 3-step pipeline
- ✅ Same data flow
- ✅ Same output format

### 3. Graph-Based Orchestration
- ✅ Explicit workflow definition
- ✅ Better state management
- ✅ Easier to extend

---

## 📈 Agent Statistics

```python
stats = agent.get_stats()

print(stats)
# {
#     "model": "gpt-4o-2024-08-06",
#     "orchestration": "LangGraph",
#     "components": {
#         "query_analyzer": "QueryAnalyzer",
#         "candidate_retriever": "CandidateRetriever",
#         "layout_generator": "LayoutGenerator"
#     },
#     "graph_nodes": ["analyze_query", "retrieve_candidates", "generate_layout"],
#     "data_handling": "external",
#     "vector_store": {...},
#     "status": "ready"
# }
```

---

## 🧪 Testing

### Run Comparison Test
```bash
cd api
python test_langgraph_agent.py
```

### Expected Output
```
✅ Original Agent Success!
✅ LangGraph Agent Success!
✅ Layout types match
✅ Section counts match
✅ Data records match
```

---

## 🔧 Troubleshooting

### Error: "OpenAI API key required"
```bash
# Set environment variable
export OPENAI_API_KEY="your-key"  # Linux/Mac
$env:OPENAI_API_KEY="your-key"    # Windows PowerShell
```

### Error: "Vector store not loaded"
```bash
# Build vector index first
cd api
python build_vector_index.py
```

### Error: "LangGraph not installed"
```bash
pip install langgraph
```

---

## 📚 Next Steps

1. ✅ Use LangGraphUIAgent in your application
2. ✅ Test with your own queries and data
3. ✅ Explore graph visualization (LangGraph Studio)
4. ✅ Add custom nodes for your use case
5. ✅ Add conditional routing for optimization

---

## 💡 Benefits

### Why LangGraph?

1. **Better Workflow Management**
   - Explicit graph structure
   - Easy to visualize
   - Easy to debug

2. **Easier to Extend**
   - Add new nodes
   - Add conditional edges
   - Add parallel processing

3. **Production Ready**
   - Built-in state management
   - Error handling
   - Retry logic support

4. **Same Performance**
   - Uses same components
   - Same logic
   - Same results

---

**Status**: ✅ Ready to use! Same logic, graph-based orchestration! 🎉

