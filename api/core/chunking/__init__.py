"""
Document chunking system for enhanced RAG

This module creates rich, searchable chunks from pattern metadata
to enable better layout retrieval.
"""

from .chunk_types import ChunkType, Chunk
from .chunk_builder import ChunkBuilder
from .chunk_generator import ChunkGenerator

__all__ = [
    "ChunkType",
    "Chunk",
    "ChunkBuilder",
    "ChunkGenerator",
]

