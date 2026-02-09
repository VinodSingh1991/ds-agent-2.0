"""
Layout schemas for complete UI structures

Defines the structure of complete layouts including sections, rows, and data.
"""

from typing import List, Dict, Optional, Literal, Union
from pydantic import BaseModel, Field
from .component_schemas import Component


class LayoutRow(BaseModel):
    """
    A row in the layout containing components

    Rows are horizontal or vertical containers that hold components.
    They typically use container components like Stack, Card, or Grid.

    Example:
        {
            "type": "Stack",
            "props": {"direction": "vertical", "gap": "medium"},
            "children": [
                {"type": "Heading", "binds_to": "name"},
                {"type": "Text", "binds_to": "description"}
            ]
        }
    """
    type: str = Field(..., description="Container type (Stack, Card, Grid, etc.)")
    props: Optional[Dict[str, Union[str, int, float, bool]]] = Field(default_factory=dict, description="Container properties")
    children: List[Component] = Field(..., description="Components in this row")
    repeat: Optional[str] = Field(None, description="Repeat row for data array")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


class LayoutSection(BaseModel):
    """
    A section containing multiple rows
    
    Sections group related content together. They can have titles and descriptions.
    
    Example:
        {
            "title": "Contact Information",
            "description": "Primary contact details",
            "rows": [...]
        }
    """
    title: Optional[str] = Field(None, description="Section title")
    description: Optional[str] = Field(None, description="Section description")
    rows: List[LayoutRow] = Field(..., description="Rows in this section")
    collapsible: Optional[bool] = Field(False, description="Whether section can be collapsed")
    default_collapsed: Optional[bool] = Field(False, description="Whether section starts collapsed")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


class LayoutMetadata(BaseModel):
    """Metadata about the layout"""
    generated_at: Optional[str] = Field(None, description="Timestamp when layout was generated")
    model_used: Optional[str] = Field(None, description="LLM model used for generation")
    rag_used: Optional[bool] = Field(None, description="Whether RAG was used")
    candidate_count: Optional[int] = Field(None, description="Number of candidate layouts retrieved")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


class LayoutResponse(BaseModel):
    """
    Complete layout response with data
    
    This is the final output of the agent - a complete, ready-to-render layout
    with all data filled in.
    
    Example:
        {
            "id": "layout_leads_001",
            "query": "show me top 5 leads with revenue > 50k",
            "object_type": "lead",
            "layout_type": "list",
            "sections": [...],
            "data": [...],
            "metadata": {...},
            "reasoning": "Selected list layout because..."
        }
    """
    id: str = Field(..., description="Unique layout ID")
    query: str = Field(..., description="Original user query")
    object_type: str = Field(..., description="CRM object type (lead, contact, account, etc.)")
    layout_type: Literal["list", "detail", "dashboard", "table", "grid", "form", "timeline"] = Field(
        ..., 
        description="Type of layout"
    )
    sections: List[LayoutSection] = Field(..., description="Layout sections")
    data: Optional[List[Dict[str, Union[str, int, float, bool, None]]]] = Field(default=None, description="Actual data to display")
    metadata: Optional[LayoutMetadata] = Field(default=None, description="Layout metadata")
    reasoning: Optional[str] = Field(default=None, description="Why this layout was chosen")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs

