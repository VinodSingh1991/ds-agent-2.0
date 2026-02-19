"""
Test script for Object Analyzer

Demonstrates:
1. Object Analyzer - Detects CRM object type
"""
import os
from openai import OpenAI
from agent.object_analyzer import ObjectAnalyzer


def test_object_analyzer():
    """Test Object Analyzer"""
    print("\n" + "="*80)
    print("TEST 1: Object Analyzer")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    
    analyzer = ObjectAnalyzer(client=client, keyword_confidence_threshold=0.7)
    
    test_queries = [
        "show me all leads",
        "display contacts",
        "what opportunities are in the pipeline?",
        "list all accounts",
    ]
    
    for query in test_queries:
        result = analyzer.analyze(query, use_llm_fallback=True)
        print(f"\nQuery: '{query}'")
        print(f"  Object Type: {result['object_type']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Method: {result['method']}")

def test_all_together():
    """Test all three analyzers working together"""
    print("\n" + "="*80)
    print("TEST 2: All Analyzers Together (Complete Pipeline)")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    
    object_analyzer = ObjectAnalyzer(client=client)
    
    # Sample data
    leads_data = [
        {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
        {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"},
        {"id": 3, "name": "Global Inc", "revenue": 50000, "status": "prospecting"}
    ]
    
    query = "show me all leads"
    
    print(f"\nQuery: '{query}'")
    print(f"{'─'*80}")
    
    # Step 2: Detect object type
    object_result = object_analyzer.analyze(query)
    print(f"2️⃣  Object: {object_result['object_type']} (confidence: {object_result['confidence']:.2f})")


if __name__ == "__main__":
    print("\n🚀 Two-Analyzer Test Suite")
    print("Testing hybrid approach for Object and Layout detection\n")
    
    test_object_analyzer()
    test_all_together()
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80 + "\n")

