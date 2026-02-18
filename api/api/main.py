"""
FastAPI server for Disposable UI Agent

Endpoints:
- POST /generate - Generate UI layout from query
- POST /generate-batch - Generate multiple layouts
- POST /reindex - Rebuild/reindex the RAG vector store
- GET /health - Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Try project root first, then api/ directory
root_env = Path(__file__).parent.parent.parent / ".env"
api_env = Path(__file__).parent.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env)
elif api_env.exists():
    load_dotenv(dotenv_path=api_env)
else:
    load_dotenv()  # Try default locations

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.langgraph_ui_agent import LangGraphUIAgent
from core.enhanced_vector_store import EnhancedVectorStore
from loguru import logger

# Configure logger
logger.add("logs/api.log", rotation="10 MB")

# Initialize FastAPI app
app = FastAPI(
    title="Disposable UI Agent API",
    description="Generate UI layouts from natural language queries using LangGraph orchestration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent (singleton)
agent = None


def get_agent() -> LangGraphUIAgent:
    """Get or create agent instance"""
    global agent
    if agent is None:
        # Get model from environment variable or use default
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info(f"Initializing LangGraphUIAgent with model: {model}...")
        agent = LangGraphUIAgent(model=model)
        logger.info("LangGraph Agent initialized successfully")
    return agent


# Request/Response models
class GenerateRequest(BaseModel):
    """Request model for layout generation"""
    query: str = Field(..., description="Natural language query", example="show me all leads")
    data: List[Dict[str, Any]] = Field(..., description="Data to bind to layout (REQUIRED)", example=[{"id": 1, "name": "Acme Corp", "revenue": 75000}])
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context information")


class GenerateResponse(BaseModel):
    """Response model for layout generation"""
    success: bool
    layout: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    query: str
    execution_time_ms: Optional[float] = None


class BatchGenerateRequest(BaseModel):
    """Request model for batch generation"""
    queries: List[str] = Field(..., description="List of queries to process")


class BatchGenerateResponse(BaseModel):
    """Response model for batch generation"""
    success: bool
    results: List[GenerateResponse]
    total: int
    successful: int
    failed: int


class ReindexRequest(BaseModel):
    """Request model for reindexing RAG"""
    force: bool = Field(default=False, description="Force rebuild even if index exists")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Embedding model to use")


class ReindexResponse(BaseModel):
    """Response model for reindexing RAG"""
    success: bool
    message: str
    stats: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent_initialized: bool
    version: str


class GenerateChunksRequest(BaseModel):
    """Request model for generating chunks"""
    regenerate: bool = Field(default=False, description="Force regenerate even if chunks exist")


class GenerateChunksResponse(BaseModel):
    """Response model for generating chunks"""
    success: bool
    message: str
    stats: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None


class GetChunksRequest(BaseModel):
    """Request model for getting chunks"""
    chunk_type: Optional[str] = Field(None, description="Filter by chunk type: ui_pattern, query_layout_pair, component_doc, intent_pattern_mapping, data_shape_pattern")
    limit: Optional[int] = Field(None, description="Limit number of chunks returned")


class GetChunksResponse(BaseModel):
    """Response model for getting chunks"""
    success: bool
    chunks: List[Dict[str, Any]]
    total: int
    filtered_by: Optional[str] = None
    error: Optional[str] = None


# Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Disposable UI Agent API (LangGraph)",
        "version": "2.0.0",
        "orchestration": "LangGraph",
        "endpoints": {
            "generate": "/generate",
            "batch": "/generate-batch",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "version": "2.0.0"
    }


@app.post("/generate", response_model=GenerateResponse, tags=["Generation"])
async def generate_layout(request: GenerateRequest):
    """
    Generate UI layout from natural language query and data

    **IMPORTANT:** You must provide data from your application.
    This agent only generates layouts - it does NOT fetch data.

    Example:
    ```json
    {
        "query": "show me all leads",
        "data": [
            {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
            {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"}
        ],
        "context": {"user_id": "123"}
    }
    ```
    """
    import time
    start_time = time.time()

    try:
        logger.info(f"Generating layout for query: {request.query} with {len(request.data)} records")

        # Get agent
        agent_instance = get_agent()

        # Generate layout
        layout = agent_instance.generate(
            query=request.query,
            data=request.data,
            context=request.context
        )

        execution_time = (time.time() - start_time) * 1000

        logger.info(f"Layout generated successfully in {execution_time:.2f}ms")

        return GenerateResponse(
            success=True,
            layout=layout,
            query=request.query,
            execution_time_ms=execution_time
        )

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Error generating layout: {e}")

        return GenerateResponse(
            success=False,
            error=str(e),
            query=request.query,
            execution_time_ms=execution_time
        )


@app.post("/generate-batch", response_model=BatchGenerateResponse, tags=["Generation"])
async def generate_batch(request: BatchGenerateRequest):
    """
    Generate multiple layouts in batch
    
    Example:
    ```json
    {
        "queries": [
            "show me all leads",
            "display contacts",
            "sales dashboard"
        ]
    }
    ```
    """
    logger.info(f"Processing batch of {len(request.queries)} queries")
    
    results = []
    successful = 0
    failed = 0
    
    for query in request.queries:
        result = await generate_layout(GenerateRequest(query=query))
        results.append(result)
        
        if result.success:
            successful += 1
        else:
            failed += 1
    
    return BatchGenerateResponse(
        success=failed == 0,
        results=results,
        total=len(request.queries),
        successful=successful,
        failed=failed
    )


@app.post("/generate-chunks", response_model=GenerateChunksResponse, tags=["Admin"])
async def generate_chunks(request: GenerateChunksRequest):
    """
    Generate all chunks from pattern files and JSON sources

    This endpoint generates chunks from:
    - Pattern files (patterns/*.json)
    - Query patterns (query_patterns.json)
    - Component patterns (component_patterns.json)
    - Intent mappings (intent_mappings.json)
    - Data shape patterns (data_shape_patterns.json)

    Example:
    ```json
    {
        "regenerate": true
    }
    ```
    """
    logger.info(f"Generating chunks (regenerate={request.regenerate})")

    start_time = time.time()

    try:
        from core.chunking.chunk_generator import ChunkGenerator
        import json

        # Check if chunks already exist
        chunks_path = Path(__file__).parent.parent / "dataset" / "enhanced_chunks.json"
        if chunks_path.exists() and not request.regenerate:
            return GenerateChunksResponse(
                success=False,
                message="Chunks already exist. Use 'regenerate=true' to force regeneration.",
                error="Chunks exist",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        # Initialize chunk generator
        patterns_dir = Path(__file__).parent.parent / "dataset" / "patterns"
        logger.info(f"Initializing chunk generator with patterns from: {patterns_dir}")
        generator = ChunkGenerator(patterns_dir=str(patterns_dir))

        # Generate all chunks
        logger.info("Generating all chunks...")
        all_chunks = generator.generate_all_chunks()

        if not all_chunks:
            return GenerateChunksResponse(
                success=False,
                message="Failed to generate chunks",
                error="No chunks generated",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        logger.info(f"Generated {len(all_chunks)} chunks")

        # Save chunks
        logger.info(f"Saving chunks to {chunks_path}...")
        generator.save_chunks(all_chunks, str(chunks_path))

        # Calculate statistics
        chunk_types = {}
        for chunk in all_chunks:
            chunk_type = chunk.chunk_type
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1

        stats = {
            "total_chunks": len(all_chunks),
            "chunks_by_type": chunk_types,
            "output_file": str(chunks_path)
        }

        execution_time = (time.time() - start_time) * 1000

        logger.info(f"Chunk generation completed in {execution_time:.2f}ms")

        return GenerateChunksResponse(
            success=True,
            message=f"Successfully generated {len(all_chunks)} chunks",
            stats=stats,
            execution_time_ms=execution_time
        )

    except Exception as e:
        logger.error(f"Error generating chunks: {e}")
        return GenerateChunksResponse(
            success=False,
            message="Failed to generate chunks",
            error=str(e),
            execution_time_ms=(time.time() - start_time) * 1000
        )


@app.post("/chunks", response_model=GetChunksResponse, tags=["Admin"])
async def get_chunks(request: GetChunksRequest):
    """
    Get all chunks or filter by type

    Chunk types:
    - ui_pattern: UI pattern templates
    - query_layout_pair: Query-to-layout examples
    - component_doc: Component documentation
    - intent_pattern_mapping: Intent-to-pattern mappings
    - data_shape_pattern: Data shape patterns

    Example:
    ```json
    {
        "chunk_type": "query_layout_pair",
        "limit": 10
    }
    ```
    """
    logger.info(f"Getting chunks (type={request.chunk_type}, limit={request.limit})")

    try:
        import json

        # Load chunks
        chunks_path = Path(__file__).parent.parent / "dataset" / "enhanced_chunks.json"
        if not chunks_path.exists():
            return GetChunksResponse(
                success=False,
                chunks=[],
                total=0,
                error="Chunks file not found. Run /generate-chunks first."
            )

        with open(chunks_path, 'r', encoding='utf-8') as f:
            all_chunks = json.load(f)

        # Filter by type if specified
        if request.chunk_type:
            filtered_chunks = [c for c in all_chunks if c.get("chunk_type") == request.chunk_type]
        else:
            filtered_chunks = all_chunks

        # Apply limit if specified
        if request.limit:
            filtered_chunks = filtered_chunks[:request.limit]

        logger.info(f"Returning {len(filtered_chunks)} chunks (total: {len(all_chunks)})")

        return GetChunksResponse(
            success=True,
            chunks=filtered_chunks,
            total=len(filtered_chunks),
            filtered_by=request.chunk_type
        )

    except Exception as e:
        logger.error(f"Error getting chunks: {e}")
        return GetChunksResponse(
            success=False,
            chunks=[],
            total=0,
            error=str(e)
        )


@app.post("/reindex", response_model=ReindexResponse, tags=["Admin"])
async def reindex_rag(request: ReindexRequest):
    """
    Rebuild or reindex the RAG vector store

    This endpoint rebuilds the FAISS vector index from the chunks file.
    Use this when:
    - You've updated the chunks data
    - You want to use a different embedding model
    - The index is corrupted or missing

    Example:
    ```json
    {
        "force": true,
        "embedding_model": "all-MiniLM-L6-v2"
    }
    ```
    """
    logger.info(f"Reindexing RAG (force={request.force}, model={request.embedding_model})")

    start_time = time.time()

    try:
        # Check if chunks exist
        chunks_path = Path(__file__).parent.parent / "dataset" / "enhanced_chunks.json"
        if not chunks_path.exists():
            return ReindexResponse(
                success=False,
                message="Chunks file not found. Please run /generate-chunks first.",
                error="enhanced_chunks.json not found",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        # Check if index already exists
        index_path = Path(__file__).parent.parent / "vector_index" / "enhanced_layouts.faiss"
        if index_path.exists() and not request.force:
            return ReindexResponse(
                success=False,
                message="Index already exists. Use 'force=true' to rebuild.",
                error="Index exists",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        # Initialize vector store
        logger.info(f"Initializing vector store with model: {request.embedding_model}")
        vector_store = EnhancedVectorStore(embedding_model=request.embedding_model)

        # Load chunks
        logger.info("Loading chunks...")
        chunks = vector_store.load_chunks(chunks_path)

        if not chunks:
            return ReindexResponse(
                success=False,
                message="Failed to load chunks",
                error="No chunks loaded",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        logger.info(f"Loaded {len(chunks)} chunks")

        # Build index
        logger.info("Building FAISS index...")
        vector_store.build_index(chunks)

        # Save index
        logger.info("Saving index to disk...")
        vector_store.save_index()

        # Get statistics
        stats = vector_store.get_stats()

        execution_time = (time.time() - start_time) * 1000

        logger.info(f"Reindexing completed in {execution_time:.2f}ms")

        return ReindexResponse(
            success=True,
            message=f"Successfully rebuilt index with {stats['total_chunks']} chunks",
            stats=stats,
            execution_time_ms=execution_time
        )

    except ImportError as e:
        logger.error(f"Import error during reindexing: {e}")
        return ReindexResponse(
            success=False,
            message="Missing dependencies. Install with: pip install faiss-cpu sentence-transformers",
            error=str(e),
            execution_time_ms=(time.time() - start_time) * 1000
        )

    except Exception as e:
        logger.error(f"Error during reindexing: {e}")
        return ReindexResponse(
            success=False,
            message="Failed to rebuild index",
            error=str(e),
            execution_time_ms=(time.time() - start_time) * 1000
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

