"""
Query analysis schemas

Defines the structure for analyzing and understanding user queries.
"""

from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field


class QueryFilter(BaseModel):
    """
    A single filter condition

    Examples:
        - {"field": "revenue", "operator": ">", "value": 50000}
        - {"field": "status", "operator": "=", "value": "active"}
        - {"field": "name", "operator": "contains", "value": "tech"}
    """
    field: str = Field(..., description="Field name to filter on")
    operator: Literal["=", ">", "<", ">=", "<=", "!=", "contains", "in", "not_in", "between"] = Field(
        ...,
        description="Comparison operator"
    )
    value: Union[str, int, float, bool] = Field(..., description="Filter value (for lists, use comma-separated string)")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


class QueryAnalysis(BaseModel):
    """
    Structured query analysis
    
    This schema captures all the information extracted from a user's query.
    
    Example:
        Query: "show me top 5 leads with revenue > 50k"
        
        Analysis:
        {
            "object_type": "lead",
            "object_list": ["lead"],
            "intent": "view_list",
            "layout_type": "list",
            "filters": [
                {"field": "revenue", "operator": ">", "value": 50000}
            ],
            "sort": "revenue DESC",
            "limit": 5,
            "fields_mentioned": ["revenue"],
            "reasoning": "User wants to see a filtered list of leads..."
        }
    """
    # Object information
    object_type: str = Field(..., description="Primary CRM object (lead, contact, opportunity, account, etc.)")
    object_list: List[str] = Field(default_factory=list, description="All objects mentioned in query")
    
    # Intent
    intent: Literal[
        "greeting",         # Greeting or general conversation (not CRM-related)
        "view_list",        # View multiple records
        "view_detail",      # View single record details
        "view_dashboard",   # View metrics/analytics
        "view_table",           # View tabular data
        "view_summary",           # View summary of a single record,
        "view_trends",            # View trends over time
        "view_comparison",        # View comparison between records
        "view_cards",             # View records as cards
    ] = Field(..., description="User's intent")
    
    # Layout
    layout_type: Literal["list", "detail", "dashboard", "table", "grid", "form", "timeline"] = Field(
        ..., 
        description="Best layout type for this query"
    )
    
    # Filters and sorting
    filters: List[QueryFilter] = Field(default_factory=list, description="Filter conditions")
    sort: Optional[str] = Field(None, description="Sort field and direction (e.g., 'revenue DESC', 'name ASC')")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Number of records to show")
    
    # Aggregation
    aggregation: Optional[Literal["sum", "avg", "count", "min", "max", "group_by"]] = Field(
        None, 
        description="Aggregation type if applicable"
    )
    group_by: Optional[str] = Field(None, description="Field to group by")
    
    # Fields
    fields_mentioned: List[str] = Field(default_factory=list, description="Fields explicitly mentioned in query")
    fields_required: List[str] = Field(default_factory=list, description="Fields required for this layout")
    
    # Context
    time_range: Optional[str] = Field(None, description="Time range if mentioned (e.g., 'last 30 days', 'this month')")
    
    # Reasoning
    reasoning: str = Field(..., description="Explanation of this analysis")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in this analysis")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs

