"""
Enhanced Vector Store with FAISS

Multi-type chunk search with metadata filtering and ranking.
Supports semantic search across different chunk types.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    logger.warning("FAISS or sentence-transformers not installed. Install with: pip install faiss-cpu sentence-transformers")
    faiss = None
    SentenceTransformer = None


class EnhancedVectorStore:
    """
    Enhanced vector store with multi-type chunk search
    
    Features:
    - Semantic search using sentence transformers
    - Metadata filtering by chunk type
    - Multi-stage search (search different chunk types)
    - Ranking and relevance scoring
    """
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        index_path: Optional[str] = None,
        metadata_path: Optional[str] = None
    ):
        """
        Initialize enhanced vector store
        
        Args:
            embedding_model: Sentence transformer model name
            index_path: Path to FAISS index file
            metadata_path: Path to metadata pickle file
        """
        self.embedding_model_name = embedding_model
        self.model = None
        self.index = None
        self.chunks = []
        self.chunk_metadata = []
        
        # Set default paths
        if index_path is None:
            index_path = Path(__file__).parent.parent / "vector_index" / "enhanced_layouts.faiss"
        if metadata_path is None:
            metadata_path = Path(__file__).parent.parent / "vector_index" / "enhanced_layouts_metadata.pkl"
        
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        
        logger.info(f"Initialized EnhancedVectorStore with model: {embedding_model}")
    
    def _load_embedding_model(self):
        """Load sentence transformer model"""
        if self.model is None:
            if SentenceTransformer is None:
                raise ImportError("sentence-transformers not installed")
            
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            logger.info("Embedding model loaded")
    
    def load_chunks(self, chunks_path: str = None) -> List[Dict[str, Any]]:
        """
        Load chunks from JSON file
        
        Args:
            chunks_path: Path to enhanced_chunks.json
            
        Returns:
            List of chunks
        """
        if chunks_path is None:
            chunks_path = Path(__file__).parent.parent / "dataset" / "enhanced_chunks.json"
        
        chunks_path = Path(chunks_path)
        
        if not chunks_path.exists():
            logger.error(f"Chunks file not found: {chunks_path}")
            logger.info("Run 'python generate_chunks.py' first to generate chunks")
            return []
        
        try:
            with open(chunks_path, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            logger.info(f"Loaded {len(chunks)} chunks from {chunks_path}")
            return chunks
        
        except Exception as e:
            logger.error(f"Error loading chunks: {e}")
            return []
    
    def build_index(self, chunks: List[Dict[str, Any]]):
        """
        Build FAISS index from chunks
        
        Args:
            chunks: List of chunk dictionaries
        """
        if faiss is None:
            raise ImportError("faiss not installed")
        
        self._load_embedding_model()
        
        logger.info("Building FAISS index...")
        
        # Extract searchable text from chunks
        texts = [chunk.get("searchable_text", "") for chunk in chunks]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        logger.info(f"Creating FAISS index with dimension: {dimension}")
        
        # Use IndexFlatL2 for exact search (can switch to IndexIVFFlat for large datasets)
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        # Store chunks and metadata
        self.chunks = chunks
        self.chunk_metadata = [
            {
                "chunk_id": chunk.get("chunk_id"),
                "chunk_type": chunk.get("chunk_type"),
                "metadata": chunk.get("metadata", {}),
                "keywords": chunk.get("keywords", []),
                "tags": chunk.get("tags", [])
            }
            for chunk in chunks
        ]
        
        logger.info(f"FAISS index built with {self.index.ntotal} vectors")
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            logger.error("No index to save. Build index first.")
            return
        
        # Create directory if it doesn't exist
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        logger.info(f"Saved FAISS index to {self.index_path}")
        
        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                "chunks": self.chunks,
                "chunk_metadata": self.chunk_metadata,
                "embedding_model": self.embedding_model_name
            }, f)
        logger.info(f"Saved metadata to {self.metadata_path}")

    def load_index(self):
        """Load FAISS index and metadata from disk"""
        if not self.index_path.exists():
            logger.error(f"Index file not found: {self.index_path}")
            logger.info("Run build_vector_index.py first to create the index")
            return False

        if not self.metadata_path.exists():
            logger.error(f"Metadata file not found: {self.metadata_path}")
            return False

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")

            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)

            self.chunks = data["chunks"]
            self.chunk_metadata = data["chunk_metadata"]
            self.embedding_model_name = data.get("embedding_model", self.embedding_model_name)

            logger.info(f"Loaded {len(self.chunks)} chunks")

            # Load embedding model
            self._load_embedding_model()

            return True

        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False

    def search(
        self,
        query: str,
        k: int = 5,
        chunk_type: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks

        Args:
            query: Search query
            k: Number of results to return
            chunk_type: Filter by chunk type (e.g., "ui_pattern", "query_layout_pair")
            metadata_filter: Additional metadata filters

        Returns:
            List of matching chunks with scores
        """
        if self.index is None:
            logger.error("Index not loaded. Call load_index() first.")
            return []

        if self.model is None:
            self._load_embedding_model()

        # Generate query embedding
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        # Search FAISS index (get more results for filtering)
        search_k = k * 10 if (chunk_type or metadata_filter) else k
        distances, indices = self.index.search(query_embedding, search_k)

        # Build results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]
            metadata = self.chunk_metadata[idx]

            # Apply filters
            if chunk_type and chunk.get("chunk_type") != chunk_type:
                continue

            if metadata_filter:
                if not self._matches_filter(metadata.get("metadata", {}), metadata_filter):
                    continue

            # Calculate relevance score (convert distance to similarity)
            # Lower distance = higher similarity
            similarity = 1 / (1 + distance)

            results.append({
                "chunk": chunk,
                "score": float(similarity),
                "distance": float(distance),
                "chunk_id": chunk.get("chunk_id"),
                "chunk_type": chunk.get("chunk_type"),
                "metadata": metadata.get("metadata", {})
            })

            if len(results) >= k:
                break

        logger.debug(f"Found {len(results)} results for query: {query[:50]}...")
        return results

    def multi_stage_search(
        self,
        query: str,
        analysis: Optional[Dict[str, Any]] = None,
        k_per_stage: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Multi-stage search across different chunk types

        Args:
            query: Search query
            analysis: Query analysis (optional, for better filtering)
            k_per_stage: Results per stage

        Returns:
            Dictionary with results per chunk type
        """
        results = {}

        # Stage 1: Search query-layout pairs (examples)
        results["query_examples"] = self.search(
            query=query,
            k=k_per_stage,
            chunk_type="query_layout_pair"
        )

        # Stage 2: Search UI patterns
        pattern_query = query
        if analysis:
            # Enhance query with analysis
            intent = analysis.get("intent", "")
            layout_type = analysis.get("layout_type", "")
            pattern_query = f"{query} {intent} {layout_type}"

        results["patterns"] = self.search(
            query=pattern_query,
            k=k_per_stage,
            chunk_type="ui_pattern"
        )

        # Stage 3: Search intent mappings
        if analysis and analysis.get("intent"):
            results["intent_mappings"] = self.search(
                query=analysis["intent"],
                k=2,
                chunk_type="intent_pattern_mapping"
            )

        logger.info(f"Multi-stage search completed: {sum(len(v) for v in results.values())} total results")
        return results

    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if metadata matches filter"""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get chunk by ID"""
        for chunk in self.chunks:
            if chunk.get("chunk_id") == chunk_id:
                return chunk
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if not self.chunks:
            return {"total_chunks": 0}

        # Count by chunk type
        type_counts = {}
        for chunk in self.chunks:
            chunk_type = chunk.get("chunk_type", "unknown")
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1

        return {
            "total_chunks": len(self.chunks),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_model": self.embedding_model_name,
            "chunk_types": type_counts
        }

