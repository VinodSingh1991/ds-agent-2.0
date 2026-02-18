"""
Pattern selection schemas

Defines schemas for UI pattern selection and metadata.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PatternMetadata(BaseModel):
    """
    Metadata about a UI pattern
    
    This describes the characteristics and requirements of a UI pattern.
    """
    pattern_id: str = Field(..., description="Unique pattern identifier")
    pattern_name: str = Field(..., description="Human-readable pattern name")
    description: str = Field(..., description="Pattern description")
    
    # Use cases
    use_cases: List[str] = Field(default_factory=list, description="When to use this pattern")
    best_for: List[str] = Field(default_factory=list, description="What this pattern is best for")
    
    # Requirements
    min_records: Optional[int] = Field(None, description="Minimum number of records")
    max_records: Optional[int] = Field(None, description="Maximum number of records")
    layout_direction: Optional[str] = Field(None, description="Layout direction (vertical, horizontal)")
    
    # Complexity
    complexity: Optional[str] = Field(None, description="Pattern complexity (simple, medium, complex)")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


class PatternSelection(BaseModel):
    """
    Selected UI pattern with reasoning
    
    This represents the result of pattern selection - which pattern was chosen and why.
    
    Example:
        {
            "pattern_id": "user_avatar_list",
            "pattern_name": "User Avatar List Pattern",
            "confidence": 0.92,
            "reasoning": "Query requests a list of contacts with photos...",
            "required_components": ["Stack", "ListCard", "Avatar", "Heading"],
            "data_requirements_met": true,
            "alternative_patterns": ["simple_list", "table_view"]
        }
    """
    pattern_id: str = Field(..., description="ID of selected pattern")
    pattern_name: str = Field(..., description="Name of selected pattern")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Why this pattern was selected")
    
    # Components
    required_components: List[str] = Field(..., description="Components needed for this pattern")
    
    # Validation
    data_requirements_met: bool = Field(..., description="Whether data meets pattern requirements")
    missing_fields: List[str] = Field(default_factory=list, description="Fields required but not available in data")
    
    # Alternatives
    alternative_patterns: List[str] = Field(default_factory=list, description="Other patterns that could work")
    
    # Metadata
    metadata: Optional[PatternMetadata] = Field(None, description="Full pattern metadata")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs

