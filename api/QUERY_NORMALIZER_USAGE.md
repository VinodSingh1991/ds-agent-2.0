# Query Normalizer Usage Guide

## Overview

The Query Normalizer analyzes user queries and determines:
1. **Normalized Query** - A cleaned, professional version of the query
2. **Is RAG Required** - Whether retrieval-augmented generation is needed
3. **Is CRM Related** - Whether the query is related to CRM operations
4. **Reasoning** - Explanation of the analysis

## Setup

### 1. Install Dependencies

```bash
pip install openai>=1.12.0
```

### 2. Set OpenAI API Key

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Running the Test

```bash
cd api
python test_query_normalizer.py
```

## Expected Output

```
================================================================================
TEST 1: Query Normalizer
================================================================================

Query: 'show me top 5 leads with revenue > 50k'
  Normalized Query: show top 5 leads with revenue greater than 50000
  RAG Required: False
  CRM Related: True
  Reasoning: This is a CRM query requesting leads data with filtering...

Query: 'hello'
  Normalized Query: greeting
  RAG Required: False
  CRM Related: False
  Reasoning: This is a greeting, not a CRM-related query...
```

## Usage in Code

```python
from openai import OpenAI
from agent.query_normalizer import QueryNormalizer

# Initialize
client = OpenAI(api_key="your-key")
normalizer = QueryNormalizer(client=client)

# Normalize a query
result = normalizer.normalize("show me top 5 leads")

print(result.normalized_query)  # "show top 5 leads"
print(result.is_rag_required)   # False
print(result.is_crm_related)    # True
print(result.reasoning)         # "This is a CRM query..."
```

## Common Issues

### Issue 1: "OpenAI client is required"

**Error:**
```
ValueError: OpenAI client is required for query normalization
```

**Solution:**
Make sure you pass a valid OpenAI client:
```python
client = OpenAI(api_key="your-key")
normalizer = QueryNormalizer(client=client)  # ✅ Pass client
```

### Issue 2: "OPENAI_API_KEY not set"

**Error:**
```
⚠️  OPENAI_API_KEY not set. Please set it to run this test.
```

**Solution:**
Set the environment variable before running:
```bash
export OPENAI_API_KEY="your-key-here"
python test_query_normalizer.py
```

### Issue 3: Import errors

**Error:**
```
ModuleNotFoundError: No module named 'openai'
```

**Solution:**
Install the OpenAI package:
```bash
pip install openai>=1.12.0
```

## How It Works

1. **Input**: User query (e.g., "show me top 5 leads")

2. **Processing**:
   - Sends query to OpenAI GPT-4 with JSON mode
   - Analyzes if it's a greeting vs CRM query
   - Determines if RAG is needed (specific data retrieval)
   - Normalizes the query to a professional format

3. **Output**: `QueryNormalization` object with:
   - `normalized_query`: Cleaned version
   - `is_rag_required`: Boolean
   - `is_crm_related`: Boolean
   - `reasoning`: Explanation

## Examples

### CRM Query (No RAG)
```python
query = "show me all leads"
result = normalizer.normalize(query)
# normalized_query: "show all leads"
# is_rag_required: False (general query, no specific data needed)
# is_crm_related: True
```

### CRM Query (With RAG)
```python
query = "what was the revenue for Acme Corp last quarter?"
result = normalizer.normalize(query)
# normalized_query: "retrieve revenue for Acme Corp in last quarter"
# is_rag_required: True (needs specific data retrieval)
# is_crm_related: True
```

### Greeting (Not CRM)
```python
query = "hello"
result = normalizer.normalize(query)
# normalized_query: "greeting"
# is_rag_required: False
# is_crm_related: False
```

## Integration with Other Analyzers

The Query Normalizer works alongside:
- **Intent Analyzer** - Detects user intent
- **Object Analyzer** - Detects CRM object type
- **Layout Analyzer** - Determines best layout

Together they form a complete query analysis pipeline.

