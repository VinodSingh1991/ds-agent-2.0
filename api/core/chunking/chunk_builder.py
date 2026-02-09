"""
Chunk builder - Creates searchable chunks from pattern metadata

This module builds rich, searchable chunks from pattern metadata.
Each chunk type has specialized logic for creating searchable text.
"""

from typing import Dict, Any, List
from .chunk_types import (
    Chunk, ChunkType, 
    PatternChunk, QueryLayoutChunk, ComponentDocChunk,
    IntentMappingChunk, DataShapeChunk
)


class ChunkBuilder:
    """Builds searchable chunks from pattern metadata"""
    
    @staticmethod
    def build_pattern_chunk(pattern: Dict[str, Any]) -> PatternChunk:
        """
        Build a pattern chunk from pattern metadata
        
        Creates rich searchable text with:
        - Pattern name and description
        - Use cases
        - Components
        - Data requirements
        """
        pattern_id = pattern.get("pattern_id", "unknown")
        pattern_name = pattern.get("pattern_name", "Unknown Pattern")
        description = pattern.get("description", "")
        use_cases = pattern.get("use_cases", [])
        
        # Extract component information
        components = pattern.get("components", {})
        required_components = components.get("required_components", [])
        optional_components = components.get("optional_components", [])
        layout_direction = components.get("layout_direction", "")
        
        # Extract data requirements
        data_reqs = pattern.get("data_requirements", {})
        min_fields = data_reqs.get("min_fields", [])
        recommended_fields = data_reqs.get("recommended_fields", [])
        
        # Build rich searchable text
        searchable_text = f"""
{pattern_name} for {' '.join(use_cases)}.
{description}
Uses components: {' '.join(required_components + optional_components)}.
Layout direction: {layout_direction}.
Required fields: {' '.join(min_fields)}.
Recommended fields: {' '.join(recommended_fields)}.
Perfect for displaying {pattern.get('best_for', ' '.join(use_cases))}.
        """.strip()
        
        # Extract keywords
        keywords = [
            pattern_id,
            pattern_name.lower(),
            *[uc.lower() for uc in use_cases],
            *[comp.lower() for comp in required_components],
            *min_fields,
            *recommended_fields
        ]
        
        # Build metadata
        metadata = {
            "pattern_id": pattern_id,
            "pattern_name": pattern_name,
            "layout_type": pattern.get("best_for_layout", "list"),
            "complexity": pattern.get("complexity", "medium"),
            "required_components": required_components,
            "min_fields": min_fields,
            "use_cases": use_cases
        }
        
        return PatternChunk(
            chunk_id=f"pattern_{pattern_id}",
            searchable_text=searchable_text,
            metadata=metadata,
            content={
                "pattern": pattern,
                "schema_structure": pattern.get("schema_structure", {})
            },
            keywords=keywords,
            tags=["pattern", pattern.get("complexity", "medium")]
        )
    
    @staticmethod
    def build_query_layout_chunk(
        query: str,
        layout: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> QueryLayoutChunk:
        """
        Build a query-layout pair chunk
        
        Creates searchable text from real query examples
        """
        object_type = analysis.get("object_type", "record")
        intent = analysis.get("intent", "view")
        layout_type = analysis.get("layout_type", "list")
        filters = analysis.get("filters", [])
        
        # Build searchable text
        filter_text = " ".join([
            f"{f.get('field', '')} {f.get('operator', '')} {f.get('value', '')}"
            for f in filters
        ])
        
        searchable_text = f"""
Query: {query}
Shows {object_type} in {layout_type} format.
Intent: {intent}.
Filters: {filter_text}.
Example of how to display {object_type} data with {intent} intent.
        """.strip()
        
        # Extract keywords
        keywords = [
            query.lower(),
            object_type,
            intent,
            layout_type,
            *[f.get('field', '') for f in filters]
        ]
        
        # Build metadata
        metadata = {
            "query": query,
            "object_type": object_type,
            "intent": intent,
            "layout_type": layout_type,
            "has_filters": len(filters) > 0,
            "has_sorting": "sort" in analysis,
            "has_limit": "limit" in analysis
        }
        
        return QueryLayoutChunk(
            chunk_id=f"example_{hash(query)}",
            searchable_text=searchable_text,
            metadata=metadata,
            content={
                "query": query,
                "layout": layout,
                "analysis": analysis
            },
            keywords=keywords,
            tags=["example", intent, layout_type]
        )
    
    @staticmethod
    def build_component_doc_chunk(
        component_type: str,
        documentation: Dict[str, Any]
    ) -> ComponentDocChunk:
        """
        Build a component documentation chunk
        
        Documents how to use a specific component
        """
        description = documentation.get("description", "")
        use_for = documentation.get("use_for", [])
        data_types = documentation.get("data_types", [])
        common_bindings = documentation.get("common_bindings", [])
        
        # Build searchable text
        searchable_text = f"""
{component_type} component for {' '.join(use_for)}.
{description}
Use for data types: {' '.join(data_types)}.
Common bindings: {' '.join(common_bindings)}.
Perfect for displaying {' '.join(use_for)} in UI.
        """.strip()
        
        # Extract keywords
        keywords = [
            component_type.lower(),
            *[u.lower() for u in use_for],
            *data_types,
            *common_bindings
        ]
        
        # Build metadata
        metadata = {
            "component_type": component_type,
            "category": documentation.get("category", "display"),
            "use_for": use_for,
            "data_types": data_types
        }
        
        return ComponentDocChunk(
            chunk_id=f"component_{component_type.lower()}",
            searchable_text=searchable_text,
            metadata=metadata,
            content=documentation,
            keywords=keywords,
            tags=["component", documentation.get("category", "display")]
        )

    @staticmethod
    def build_intent_mapping_chunk(
        intent: str,
        mapping: Dict[str, Any]
    ) -> IntentMappingChunk:
        """
        Build an intent-to-pattern mapping chunk

        Maps user intent to recommended patterns
        """
        user_phrases = mapping.get("user_phrases", [])
        recommended_patterns = mapping.get("recommended_patterns", [])
        indicators = mapping.get("indicators", {})

        # Build searchable text
        pattern_names = [p.get("pattern_id", "") for p in recommended_patterns]

        searchable_text = f"""
Intent: {intent}
User phrases: {' '.join(user_phrases)}
Recommended patterns: {' '.join(pattern_names)}
When user says: {' '.join(user_phrases)}
Use patterns: {' '.join(pattern_names)}
        """.strip()

        # Extract keywords
        keywords = [
            intent,
            *[p.lower() for p in user_phrases],
            *pattern_names
        ]

        # Build metadata
        metadata = {
            "intent": intent,
            "user_phrases": user_phrases,
            "pattern_count": len(recommended_patterns),
            "indicators": indicators
        }

        return IntentMappingChunk(
            chunk_id=f"intent_{intent}",
            searchable_text=searchable_text,
            metadata=metadata,
            content=mapping,
            keywords=keywords,
            tags=["intent", intent]
        )

    @staticmethod
    def build_data_shape_chunk(
        shape_id: str,
        shape_pattern: Dict[str, Any]
    ) -> DataShapeChunk:
        """
        Build a data shape pattern chunk

        Maps data characteristics to recommended layouts
        """
        data_chars = shape_pattern.get("data_characteristics", {})
        recommended_layout = shape_pattern.get("recommended_layout_type", "list")
        recommended_components = shape_pattern.get("recommended_components", [])
        reasoning = shape_pattern.get("reasoning", "")

        # Build searchable text
        record_count = data_chars.get("record_count", {})
        has_numeric = data_chars.get("has_numeric_fields", False)
        has_images = data_chars.get("has_images", False)

        searchable_text = f"""
Data shape: {shape_id}
Record count: {record_count.get('min', 0)} to {record_count.get('max', 100)}
Has numeric fields: {has_numeric}
Has images: {has_images}
Recommended layout: {recommended_layout}
Recommended components: {' '.join(recommended_components)}
Reasoning: {reasoning}
        """.strip()

        # Extract keywords
        keywords = [
            shape_id,
            recommended_layout,
            *recommended_components,
            "numeric" if has_numeric else "",
            "images" if has_images else ""
        ]
        keywords = [k for k in keywords if k]  # Remove empty strings

        # Build metadata
        metadata = {
            "shape_id": shape_id,
            "recommended_layout_type": recommended_layout,
            "recommended_components": recommended_components,
            "data_characteristics": data_chars
        }

        return DataShapeChunk(
            chunk_id=f"data_shape_{shape_id}",
            searchable_text=searchable_text,
            metadata=metadata,
            content=shape_pattern,
            keywords=keywords,
            tags=["data_shape", recommended_layout]
        )

