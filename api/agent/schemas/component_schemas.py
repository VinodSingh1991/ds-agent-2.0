"""
Component schemas for UI generation

Defines the exact structure of UI components using Pydantic.
This ensures type-safe, validated component definitions.
"""

from typing import List, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field


class ComponentValue(BaseModel):
    """
    Static value for a component (when not data-bound)
    
    Examples:
        - Text component with static text: {"text": "Welcome"}
        - Image component with static src: {"src": "/logo.png"}
        - Button with static label: {"label": "Submit"}
    """
    text: Optional[str] = Field(None, description="Static text content")
    src: Optional[str] = Field(None, description="Static image/icon source")
    url: Optional[str] = Field(None, description="Static URL/link")
    label: Optional[str] = Field(None, description="Static label text")
    variant: Optional[str] = Field(None, description="Static variant/style")
    icon: Optional[str] = Field(None, description="Static icon name")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


class ComponentProps(BaseModel):
    """
    Component properties/configuration
    
    Examples:
        - Heading: {"level": 3, "weight": "bold"}
        - Button: {"variant": "primary", "size": "large"}
        - Metric: {"format": "currency", "size": "large"}
    """
    # Common props
    variant: Optional[str] = Field(None, description="Component variant (primary, secondary, outlined, etc.)")
    size: Optional[Literal["small", "medium", "large"]] = Field(None, description="Component size")
    color: Optional[str] = Field(None, description="Component color")
    
    # Layout props
    direction: Optional[Literal["horizontal", "vertical", "row", "column"]] = Field(None, description="Layout direction")
    gap: Optional[Literal["none", "small", "medium", "large"]] = Field(None, description="Gap between items")
    padding: Optional[Literal["none", "small", "medium", "large"]] = Field(None, description="Padding")
    align: Optional[Literal["start", "center", "end", "stretch"]] = Field(None, description="Alignment")
    
    # Text props
    level: Optional[int] = Field(None, ge=1, le=6, description="Heading level (1-6)")
    weight: Optional[Literal["normal", "medium", "semibold", "bold"]] = Field(None, description="Font weight")
    
    # Data formatting props
    format: Optional[Literal["currency", "number", "percentage", "date", "datetime"]] = Field(None, description="Data format")
    
    # Interactive props
    disabled: Optional[bool] = Field(None, description="Whether component is disabled")
    loading: Optional[bool] = Field(None, description="Whether component is in loading state")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


class Component(BaseModel):
    """
    A single UI component
    
    This is the core building block of layouts. Components can:
    - Display static content (using 'value')
    - Bind to data fields (using 'binds_to')
    - Contain child components (using 'children')
    - Repeat for arrays (using 'repeat')
    
    Examples:
        Static heading:
        {
            "type": "Heading",
            "value": {"text": "Welcome"},
            "props": {"level": 1}
        }
        
        Data-bound heading:
        {
            "type": "Heading",
            "binds_to": "name",
            "props": {"level": 3}
        }
        
        Container with children:
        {
            "type": "Stack",
            "props": {"direction": "vertical", "gap": "medium"},
            "children": [...]
        }
        
        Repeating component:
        {
            "type": "ListCard",
            "repeat": "data",
            "children": [...]
        }
    """
    type: str = Field(..., description="Component type (Heading, Text, Button, Card, Stack, etc.)")
    
    # Data binding
    binds_to: Optional[str] = Field(None, description="Data field to bind to (e.g., 'name', 'revenue', 'status')")
    
    # Static value (alternative to binds_to)
    value: Optional[Union[ComponentValue, str, int, float, bool]] = Field(
        None,
        description="Static value when not data-bound (for complex values use ComponentValue)"
    )
    
    # Configuration
    props: Optional[ComponentProps] = Field(default_factory=ComponentProps, description="Component properties")
    
    # Hierarchy
    children: Optional[List['Component']] = Field(None, description="Child components")
    
    # Repetition
    repeat: Optional[str] = Field(None, description="Repeat this component for each item in data array (e.g., 'data', 'items')")
    
    # Conditional rendering
    optional: Optional[bool] = Field(False, description="Component is optional based on data availability")
    show_if: Optional[str] = Field(None, description="Condition for showing component (e.g., 'status == active')")
    
    # Metadata
    key: Optional[str] = Field(None, description="Unique key for component (useful for React)")
    class_name: Optional[str] = Field(None, description="CSS class name")
    
    class Config:
        extra = "forbid"  # Required for OpenAI structured outputs


# Enable forward references
Component.model_rebuild()

