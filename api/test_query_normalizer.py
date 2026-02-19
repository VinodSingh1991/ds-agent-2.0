"""
Test script for Query Normalizer

Demonstrates:
1. Query Normalizer - Normalizes queries and determines if RAG is needed
"""
import os
from openai import OpenAI
from agent.query_normalizer import QueryNormalizer

# Try to load from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use environment variables directly


def test_query_normalizer():
    """Test Query Normalizer"""
    print("\n" + "="*80)
    print("TEST 1: Query Normalizer")
    print("="*80)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set. Please set it to run this test.")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        return

    client = OpenAI(api_key=api_key)
    normalizer = QueryNormalizer(client=client)

    test_queries = [
        "show me top 5 leads with revenue > 50k",
        "hello",
        "what can you do",
        "display all contacts",
        "I need a dashboard of opportunities"
    ]

    for query in test_queries:
        try:
            result = normalizer.normalize(query)

            print(f"\nQuery: '{query}'")
            print(f"  Normalized Query: {result.normalized_query}")
            print(f"  CRM Related: {result.is_crm_related}")
            print(f"  Reasoning: {result.reasoning}")
        except Exception as e:
            print(f"\nQuery: '{query}'")
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("\n🚀 Query Normalizer Test")
    test_query_normalizer()
