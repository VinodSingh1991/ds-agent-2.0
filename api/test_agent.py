"""
Test Structured UI Agent

Simple test script to verify the agent works.

Usage:
    python test_agent.py
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.structured_ui_agent import StructuredUIAgent
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def test_agent():
    """Test the structured UI agent"""
    print("=" * 60)
    print("🧪 Testing Structured UI Agent")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("📋 Checking prerequisites...")
    
    # Check if vector index exists
    index_path = Path(__file__).parent / "vector_index" / "enhanced_layouts.faiss"
    if not index_path.exists():
        print("❌ Error: Vector index not found!")
        print()
        print("Please run these commands first:")
        print("  1. python generate_chunks.py")
        print("  2. python build_vector_index.py")
        print()
        return
    
    print("✅ Vector index found")
    
    # Check if OpenAI API key is set
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set!")
        print()
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'  # Linux/Mac")
        print("  set OPENAI_API_KEY=your-key-here       # Windows")
        print()
        return
    
    print("✅ OpenAI API key found")
    print()
    
    # Initialize agent
    print("🚀 Initializing agent...")
    try:
        agent = StructuredUIAgent()
        print("✅ Agent initialized")
        print()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return
    
    # Test queries
    test_queries = [
        "show me top 5 leads with revenue > 50k",
        "display all contacts",
        "show me a dashboard of lead metrics"
    ]
    
    print("=" * 60)
    print("🧪 Running Test Queries")
    print("=" * 60)
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─' * 60}")
        print(f"Test {i}/{len(test_queries)}: {query}")
        print('─' * 60)
        
        try:
            # Generate layout
            result = agent.generate(query)
            
            # Show summary
            print(f"\n✅ Layout generated successfully!")
            print(f"\nSummary:")
            print(f"  - Layout Type: {result.get('layout_type')}")
            print(f"  - Sections: {len(result.get('sections', []))}")
            print(f"  - Data Records: {len(result.get('data', []))}")
            
            # Show first section
            if result.get('sections'):
                first_section = result['sections'][0]
                print(f"\nFirst Section:")
                print(f"  - Title: {first_section.get('title', 'N/A')}")
                print(f"  - Rows: {len(first_section.get('rows', []))}")
                
                if first_section.get('rows'):
                    first_row = first_section['rows'][0]
                    print(f"  - First Row Components: {len(first_row.get('components', []))}")
            
            # Save full result
            output_file = Path(__file__).parent / f"test_output_{i}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Full output saved to: {output_file}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.exception("Error details:")
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)
    print()
    
    # Show stats
    stats = agent.get_stats()
    print("Agent Statistics:")
    print(f"  - Model: {stats.get('model')}")
    print(f"  - Status: {stats.get('status')}")
    print(f"  - Vector Store Chunks: {stats.get('vector_store', {}).get('total_chunks', 0)}")
    print()


if __name__ == "__main__":
    test_agent()

