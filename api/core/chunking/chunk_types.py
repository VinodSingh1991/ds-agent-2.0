"""
Chunk type definitions

Defines the 5 types of chunks used for enhanced RAG:
1. Pattern Chunks - UI patterns with templates
2. Query-Layout Pairs - Real examples
3. Component Documentation - Component usage
4. Intent Mappings - Intent → Pattern
5. Data Shape Patterns - Data characteristics → Layout
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class ChunkType(str, Enum):
    """Types of chunks for RAG"""
    PATTERN = "ui_pattern"
    QUERY_LAYOUT_PAIR = "query_layout_pair"
    COMPONENT_DOC = "component_doc"
    INTENT_MAPPING = "intent_pattern_mapping"
    DATA_SHAPE = "data_shape_pattern"


class Chunk(BaseModel):
    """
    A searchable chunk for RAG
    
    Each chunk has:
    - Unique ID
    - Type (pattern, query-layout, component, etc.)
    - Rich searchable text (with synonyms and variations)
    - Metadata for filtering
    - Content (template, example, documentation, etc.)
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    chunk_type: ChunkType = Field(..., description="Type of chunk")
    searchable_text: str = Field(..., description="Rich text for semantic search")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for filtering")
    content: Dict[str, Any] = Field(default_factory=dict, description="Chunk content (template, example, etc.)")
    
    # Optional fields for specific chunk types
    keywords: List[str] = Field(default_factory=list, description="Keywords for keyword search")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    class Config:
        use_enum_values = True


class PatternChunk(Chunk):
    """
    Chunk representing a UI pattern

    Contains:
    - Pattern metadata
    - Use cases
    - Component requirements
    - Layout template
    """
    chunk_type: Literal[ChunkType.PATTERN] = Field(default=ChunkType.PATTERN)

    def __init__(self, **data):
        super().__init__(**data)
        self.chunk_type = ChunkType.PATTERN


class QueryLayoutChunk(Chunk):
    """
    Chunk representing a query-layout pair

    Contains:
    - Example query
    - Resulting layout
    - Query analysis
    """
    chunk_type: Literal[ChunkType.QUERY_LAYOUT_PAIR] = Field(default=ChunkType.QUERY_LAYOUT_PAIR)

    def __init__(self, **data):
        super().__init__(**data)
        self.chunk_type = ChunkType.QUERY_LAYOUT_PAIR


class ComponentDocChunk(Chunk):
    """
    Chunk representing component documentation

    Contains:
    - Component type
    - Usage guidelines
    - Props and schema
    - Examples
    """
    chunk_type: Literal[ChunkType.COMPONENT_DOC] = Field(default=ChunkType.COMPONENT_DOC)

    def __init__(self, **data):
        super().__init__(**data)
        self.chunk_type = ChunkType.COMPONENT_DOC


class IntentMappingChunk(Chunk):
    """
    Chunk representing intent-to-pattern mapping

    Contains:
    - User intent
    - Recommended patterns
    - Decision logic
    """
    chunk_type: Literal[ChunkType.INTENT_MAPPING] = Field(default=ChunkType.INTENT_MAPPING)

    def __init__(self, **data):
        super().__init__(**data)
        self.chunk_type = ChunkType.INTENT_MAPPING


class DataShapeChunk(Chunk):
    """
    Chunk representing data shape pattern

    Contains:
    - Data characteristics
    - Recommended layout
    - Component suggestions
    """
    chunk_type: Literal[ChunkType.DATA_SHAPE] = Field(default=ChunkType.DATA_SHAPE)

    def __init__(self, **data):
        super().__init__(**data)
        self.chunk_type = ChunkType.DATA_SHAPE

