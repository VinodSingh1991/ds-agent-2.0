# Layout Generation - Current Implementation

## Overview

The layout generation system uses a **complete LayoutResponse structure** approach where:
1. **Chunk Generator** reads pattern files and creates full `LayoutResponse` structures
2. **Chunk Builder** wraps component trees in complete layout with sections and rows
3. **LLM** receives complete layout and fills data
4. **No wrapping needed** - LLM output is already in correct format

## Complete Data Flow

```
Pattern JSON Files (dataset/patterns/*.json)
    ↓
ChunkGenerator.load_patterns() - Loads all pattern files
    ↓
ChunkGenerator.generate_pattern_chunks() - Processes each pattern
    ↓
ChunkBuilder.build_pattern_chunk() - Creates complete LayoutResponse
    ↓
Vector Store - Stores complete layouts
    ↓
RAG Retrieval - Returns complete layout
    ↓
Layout Generator - Sends to LLM with data
    ↓
OpenAI Structured Output - Fills data, returns LayoutResponse
    ↓
LangGraph Agent - Serializes (exclude_none=True, exclude_unset=True)
    ↓
API Response - Clean JSON without null fields
```

## Architecture

### 1. Pattern Files (`dataset/patterns/*.json`)

Each pattern file contains:
- **pattern_id**: Unique identifier
- **pattern_name**: Human-readable name
- **description**: What the pattern does
- **use_cases**: When to use this pattern
- **crm_queries**: Example queries that match this pattern
- **components**: Component structure
- **data_requirements**: Required and recommended fields
- **schema_structure**: The actual component tree

Example structure:
```json
{
  "pattern_id": "account_summary_comprehensive",
  "pattern_name": "Comprehensive Account Summary Pattern",
  "description": "Multi-section comprehensive account overview...",
  "use_cases": ["complete account overview", "account 360 view"],
  "crm_queries": ["explain this account", "give me summary of this account"],
  "schema_structure": {
    "type": "Stack",
    "props": {"direction": "vertical", "gap": 8},
    "children": [...]
  }
}
```

### 2. Chunk Generator (`chunk_generator.py`)

**Loads patterns from files:**
```python
def load_patterns(self) -> List[Dict[str, Any]]:
    """Load pattern metadata from individual JSON files in patterns folder"""
    patterns = []
    pattern_files = sorted(self.patterns_dir.glob("*.json"))

    for pattern_file in pattern_files:
        with open(pattern_file, 'r', encoding='utf-8') as f:
            pattern = json.load(f)
            patterns.append(pattern)

    return patterns
```

**Generates chunks:**
```python
def generate_pattern_chunks(self, patterns: List[Dict[str, Any]]) -> List[Chunk]:
    """Generate pattern chunks from pattern metadata"""
    chunks = []
    for pattern in patterns:
        chunk = self.builder.build_pattern_chunk(pattern)
        chunks.append(chunk)
    return chunks
```

### 3. Chunk Builder (`chunk_builder.py`)

**Creates complete LayoutResponse structure:**

```python
def build_pattern_chunk(pattern: Dict[str, Any]) -> PatternChunk:
    # Extract pattern metadata
    pattern_id = pattern.get("pattern_id", "unknown")
    pattern_name = pattern.get("pattern_name", "Unknown Pattern")
    description = pattern.get("description", "")
    schema_structure = pattern.get("schema_structure", {})
    data_shape = data_reqs.get("data_shape", "array")

    # Build complete LayoutResponse structure
    full_layout = {
        "id": f"layout_{pattern_id}",
        "query": "{{query}}",  # Placeholder
        "object_type": data_shape,
        "layout_type": pattern.get("best_for_layout", "list"),
        "sections": [
            {
                "id": "body",
                "title": pattern_name,
                "description": description,
                "rows": [schema_structure]  # Component tree wrapped in rows
            }
        ]
    }

    return PatternChunk(
        chunk_id=f"pattern_{pattern_id}",
        searchable_text=searchable_text,
        metadata=metadata,
        content={
            "pattern": pattern,
            "schema_structure": full_layout,  # Complete LayoutResponse
            "component_tree": schema_structure  # Original component tree
        },
        keywords=keywords,
        tags=["pattern", pattern.get("complexity", "medium")]
    )
```

**Key points:**
- Takes `schema_structure` from pattern file (component tree)
- Wraps it in complete `LayoutResponse` with `id`, `query`, `object_type`, `layout_type`, `sections`
- Each section has `id`, `title`, `description`, and `rows`
- The component tree goes into `rows` array
- Stores both complete layout and original component tree

### 4. Layout Generator (`layout_generator.py`)

**Retrieves pattern and sends to LLM:**

