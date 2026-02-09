"""
Build Vector Index

This script builds the FAISS vector index from generated chunks.

Usage:
    python build_vector_index.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.enhanced_vector_store import EnhancedVectorStore
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def main():
    """Build vector index from chunks"""
    print("=" * 60)
    print("🚀 Enhanced Vector Index Builder")
    print("=" * 60)
    print()
    
    # Check if chunks exist
    chunks_path = Path(__file__).parent / "dataset" / "enhanced_chunks.json"
    if not chunks_path.exists():
        print("❌ Error: enhanced_chunks.json not found!")
        print()
        print("Please run 'python generate_chunks.py' first to generate chunks.")
        print()
        return
    
    # Initialize vector store
    print("📂 Initializing vector store...")
    vector_store = EnhancedVectorStore(
        embedding_model="all-MiniLM-L6-v2"  # Fast and good quality
    )
    print()
    
    # Load chunks
    print("📥 Loading chunks...")
    chunks = vector_store.load_chunks(chunks_path)
    
    if not chunks:
        print("❌ Error: No chunks loaded!")
        return
    
    print(f"✅ Loaded {len(chunks)} chunks")
    print()
    
    # Build index
    print("🔨 Building FAISS index...")
    print("   (This may take a minute...)")
    print()
    
    try:
        vector_store.build_index(chunks)
        print("✅ Index built successfully!")
        print()
    except Exception as e:
        print(f"❌ Error building index: {e}")
        print()
        print("Make sure you have installed the required packages:")
        print("  pip install faiss-cpu sentence-transformers")
        print()
        return
    
    # Save index
    print("💾 Saving index to disk...")
    vector_store.save_index()
    print()
    
    # Show statistics
    stats = vector_store.get_stats()
    print("=" * 60)
    print("✅ Vector Index Built Successfully!")
    print("=" * 60)
    print()
    print("Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Index size: {stats['index_size']} vectors")
    print(f"  Embedding model: {stats['embedding_model']}")
    print()
    print("Chunk types:")
    for chunk_type, count in stats['chunk_types'].items():
        print(f"  - {chunk_type}: {count}")
    print()
    
    # Output location
    index_path = Path(__file__).parent / "vector_index" / "enhanced_layouts.faiss"
    metadata_path = Path(__file__).parent / "vector_index" / "enhanced_layouts_metadata.pkl"
    print(f"📁 Index saved to: {index_path}")
    print(f"📁 Metadata saved to: {metadata_path}")
    print()
    
    # Test search
    print("🧪 Testing search...")
    test_query = "show me all leads"
    results = vector_store.search(test_query, k=3)
    
    if results:
        print(f"✅ Search test successful! Found {len(results)} results for '{test_query}'")
        print()
        print("Top result:")
        top_result = results[0]
        print(f"  - Chunk ID: {top_result['chunk_id']}")
        print(f"  - Chunk Type: {top_result['chunk_type']}")
        print(f"  - Score: {top_result['score']:.4f}")
        print()
    else:
        print("⚠️  Search test returned no results")
        print()
    
    # Next steps
    print("Next steps:")
    print("  1. Vector index is ready to use!")
    print("  2. Implement the StructuredUIAgent (Step 4)")
    print("  3. Test with: python examples/test_agent.py (to be created)")
    print()


if __name__ == "__main__":
    main()

