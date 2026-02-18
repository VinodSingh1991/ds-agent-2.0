# Layout Generation Fix

## Current Implementation

### LLM Returns Complete LayoutResponse

The LLM now receives a **complete LayoutResponse structure** as a pattern and returns the filled version directly.

**How it works:**

1. **Pattern from RAG** was just a component structure: `{"type": "Stack", "children": [...]}`
2. **LLM was forced to return** a complete `LayoutResponse` with `id`, `query`, `object_type`, `layout_type`, `sections`, etc.
3. **The LLM didn't know** what values to use for these wrapper fields since they weren't in the pattern

### Example of the Problem

**Input pattern (from RAG):**
```json
{
  "type": "Stack",
  "props": {"orientation": "vertical"},
  "children": [
    {"type": "Heading", "value": "{{title}}", "level": 2},
    {"type": "Table", "props": {"columns": "{{columns}}"}, "binds_to": "data"}
  ]
}
```

**What we got (wrong):**
```json
{
  "id": "layout_account_details",
  "query": "show me all leads",
  "object_type": "account",
  "layout_type": "table",
  "sections": [
    {
      "id": "body",
      "rows": [
        {
          "type": "Stack",
          "children": [
            {"type": "Heading", "value": "Account Details", "level": 2},
            {"type": "Table", "value": "Accounts table", "columns": [...]}
          ]
        }
      ]
    }
  ]
}
```

The LLM was creating the entire wrapper structure instead of just filling the pattern.

## Solution

**Separate concerns:**
1. **LLM fills ONLY the component pattern** (returns `LayoutRow`)
2. **Code wraps it in `LayoutResponse`** structure

### Changes Made

#### 1. `layout_generator.py`

**Before:**
- LLM was asked to return `LayoutResponse` (complete structure)
- Pattern was passed as entire candidate object
- LLM had to guess values for `id`, `query`, `object_type`, etc.

**After:**
- LLM returns only `LayoutRow` (just the filled component structure)
- Pattern is extracted from candidate: `candidate.get("schema_structure", candidate)`
- Code wraps the result in `LayoutResponse` using metadata from candidate

**Key changes:**
```python
# Extract pattern structure
pattern_structure = candidate.get("schema_structure", candidate)

# LLM fills only the component structure
response_format=LayoutRow  # Not LayoutResponse!

# Wrap in LayoutResponse in code
layout = self._wrap_in_layout_response(
    filled_row=filled_row,
    candidate=candidate,
    context=context
)
```

#### 2. `langgraph_ui_agent.py`

**Added query to context:**
```python
# Prepare context with query
context = state.get("context", {})
if isinstance(context, dict):
    context["query"] = state.get("query", "")
else:
    context = {"query": state.get("query", "")}
```

**Fixed serialization to exclude None values:**
```python
state["result"] = layout.model_dump(exclude_none=True)
```

This ensures the query is available when building the `LayoutResponse` and removes all null fields from the output.

#### 3. `structured_ui_agent_v2.py`

**Fixed serialization:**
```python
result = layout.model_dump(exclude_none=True)
```

## Benefits

1. **LLM focuses on data filling only** - simpler task, better results
2. **Wrapper structure is deterministic** - built from candidate metadata
3. **No hallucination of wrapper fields** - `id`, `query`, `object_type` come from metadata
4. **Clearer separation of concerns** - LLM fills data, code handles structure

### Problem 2: Extra Null Fields in Components

Components were including all possible props with `null` values:
```json
{
  "type": "Heading",
  "value": "Account Details",
  "level": 2,
  "key": null,
  "children": null,
  "columns": null,
  "variant": null,
  "sortable": null,
  ...  // 20+ more null fields
}
```

**Root cause:**
- OpenAI's structured output with Pydantic schemas includes ALL fields defined in the schema
- The `Component` class has 20+ optional fields for different component types
- Even with `exclude_none=True` in schema config, OpenAI still generates null values

**Solution:**
1. Updated system prompt to explicitly tell LLM not to add extra fields
2. Used `model_dump(exclude_none=True, exclude_unset=True)` to remove null fields during serialization

**Changes:**
```python
# langgraph_ui_agent.py
state["result"] = layout.model_dump(exclude_none=True, exclude_unset=True)
```

## Testing

Run the test script:
```bash
cd api
python test_layout_fix.py
```

Expected output:
- ✅ Layout generated successfully
- Shows proper structure with filled data
- Table columns extracted from data fields
- No extra components added
- **No null fields in components**