```python
def generate_layout(self, candidate: Dict[str, Any], context: Dict[str, Any]) -> LayoutResponse:
    # Extract the complete layout structure from candidate
    pattern_structure = candidate.get("schema_structure", candidate)

    # Build prompt with pattern and data
    prompt = f"""
Pattern (fill with data):
{json.dumps(pattern_structure, indent=2)}

Data to fill:
{json.dumps(context.get("data", {}), indent=2)}
"""

    # Send to OpenAI with LayoutResponse schema
    completion = self.client.beta.chat.completions.parse(
        model=self.model,
        messages=[
            {"role": "system", "content": "You are a data filler..."},
            {"role": "user", "content": prompt}
        ],
        response_format=LayoutResponse  # Complete layout
    )

    layout = completion.choices[0].message.parsed
    return layout  # Already in correct LayoutResponse format
```

**Key points:**
- Extracts `schema_structure` from RAG candidate (complete LayoutResponse)
- Sends complete layout to LLM with data
- LLM returns filled LayoutResponse directly
- No wrapping needed

### 5. LangGraph Agent (`langgraph_ui_agent.py`)

**Orchestrates flow and serializes:**

```python
def generate_layout_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Get candidate from RAG
    candidate = state.get("candidate", {})

    # Generate layout
    layout = layout_generator.generate_layout(candidate, state.get("context", {}))

    # Store and serialize
    state["layout"] = layout
    state["result"] = layout.model_dump(exclude_none=True, exclude_unset=True)

    return state
```

**Key points:**
- Uses `exclude_none=True` to remove fields explicitly set to None
- Uses `exclude_unset=True` to remove fields never set (defaulted to None)
- This removes all null fields from the output

## Schema Design (Prevents Hallucination)

### Problem: Complex Pydantic Models with Many Optional Fields

**Before (caused hallucination):**
```python
class Component(BaseModel):
    type: str
    value: str
    key: Optional[str] = None
    children: Optional[List['Component']] = None
    columns: Optional[List[TableColumn]] = None
    variant: Optional[str] = None
    sortable: Optional[bool] = None
    filterable: Optional[bool] = None
    # ... 20+ more optional fields
```

**Problem:** OpenAI's structured output generates values for ALL fields, even optional ones, resulting in:
```json
{
  "type": "Heading",
  "value": "Account Details",
  "key": null,
  "children": null,
  "columns": null,
  "variant": null,
  "sortable": null,
  // ... 20+ more null fields
}
```

### Solution: Dict[str, Any] for Dynamic Content

**After (prevents hallucination):**
```python
class LayoutRow(BaseModel):
    type: str = Field(..., description="Container type")
    children: Optional[List[Dict[str, Any]]] = Field(None, description="Child components")

    class Config:
        extra = "forbid"  # Forbid fields not defined in model

class LayoutSection(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    rows: List[Dict[str, Any]] = Field(..., description="Rows - preserves exact pattern structure")

    class Config:
        extra = "forbid"

class LayoutResponse(BaseModel):
    id: str
    query: str
    object_type: str
    layout_type: str
    sections: List[Dict[str, Any]] = Field(..., description="Sections - preserves exact pattern structure")
    metadata: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        extra = "forbid"
```

**Benefits:**
- `Dict[str, Any]` preserves exact structure from pattern
- LLM returns same fields it receives, no extra null fields
- `extra = "forbid"` prevents adding fields not in the model
- Flexibility comes from `Dict[str, Any]`, not from `extra = "allow"`

## Benefits

✅ **Complete structure from start** - Pattern files → Chunks → LLM all use LayoutResponse
✅ **No wrapping/unwrapping** - LLM output is already in correct format
✅ **Prevents hallucination** - Dict[str, Any] preserves exact pattern structure
✅ **Clean output** - `exclude_none=True, exclude_unset=True` removes null fields
✅ **Metadata preserved** - `id`, `query`, `object_type` from pattern
✅ **Simpler flow** - Less code, fewer transformations

## Example

**Pattern in chunk:**
```json
{
  "id": "layout_account_summary",
  "query": "{{query}}",
  "object_type": "object",
  "layout_type": "detail",
  "sections": [
    {
      "id": "body",
      "title": "Account Summary",
      "rows": [
        {
          "type": "Stack",
          "direction": "vertical",
          "gap": 16,
          "children": [
            {"type": "Heading", "value": "{{account_name}}", "level": 2},
            {"type": "Text", "value": "{{description}}"}
          ]
        }
      ]
    }
  ]
}
```

**LLM fills data and returns:**
```json
{
  "id": "layout_account_summary",
  "query": "show account details",
  "object_type": "object",
  "layout_type": "detail",
  "sections": [
    {
      "id": "body",
      "title": "Account Summary",
      "rows": [
        {
          "type": "Stack",
          "direction": "vertical",
          "gap": 16,
          "children": [
            {"type": "Heading", "value": "Acme Corp", "level": 2},
            {"type": "Text", "value": "Leading technology provider"}
          ]
        }
      ]
    }
  ]
}
```

## Key Files

- `api/core/chunking/chunk_builder.py` - Creates complete LayoutResponse structures
- `api/agent/layout_generator.py` - Sends to LLM, receives filled layout
- `api/agent/langgraph_ui_agent.py` - Orchestrates flow, serializes output
- `api/agent/schemas/layout_schemas.py` - Pydantic schemas for validation

