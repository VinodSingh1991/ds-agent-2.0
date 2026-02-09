"""
Script to generate enhanced chunks for RAG

Run this script to generate all chunks from pattern metadata.

Usage:
    python generate_chunks.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.chunking.chunk_generator import ChunkGenerator
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def main():
    """Generate all chunks"""
    print("=" * 60)
    print("🚀 Enhanced Chunk Generator")
    print("=" * 60)
    print()
    
    # Initialize generator
    print("📂 Initializing chunk generator...")
    generator = ChunkGenerator()
    print()
    
    # Generate chunks
    print("⚙️  Generating chunks...")
    chunks = generator.generate_all_chunks()
    print()
    
    # Save chunks
    print("💾 Saving chunks...")
    generator.save_chunks(chunks)
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Chunk Generation Complete!")
    print("=" * 60)
    print(f"Total chunks generated: {len(chunks)}")
    print()
    
    # Breakdown by type
    chunk_types = {}
    for chunk in chunks:
        chunk_type = chunk.chunk_type
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
    
    print("Breakdown by type:")
    for chunk_type, count in chunk_types.items():
        print(f"  - {chunk_type}: {count}")
    print()
    
    # Output location
    output_path = Path(__file__).parent / "dataset" / "enhanced_chunks.json"
    print(f"📁 Chunks saved to: {output_path}")
    print()
    
    # Next steps
    print("Next steps:")
    print("  1. Review the generated chunks in dataset/enhanced_chunks.json")
    print("  2. Run: python -m core.build_vector_index (to be created)")
    print("  3. Test the agent with: python examples/test_agent.py (to be created)")
    print()


if __name__ == "__main__":
    main()

