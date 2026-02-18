"""
Candidate Retriever

Single responsibility: Retrieve and rank candidate layouts from vector store.

Uses multi-stage search to find relevant patterns, examples, and recommendations.
"""

from typing import List, Dict, Any
from loguru import logger

from agent.schemas.query_schemas import QueryAnalysis
from core.enhanced_vector_store import EnhancedVectorStore


class CandidateRetriever:
    """
    Retrieves candidate layouts from vector store
    
    Responsibilities:
    - Multi-stage vector search
    - Rank candidates by relevance
    - Combine results from different chunk types
    - Select top candidates
    """
    
    def __init__(self, vector_store: EnhancedVectorStore):
        """
        Initialize candidate retriever
        
        Args:
            vector_store: Enhanced vector store instance
        """
        self.vector_store = vector_store
        logger.info("Initialized CandidateRetriever")
    
    def retrieve(
        self,
        query: str,
        analysis: QueryAnalysis,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve candidate layouts
        
        Args:
            query: User query
            analysis: Query analysis
            k: Number of candidates to return
            
        Returns:
            List of top k candidate layouts
        """
        logger.debug(f"Retrieving candidates for query: {query}")
        
        # Multi-stage search
        results = self.vector_store.multi_stage_search(
            query=query,
            analysis=analysis.model_dump(),
            k_per_stage=3
        )
        
        # Combine and rank
        candidates = self._combine_and_rank(results)
        
        # Select top k
        top_candidates = candidates[:k]

        # Extract best matching UI patterns
        ui_patterns = self._get_best_match_ui_patterns(results)

        # Extract layout schemas from best matching layout examples
        layout_schemas = self._extract_layout_schema_from_best_match_layout(ui_patterns)
        
        logger.info(f"Retrieved {len(top_candidates)} top candidates")
        return layout_schemas 
    
    def _combine_and_rank(self, results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Combine results from different stages and rank by relevance
        
        Args:
            results: Multi-stage search results
            
        Returns:
            Ranked list of candidates
        """
        candidates = []
        
        # Priority 1: Query examples (most relevant)
        for result in results.get("query_examples", []):
            candidates.append({
                "source": "query_example",
                "score": result["score"] * 1.0,  # Highest priority
                "chunk": result["chunk"],
                "metadata": result.get("metadata", {})
            })
        
        # Priority 2: UI patterns
        for result in results.get("patterns", []):
            candidates.append({
                "source": "ui_pattern",
                "score": result["score"] * 0.9,  # Slightly lower
                "chunk": result["chunk"],
                "metadata": result.get("metadata", {})
            })
        
        # Priority 3: Intent mappings
        for result in results.get("intent_mappings", []):
            candidates.append({
                "source": "intent_mapping",
                "score": result["score"] * 0.8,
                "chunk": result["chunk"],
                "metadata": result.get("metadata", {})
            })
    
        # Sort by score (descending)
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        logger.debug(f"Ranked {len(candidates)} total candidates")
        return candidates


    def _get_best_match_ui_patterns(self, results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Extract best matching UI patterns from results
        
        Args:
            results: Multi-stage search results
            
        Returns:
            List of best matching UI patterns
        """
        patterns = []
        
        for result in results.get("patterns", []):
            patterns.append({
                "score": result["score"],
                "chunk": result["chunk"],
                "metadata": result.get("metadata", {})
            })
        
        # Sort by score (descending)
        patterns.sort(key=lambda x: x["score"], reverse=True)
        
        logger.debug(f"Extracted {len(patterns)} UI pattern candidates")
        return patterns
    
    def _extract_layout_schema_from_best_match_layout(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract layout schemas from best matching layout examples
        
        Args:
            patterns: List of best matching UI patterns
            
        Returns:
            List of layout schemas
        """
        layouts = []
        
        for result in patterns:
            layouts.append({
                "score": result["score"],
                "chunk": result["chunk"],
                "metadata": result.get("metadata", {})
            })
        
        # Sort by score (descending)
        layouts.sort(key=lambda x: x["score"], reverse=True)
        
        logger.debug(f"Extracted {len(layouts)} layout schema candidates")
        best_layouts = layouts[0]  # Select top 1 layout schemas
        schema_structure = self._extract_schema_structure(best_layouts["chunk"])

        if not schema_structure:
            schema_structure = self.get_fallback_layout()
            logger.warning(f"Using fallback layout because no layout schema found")
        return schema_structure
        #schema_structure

    def _extract_schema_structure(self, layout_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract layout schema structure from layout chunk
        
        Args:
            layout_chunk: Layout chunk
            
        Returns:
            Layout schema structure
        """
        return layout_chunk.get("content", {}).get("schema_structure", {})
    
    def get_fallback_layout(self) -> Dict[str, Any]:
        return {
            "schema_structure": {
                "type": "Stack",
                "props": {
                    "direction": "vertical",
                    "gap": 8
                },
                "children": [
                    {
                        "type": "HtmlText",
                        "value": "<div class='data-view'>...</div>"
                    }
                ]
            }
        }