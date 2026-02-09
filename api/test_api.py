"""
Test script for Disposable UI Agent API

Tests all endpoints with different object types
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Any


# API Configuration
API_BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Health Check: {data['status']}")
        print(f"   Agent Initialized: {data['agent_initialized']}")
        print(f"   Version: {data['version']}")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_generate(query: str, object_name: str, save_result: bool = True) -> Dict[str, Any]:
    """Test single layout generation"""
    print(f"\n📝 Testing: {object_name}")
    print(f"   Query: {query}")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json={"query": query}
        )
        response.raise_for_status()
        
        request_time = (time.time() - start_time) * 1000
        data = response.json()
        
        if data['success']:
            layout = data['layout']
            print(f"   ✅ Success!")
            print(f"   Layout Type: {layout.get('layout_type')}")
            print(f"   Object Type: {layout.get('metadata', {}).get('object_type')}")
            print(f"   Sections: {len(layout.get('sections', []))}")
            print(f"   Data Records: {len(layout.get('data', []))}")
            print(f"   API Time: {request_time:.2f}ms")
            print(f"   Agent Time: {data.get('execution_time_ms', 0):.2f}ms")
            
            # Save result
            if save_result:
                output_dir = Path("test_output/api")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir / f"{object_name.lower().replace(' ', '_')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(layout, f, indent=2, ensure_ascii=False)
                
                print(f"   Saved to: {output_file}")
            
            return data
        else:
            print(f"   ❌ Failed: {data.get('error')}")
            return data
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return {"success": False, "error": str(e)}


def test_batch_generate():
    """Test batch generation"""
    print_section("Testing Batch Generation")
    
    queries = [
        "show me all leads",
        "display contacts",
        "list all cases",
        "show accounts",
        "branch performance dashboard"
    ]
    
    print(f"Sending {len(queries)} queries in batch...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/generate-batch",
            json={"queries": queries}
        )
        response.raise_for_status()
        
        request_time = (time.time() - start_time) * 1000
        data = response.json()
        
        print(f"\n✅ Batch completed!")
        print(f"   Total: {data['total']}")
        print(f"   Successful: {data['successful']}")
        print(f"   Failed: {data['failed']}")
        print(f"   Total Time: {request_time:.2f}ms")
        print(f"   Avg Time per Query: {request_time/len(queries):.2f}ms")
        
        # Show individual results
        print(f"\n   Individual Results:")
        for i, result in enumerate(data['results']):
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {queries[i]}")
        
        return data
        
    except Exception as e:
        print(f"❌ Batch request failed: {e}")
        return None


def test_all_object_types():
    """Test all supported object types"""
    print_section("Testing All Object Types")
    
    test_cases = [
        ("show me all leads", "lead"),
        ("display top 5 contacts", "contact"),
        ("show my deals", "deal"),
        ("list all open cases", "case"),
        ("show all accounts", "account"),
        ("display branch performance", "branch"),
        ("show product catalog", "product"),
        ("case details for CASE-001", "case_detail"),
        ("account dashboard with metrics", "account_dashboard"),
        ("show low stock products", "product_inventory"),
    ]
    
    results = []
    for query, object_name in test_cases:
        result = test_generate(query, object_name)
        results.append((object_name, result['success']))
        time.sleep(0.5)  # Small delay between requests
    
    return results


def print_summary(results):
    """Print test summary"""
    print_section("Test Summary")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for object_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {object_name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 All API tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")


def main():
    """Run all API tests"""
    print("\n" + "="*80)
    print("🚀 Testing Disposable UI Agent API")
    print("="*80)
    print(f"\nAPI URL: {API_BASE_URL}")
    print("Make sure the API server is running: python api/main.py")
    print("\nWaiting for server to be ready...")
    
    # Wait for server
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!\n")
                break
        except:
            if i < max_retries - 1:
                print(f"   Waiting... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("\n❌ Server is not responding!")
                print("   Please start the server with: python api/main.py")
                return
    
    # Run tests
    test_health_check()
    
    results = test_all_object_types()
    
    test_batch_generate()
    
    print_summary(results)


if __name__ == "__main__":
    main()

