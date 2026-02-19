"""
Test script for all three analyzers

Demonstrates the hybrid approach for:
1. Intent Analyzer - Detects user intent
2. Object Analyzer - Detects CRM object type
3. Layout Analyzer - Determines best layout based on data and query
"""
import os
from openai import OpenAI
from agent.layout_analyzer import LayoutAnalyzer

def test_layout_analyzer():
    """Test Layout Analyzer"""
    print("\n" + "="*80)
    print("TEST 3: Layout Analyzer")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    
    analyzer = LayoutAnalyzer(client=client, rule_confidence_threshold=0.7)
    
    # Test with different data shapes
    test_cases = [
        {
            "query": "show me all leads",
            "data": [
                {"id": 1, "name": "Acme Corp", "revenue": 75000},
                {"id": 2, "name": "TechStart", "revenue": 120000},
                {"id": 3, "name": "Global Inc", "revenue": 50000}
            ],
            "intent": "view_list"
        },
        {
            "query": "show me lead details",
            "data": [{"id": 1, "name": "Acme Corp", "revenue": 75000}],
            "intent": "view_detail"
        },
        {
            "query": "display contacts in a table",
            "data": [{"id": i, "name": f"Contact {i}"} for i in range(1, 25)],
            "intent": "view_table"
        },
    ]
    
    for test_case in test_cases:
        result = analyzer.analyze(
            query=test_case["query"],
            data=test_case["data"],
            intent=test_case["intent"],
            use_llm_fallback=True
        )
        print(f"\nQuery: '{test_case['query']}'")
        print(f"  Data: {len(test_case['data']) if test_case['data'] else 0} records")
        print(f"  Layout Type: {result['layout_type']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Method: {result['method']}")


def test_all_together():
    """Test all three analyzers working together"""
    print("\n" + "="*80)
    print("TEST 4: All Analyzers Together (Complete Pipeline)")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    
    layout_analyzer = LayoutAnalyzer(client=client)
    
    # Sample data
    leads_data = [
        {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
        {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"},
        {"id": 3, "name": "Global Inc", "revenue": 50000, "status": "prospecting"}
    ]
    
    query = "show me all leads"
    
    print(f"\nQuery: '{query}'")
    print(f"{'─'*80}")

    # Step 3: Determine layout
    layout_result = layout_analyzer.analyze(query=query, data=leads_data, intent="view_list")
    print(f"3️⃣  Layout: {layout_result['layout_type']} (confidence: {layout_result['confidence']:.2f})")


if __name__ == "__main__":
    print("\n🚀 Three-Analyzer Test Suite")
    print("Testing hybrid approach for Intent, Object, and Layout detection\n")
    
    test_layout_analyzer()
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80 + "\n")

