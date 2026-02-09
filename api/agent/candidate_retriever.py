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
        
        logger.info(f"Retrieved {len(top_candidates)} top candidates")
        return top_candidates
    
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
        
        # Priority 4: Data shapes
        for result in results.get("data_shapes", []):
            candidates.append({
                "source": "data_shape",
                "score": result["score"] * 0.7,
                "chunk": result["chunk"],
                "metadata": result.get("metadata", {})
            })
        
        # Priority 5: Component docs
        for result in results.get("component_docs", []):
            candidates.append({
                "source": "component_doc",
                "score": result["score"] * 0.6,
                "chunk": result["chunk"],
                "metadata": result.get("metadata", {})
            })
        
        # Sort by score (descending)
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        logger.debug(f"Ranked {len(candidates)} total candidates")
        return candidates

