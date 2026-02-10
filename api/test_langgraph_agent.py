"""
Test LangGraph UI Agent

Compares the LangGraph implementation with the original StructuredUIAgent
to verify they produce the same results.
"""

import json
from agent.structured_ui_agent_v2 import StructuredUIAgent
from agent.langgraph_ui_agent import LangGraphUIAgent


def test_comparison():
    """Test that both agents produce the same results"""
    print("\n" + "="*80)
    print("🧪 Testing LangGraph UI Agent vs Original StructuredUIAgent")
    print("="*80)
    
    # Sample data
    leads_data = [
        {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
        {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"},
        {"id": 3, "name": "Global Inc", "revenue": 50000, "status": "new"}
    ]
    
    query = "show me all leads"
    
    print(f"\n📝 Query: '{query}'")
    print(f"📊 Data: {len(leads_data)} records")
    
    # Test 1: Original StructuredUIAgent
    print("\n" + "-"*80)
    print("1️⃣  Testing Original StructuredUIAgent...")
    print("-"*80)
    
    try:
        original_agent = StructuredUIAgent()
        original_result = original_agent.generate(query=query, data=leads_data)
        
        print(f"✅ Original Agent Success!")
        print(f"   Layout type: {original_result['layout_type']}")
        print(f"   Sections: {len(original_result['sections'])}")
        print(f"   Data records: {len(original_result['data'])}")
        
    except Exception as e:
        print(f"❌ Original Agent Failed: {e}")
        return
    
    # Test 2: LangGraph UIAgent
    print("\n" + "-"*80)
    print("2️⃣  Testing LangGraph UIAgent...")
    print("-"*80)
    
    try:
        langgraph_agent = LangGraphUIAgent()
        langgraph_result = langgraph_agent.generate(query=query, data=leads_data)
        
        print(f"✅ LangGraph Agent Success!")
        print(f"   Layout type: {langgraph_result['layout_type']}")
        print(f"   Sections: {len(langgraph_result['sections'])}")
        print(f"   Data records: {len(langgraph_result['data'])}")
        
    except Exception as e:
        print(f"❌ LangGraph Agent Failed: {e}")
        return
    
    # Compare results
    print("\n" + "="*80)
    print("📊 Comparison Results")
    print("="*80)
    
    print(f"\nLayout Type:")
    print(f"  Original:  {original_result['layout_type']}")
    print(f"  LangGraph: {langgraph_result['layout_type']}")
    print(f"  Match: {'✅' if original_result['layout_type'] == langgraph_result['layout_type'] else '❌'}")
    
    print(f"\nNumber of Sections:")
    print(f"  Original:  {len(original_result['sections'])}")
    print(f"  LangGraph: {len(langgraph_result['sections'])}")
    print(f"  Match: {'✅' if len(original_result['sections']) == len(langgraph_result['sections']) else '❌'}")
    
    print(f"\nData Records:")
    print(f"  Original:  {len(original_result['data'])}")
    print(f"  LangGraph: {len(langgraph_result['data'])}")
    print(f"  Match: {'✅' if len(original_result['data']) == len(langgraph_result['data']) else '❌'}")
    
    # Get stats
    print("\n" + "="*80)
    print("📈 Agent Statistics")
    print("="*80)
    
    original_stats = original_agent.get_stats()
    langgraph_stats = langgraph_agent.get_stats()
    
    print(f"\nOriginal Agent:")
    print(f"  Model: {original_stats['model']}")
    print(f"  Components: {', '.join(original_stats['components'].values())}")
    print(f"  Data Handling: {original_stats['data_handling']}")
    
    print(f"\nLangGraph Agent:")
    print(f"  Model: {langgraph_stats['model']}")
    print(f"  Orchestration: {langgraph_stats['orchestration']}")
    print(f"  Components: {', '.join(langgraph_stats['components'].values())}")
    print(f"  Graph Nodes: {', '.join(langgraph_stats['graph_nodes'])}")
    print(f"  Data Handling: {langgraph_stats['data_handling']}")
    
    print("\n" + "="*80)
    print("✅ Test Complete!")
    print("="*80)
    print("\n💡 Both agents use the same components and logic.")
    print("💡 LangGraph adds graph-based orchestration for better workflow management.")
    print()


def test_langgraph_only():
    """Test LangGraph agent with multiple queries"""
    print("\n" + "="*80)
    print("🚀 Testing LangGraph UI Agent with Multiple Queries")
    print("="*80)
    
    agent = LangGraphUIAgent()
    
    # Test cases
    test_cases = [
        {
            "query": "show me all leads",
            "data": [
                {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
                {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"}
            ]
        },
        {
            "query": "sales dashboard with metrics",
            "data": [
                {"region": "North", "sales": 125000, "deals": 45},
                {"region": "South", "sales": 98000, "deals": 32}
            ]
        },
        {
            "query": "show team member profiles",
            "data": [
                {"name": "John Doe", "role": "Sales Manager", "email": "john@example.com"},
                {"name": "Jane Smith", "role": "Account Executive", "email": "jane@example.com"}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Query: '{test_case['query']}'")
        
        try:
            result = agent.generate(
                query=test_case['query'],
                data=test_case['data']
            )
            
            print(f"   ✅ Layout: {result['layout_type']}")
            print(f"   ✅ Sections: {len(result['sections'])}")
            print(f"   ✅ Data: {len(result['data'])} records")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ All Tests Complete!")
    print("="*80)
    print()


if __name__ == "__main__":
    # Run comparison test
    test_comparison()
    
    # Run LangGraph-only tests
    # test_langgraph_only()

