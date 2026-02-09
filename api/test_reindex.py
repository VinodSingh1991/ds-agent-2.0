"""
Test the /reindex endpoint

This script tests the RAG reindexing endpoint.
"""

import requests
import json
from pathlib import Path


def test_reindex():
    """Test the reindex endpoint"""
    print("=" * 60)
    print("🧪 Testing /reindex Endpoint")
    print("=" * 60)
    print()
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if index exists (force=false)
    print("Test 1: Check if index exists (force=false)")
    print("-" * 60)
    
    response = requests.post(
        f"{base_url}/reindex",
        json={"force": False}
    )
    
    result = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    
    if result.get('stats'):
        print("\nStatistics:")
        stats = result['stats']
        print(f"  Total chunks: {stats.get('total_chunks')}")
        print(f"  Index size: {stats.get('index_size')}")
        print(f"  Embedding model: {stats.get('embedding_model')}")
        
        if 'chunk_types' in stats:
            print("\n  Chunk types:")
            for chunk_type, count in stats['chunk_types'].items():
                print(f"    - {chunk_type}: {count}")
    
    if result.get('execution_time_ms'):
        print(f"\nExecution time: {result['execution_time_ms']:.2f}ms")
    
    print()
    
    # Test 2: Force rebuild (if user wants)
    print("Test 2: Force rebuild")
    print("-" * 60)
    print("⚠️  This will rebuild the entire index (may take a minute)")
    
    user_input = input("Do you want to force rebuild? (y/N): ").strip().lower()
    
    if user_input == 'y':
        print("\n🔨 Rebuilding index...")
        
        response = requests.post(
            f"{base_url}/reindex",
            json={"force": True, "embedding_model": "all-MiniLM-L6-v2"}
        )
        
        result = response.json()
        print(f"\nStatus Code: {response.status_code}")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        if result.get('stats'):
            print("\nStatistics:")
            stats = result['stats']
            print(f"  Total chunks: {stats.get('total_chunks')}")
            print(f"  Index size: {stats.get('index_size')}")
            print(f"  Embedding model: {stats.get('embedding_model')}")
            
            if 'chunk_types' in stats:
                print("\n  Chunk types:")
                for chunk_type, count in stats['chunk_types'].items():
                    print(f"    - {chunk_type}: {count}")
        
        if result.get('execution_time_ms'):
            print(f"\nExecution time: {result['execution_time_ms']:.2f}ms")
        
        if result.get('error'):
            print(f"\n❌ Error: {result['error']}")
    else:
        print("Skipped force rebuild")
    
    print()
    print("=" * 60)
    print("✅ Testing Complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_reindex()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the server is running: python start_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")

