"""
Direct test of the agent (without API)
Tests all object types directly
"""

import json
import os
from pathlib import Path
from agent.structured_ui_agent_v2 import StructuredUIAgent


def test_object(agent, query, object_name):
    """Test a single object type"""
    print(f"\n{'='*80}")
    print(f"Testing: {object_name}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    try:
        result = agent.generate(query)
        
        print(f"✅ Success!")
        print(f"   Layout Type: {result.get('layout_type')}")
        print(f"   Object Type: {result.get('metadata', {}).get('object_type')}")
        print(f"   Sections: {len(result.get('sections', []))}")
        print(f"   Data Records: {len(result.get('data', []))}")
        
        # Save result
        output_dir = Path("test_output/direct")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{object_name.lower().replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   Saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*80)
    print("🚀 Testing Disposable UI Agent (Direct - No API)")
    print("="*80)
    
    # Check environment
    print("\n📋 Checking environment...")
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment")
        print("   Please set it in .env file or environment variables")
        return
    else:
        print("✅ OPENAI_API_KEY is set")
    
    # Initialize agent
    print("\n🔧 Initializing agent...")
    try:
        agent = StructuredUIAgent()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test cases
    test_cases = [
        ("show me all leads", "lead"),
        ("display top 5 contacts", "contact"),
        ("show my deals", "deal"),
        ("list all open cases", "case"),
        ("show all accounts", "account"),
        ("display branch performance", "branch"),
        ("show product catalog", "product"),
    ]
    
    results = []
    for query, object_name in test_cases:
        success = test_object(agent, query, object_name)
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
        print("⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()

