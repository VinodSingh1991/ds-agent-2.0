"""
Corrected Layout Schema for OpenAI Structured Outputs.

IMPORTANT:
- Pydantic must produce a REAL JSON schema.
- OpenAI requires: no unsupported types, no forbid extra.
- All fields must appear in required[] if defined in properties.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# =========================================================
# Layout Row Schema
# =========================================================
class LayoutRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    children: Optional[List[Dict[str, Any]]] = None


# =========================================================
# Layout Section Schema
# =========================================================
class LayoutSection(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    rows: List[Dict[str, Any]]  # Keep as Dict to preserve exact pattern structure


# =========================================================
# Metadata Schema
# =========================================================
class LayoutMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_items: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


# =========================================================
# Main Layout Response Schema
# =========================================================
class LayoutResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    query: str
    object_type: str
    layout_type: str
    sections: List[LayoutSection]

    metadata: Optional[LayoutMetadata] = None
    reasoning: Optional[str] = None
    summary: Optional[str] = None

