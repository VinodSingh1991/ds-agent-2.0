"""
Chunk builder - Creates searchable chunks from pattern metadata

This module builds rich, searchable chunks from pattern metadata.
Each chunk type has specialized logic for creating searchable text.
"""

from typing import Dict, Any
from .chunk_types import (
    PatternChunk, QueryLayoutChunk,
    IntentMappingChunk
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

        Stores complete LayoutResponse structure for direct use by LLM
        """
        pattern_id = pattern.get("pattern_id", "unknown")
        pattern_name = pattern.get("pattern_name", "Unknown Pattern")
        description = pattern.get("description", "")
        use_cases = pattern.get("use_cases", [])

        # Extract best_for and avoid_when
        best_for = pattern.get("best_for", use_cases)
        avoid_when = pattern.get("avoid_when", [])

        # Build rich searchable text
        searchable_text = f"""
{pattern_name} for {' '.join(use_cases)}.
{description}
Best for: {' '.join(best_for) if isinstance(best_for, list) else best_for}.
Avoid when: {' '.join(avoid_when)}.
        """.strip()

        # Extract keywords including CRM queries
        crm_queries = pattern.get("crm_queries", [])
        keywords = [
            pattern_id,
            pattern_name.lower(),
            *[uc.lower() for uc in use_cases],
            *[q.lower() for q in crm_queries]
        ]

        # Build metadata
        metadata = {
            "pattern_id": pattern_id,
            "pattern_name": pattern_name,
            "title": pattern_name,
            "description": description,
            "layout_type": pattern.get("best_for_layout", "list"),
            "complexity": pattern.get("complexity", "medium"),
            "use_cases": use_cases,
        }

        # Get schema_structure - it should already be a complete LayoutResponse
        schema_structure = pattern.get("schema_structure", {})

        # Build content - remove schema_structure from pattern to avoid duplication
        # Create a copy of pattern without schema_structure
        pattern_without_schema = {k: v for k, v in pattern.items() if k != "schema_structure"}

        content = {
            "pattern": pattern_without_schema,  # Pattern metadata without schema_structure
            "schema_structure": schema_structure  # Complete LayoutResponse
        }

        return PatternChunk(
            chunk_id=f"pattern_{pattern_id}",
            searchable_text=searchable_text,
            metadata=metadata,
            content=content,
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