# Reindex Endpoint Documentation

## Overview

The `/reindex` endpoint allows you to rebuild or reindex the RAG (Retrieval-Augmented Generation) vector store. This is useful when you've updated the chunks data, want to use a different embedding model, or the index is corrupted or missing.

## Endpoint

**POST** `/reindex`

## Request Body

```json
{
  "force": false,
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `force` | boolean | No | `false` | Force rebuild even if index exists |
| `embedding_model` | string | No | `"all-MiniLM-L6-v2"` | Embedding model to use for vector generation |

## Response

```json
{
  "success": true,
  "message": "Successfully rebuilt index with 150 chunks",
  "stats": {
    "total_chunks": 150,
    "index_size": 150,
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_types": {
      "query_layout_pair": 50,
      "ui_pattern": 40,
      "intent_pattern_mapping": 30,
      "component_doc": 20,
      "data_shape_pattern": 10
    }
  },
  "execution_time_ms": 12345.67,
  "error": null
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the reindexing was successful |
| `message` | string | Human-readable message about the operation |
| `stats` | object | Statistics about the rebuilt index (only on success) |
| `execution_time_ms` | number | Time taken to complete the operation in milliseconds |
| `error` | string | Error message if operation failed |

## Use Cases

### 1. Check if Index Exists

```bash
curl -X POST http://localhost:8000/reindex \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

If the index already exists, you'll get:
```json
{
  "success": false,
  "message": "Index already exists. Use 'force=true' to rebuild.",
  "error": "Index exists"
}
```

### 2. Force Rebuild Index

```bash
curl -X POST http://localhost:8000/reindex \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

This will rebuild the entire index from scratch.

### 3. Use Different Embedding Model

```bash
curl -X POST http://localhost:8000/reindex \
  -H "Content-Type: application/json" \
  -d '{
    "force": true,
    "embedding_model": "all-mpnet-base-v2"
  }'
```

## Prerequisites

Before using this endpoint, ensure:

1. **Chunks file exists**: The `dataset/enhanced_chunks.json` file must exist
   - If missing, run: `python generate_chunks.py`

2. **Dependencies installed**: Required packages must be installed
   - `pip install faiss-cpu sentence-transformers`

## Error Responses

### Missing Chunks File

```json
{
  "success": false,
  "message": "Chunks file not found. Please run 'python generate_chunks.py' first.",
  "error": "enhanced_chunks.json not found"
}
```

### Missing Dependencies

```json
{
  "success": false,
  "message": "Missing dependencies. Install with: pip install faiss-cpu sentence-transformers",
  "error": "No module named 'faiss'"
}
```

### Index Already Exists

```json
{
  "success": false,
  "message": "Index already exists. Use 'force=true' to rebuild.",
  "error": "Index exists"
}
```

## Performance Notes

- **Execution time**: Rebuilding the index typically takes 30-60 seconds depending on:
  - Number of chunks
  - Embedding model size
  - System performance

- **Resource usage**: The operation is CPU-intensive during embedding generation

## Testing

Use the provided test script:

```bash
python test_reindex.py
```

Or test via the interactive API docs:

1. Open http://localhost:8000/docs
2. Navigate to the `/reindex` endpoint under "Admin" section
3. Click "Try it out"
4. Modify the request body as needed
5. Click "Execute"

## Integration Example

```python
import requests

# Rebuild index with custom embedding model
response = requests.post(
    "http://localhost:8000/reindex",
    json={
        "force": True,
        "embedding_model": "all-MiniLM-L6-v2"
    }
)

result = response.json()

if result["success"]:
    print(f"✅ Index rebuilt successfully!")
    print(f"Total chunks: {result['stats']['total_chunks']}")
    print(f"Execution time: {result['execution_time_ms']:.2f}ms")
else:
    print(f"❌ Error: {result['message']}")
```

## Best Practices

1. **Backup before rebuild**: If you have a working index, consider backing it up before forcing a rebuild
2. **Use force sparingly**: Only use `force=true` when necessary (e.g., after updating chunks)
3. **Monitor execution time**: Large datasets may take several minutes to reindex
4. **Check logs**: Review server logs for detailed progress information during reindexing

