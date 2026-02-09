"""
Test script to verify the agent works with all object types:
- Lead
- Contact
- Deal/Opportunity
- Case/Ticket
- Account/Company
- Branch/Office
- Product/Item
"""

import json
import os
from pathlib import Path
from agent.structured_ui_agent_v2 import StructuredUIAgent
from loguru import logger

# Configure logger
logger.add("logs/test_all_objects.log", rotation="10 MB")


def test_object_type(agent: StructuredUIAgent, query: str, object_name: str):
    """Test a single object type"""
    print(f"\n{'='*80}")
    print(f"Testing: {object_name}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    try:
        result = agent.generate(query)
        
        # Print summary
        print(f"✅ Success!")
        print(f"   Layout Type: {result.get('layout_type')}")
        print(f"   Sections: {len(result.get('sections', []))}")
        print(f"   Data Records: {len(result.get('data', []))}")
        print(f"   Object Type: {result.get('metadata', {}).get('object_type')}")
        
        # Save result
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"test_{object_name.lower().replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        logger.error(f"Error testing {object_name}: {e}")
        return False


def main():
    """Test all object types"""
    print("\n" + "="*80)
    print("🚀 Testing Disposable UI Agent with Multiple Object Types")
    print("="*80)
    
    # Initialize agent
    print("\nInitializing agent...")
    agent = StructuredUIAgent()
    print("✅ Agent initialized!")
    
    # Test cases for different object types
    test_cases = [
        ("show me all leads", "Lead"),
        ("display top 5 contacts", "Contact"),
        ("show my deals", "Deal/Opportunity"),
        ("list all open cases", "Case/Ticket"),
        ("show all accounts", "Account/Company"),
        ("display branch performance", "Branch/Office"),
        ("show product catalog", "Product/Item"),
        ("show case details", "Case Detail"),
        ("account dashboard with metrics", "Account Dashboard"),
        ("branch comparison table", "Branch Table"),
    ]
    
    results = []
    for query, object_name in test_cases:
        success = test_object_type(agent, query, object_name)
        results.append((object_name, success))
    
    # Summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for object_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {object_name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 All tests passed! The agent works with all object types!")
    else:
        print("⚠️  Some tests failed. Check logs for details.")


if __name__ == "__main__":
    main()

