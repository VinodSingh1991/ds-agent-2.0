# 📖 Schema Quick Reference Guide

## 🎯 Three Core Schema Types

### 1. Query Schemas (`query_schemas.py`)
**What:** Understand user queries  
**When:** First step - analyze what user wants  
**Output:** Structured query information

```python
QueryAnalysis(
    object_type="lead",           # What object
    intent="view_list",           # What action
    layout_type="list",           # Best layout
    filters=[...],                # Filter conditions
    sort="revenue DESC",          # Sorting
    limit=10                      # Record limit
)
```

---

### 2. Pattern Schemas (`pattern_schemas.py`)
**What:** Select best UI pattern  
**When:** Second step - find matching pattern  
**Output:** Selected pattern with metadata

```python
PatternSelection(
    pattern_id="user_avatar_list",
    pattern_name="User Avatar List Pattern",
    confidence=0.92,
    required_components=["Stack", "ListCard", "Avatar"],
    data_requirements_met=True
)
```

---

### 3. Component Schemas (`component_schemas.py`)
**What:** Build UI components  
**When:** Final step - generate layout  
**Output:** Component tree with data bindings

```python
Component(
    type="Stack",
    props={"direction": "vertical", "gap": "medium"},
    children=[
        Component(
            type="ListCard",
            repeat="data",
            children=[
                Component(type="Avatar", binds_to="avatar_url"),
                Component(type="Heading", binds_to="name")
            ]
        )
    ]
)
```

---

## 📁 Pattern Database Files

### `component_patterns_metadata.json`
**Contains:** UI pattern templates  
**Examples:** user_avatar_list, metric_dashboard, data_table

### `query_patterns_metadata.json`
**Contains:** Query → Layout mappings  
**Examples:** "show leads" → sorted_list_with_metrics

### `layout_patterns_metadata.json`
**Contains:** Complete layout examples  
**Examples:** Lead List, Contact Table, Sales Dashboard

---

## 🔑 Key Component Features

### Data Binding
```json
{"type": "Heading", "binds_to": "name"}
```
→ Displays the `name` field from data

### Static Values
```json
{"type": "Text", "value": "Welcome"}
```
→ Displays fixed text

### Repetition
```json
{"type": "ListCard", "repeat": "data"}
```
→ Creates one card per data item

### Props
```json
{"type": "Metric", "props": {"format": "currency"}}
```
→ Configures component behavior

### Optional
```json
{"type": "Avatar", "binds_to": "avatar_url", "optional": true}
```
→ Only renders if data exists

---

## 🚀 Quick Test

**Input:**
```json
{
  "query": "show me all leads",
  "data": [{"id": 1, "name": "Acme Corp", "revenue": 75000}]
}
```

**Flow:**
1. **QueryAnalysis** → `{object_type: "lead", intent: "view_list", layout_type: "list"}`
2. **PatternSelection** → `{pattern_id: "user_avatar_list", confidence: 0.9}`
3. **Component Tree** → `Stack → ListCard → [Avatar, Heading, Metric]`

**Output:** Complete layout JSON ready to render

---

## 📚 File Locations

```
api/
├── agent/
│   └── schemas/
│       ├── query_schemas.py          # Query analysis
│       ├── pattern_schemas.py        # Pattern selection
│       ├── component_schemas.py      # UI components
│       └── layout_schemas.py         # Complete layouts
└── dataset/
    ├── component_patterns_metadata.json   # Pattern templates
    ├── query_patterns_metadata.json       # Query mappings
    └── layout_patterns_metadata.json      # Layout examples
```

---

## 🎓 Remember

- **Query Schemas** = Understanding (What does user want?)
- **Pattern Schemas** = Selection (Which UI pattern fits?)
- **Component Schemas** = Building (How to construct UI?)

Each schema has a single responsibility and they work together in a pipeline! 🔄


