"""
Example: How to use the Disposable UI Agent with external data

This shows the NEW way to use the agent where YOU provide the data.
"""

import json
from agent.structured_ui_agent_v2 import StructuredUIAgent


def example_1_simple_usage():
    """Example 1: Simple usage with hardcoded data"""
    print("\n" + "="*80)
    print("Example 1: Simple Usage")
    print("="*80)
    
    # Initialize agent
    agent = StructuredUIAgent()
    
    # YOU provide the data (from your database, API, etc.)
    leads_data = [
        {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
        {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"},
        {"id": 3, "name": "Global Inc", "revenue": 50000, "status": "new"}
    ]
    
    # Agent generates layout
    layout = agent.generate(
        query="show me all leads",
        data=leads_data
    )
    
    print(f"✅ Generated layout with {len(layout['data'])} records")
    print(f"   Layout type: {layout['layout_type']}")
    print(f"   Sections: {len(layout['sections'])}")


def example_2_from_database():
    """Example 2: Fetching data from a database (simulated)"""
    print("\n" + "="*80)
    print("Example 2: With Database")
    print("="*80)
    
    # Simulate database query
    def fetch_cases_from_database(status=None):
        """Your database query function"""
        # In real app, this would be: db.query(Case).filter_by(status=status).all()
        all_cases = [
            {"id": 1, "case_number": "CASE-001", "subject": "Login Issue", "priority": "high", "status": "open"},
            {"id": 2, "case_number": "CASE-002", "subject": "Payment Failed", "priority": "critical", "status": "open"},
            {"id": 3, "case_number": "CASE-003", "subject": "Feature Request", "priority": "low", "status": "closed"}
        ]
        
        if status:
            return [c for c in all_cases if c["status"] == status]
        return all_cases
    
    # Initialize agent
    agent = StructuredUIAgent()
    
    # Fetch data from your database
    cases_data = fetch_cases_from_database(status="open")
    
    # Generate layout
    layout = agent.generate(
        query="show all open cases",
        data=cases_data
    )
    
    print(f"✅ Generated layout with {len(layout['data'])} open cases")


def example_3_from_api():
    """Example 3: Fetching data from an API (simulated)"""
    print("\n" + "="*80)
    print("Example 3: With External API")
    print("="*80)
    
    # Simulate API call
    def fetch_products_from_api():
        """Your API call function"""
        # In real app: requests.get("https://api.example.com/products").json()
        return [
            {"id": 1, "name": "Laptop Pro", "price": 1299, "stock": 45, "category": "Electronics"},
            {"id": 2, "name": "Wireless Mouse", "price": 29, "stock": 120, "category": "Accessories"},
            {"id": 3, "name": "USB-C Cable", "price": 15, "stock": 8, "category": "Accessories"}
        ]
    
    # Initialize agent
    agent = StructuredUIAgent()
    
    # Fetch data from API
    products_data = fetch_products_from_api()
    
    # Generate layout
    layout = agent.generate(
        query="show product catalog",
        data=products_data
    )
    
    print(f"✅ Generated layout with {len(layout['data'])} products")


def example_4_with_filtering():
    """Example 4: Filtering data before passing to agent"""
    print("\n" + "="*80)
    print("Example 4: With Data Filtering")
    print("="*80)
    
    # Initialize agent
    agent = StructuredUIAgent()
    
    # Get all accounts
    all_accounts = [
        {"id": 1, "name": "Acme Corp", "revenue": 500000, "tier": "enterprise", "industry": "Technology"},
        {"id": 2, "name": "Small Shop", "revenue": 50000, "tier": "basic", "industry": "Retail"},
        {"id": 3, "name": "MegaCorp", "revenue": 2000000, "tier": "enterprise", "industry": "Finance"},
        {"id": 4, "name": "StartupXYZ", "revenue": 100000, "tier": "professional", "industry": "Technology"}
    ]
    
    # Filter for enterprise accounts only
    enterprise_accounts = [a for a in all_accounts if a["tier"] == "enterprise"]
    
    # Generate layout
    layout = agent.generate(
        query="show enterprise accounts",
        data=enterprise_accounts
    )
    
    print(f"✅ Generated layout with {len(layout['data'])} enterprise accounts")


def example_5_with_context():
    """Example 5: Using context for personalization"""
    print("\n" + "="*80)
    print("Example 5: With User Context")
    print("="*80)
    
    # Initialize agent
    agent = StructuredUIAgent()
    
    # Your data
    branches_data = [
        {"id": 1, "name": "New York HQ", "revenue": 1500000, "region": "East"},
        {"id": 2, "name": "San Francisco", "revenue": 1200000, "region": "West"},
        {"id": 3, "name": "Chicago", "revenue": 800000, "region": "Central"}
    ]
    
    # User context (preferences, permissions, etc.)
    user_context = {
        "user_id": "123",
        "role": "manager",
        "region": "West",
        "preferences": {"theme": "dark", "density": "compact"}
    }
    
    # Generate layout with context
    layout = agent.generate(
        query="show branch performance",
        data=branches_data,
        context=user_context
    )
    
    print(f"✅ Generated personalized layout for user {user_context['user_id']}")


def example_6_error_handling():
    """Example 6: Proper error handling"""
    print("\n" + "="*80)
    print("Example 6: Error Handling")
    print("="*80)
    
    agent = StructuredUIAgent()
    
    # Try with empty data
    try:
        layout = agent.generate(
            query="show me leads",
            data=[]  # Empty data
        )
    except ValueError as e:
        print(f"❌ Error (expected): {e}")
    
    # Try with valid data
    try:
        layout = agent.generate(
            query="show me leads",
            data=[{"id": 1, "name": "Test Lead"}]
        )
        print(f"✅ Success with valid data")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Disposable UI Agent - Usage Examples")
    print("="*80)
    print("\nThese examples show how to use the agent with external data.")
    print("The agent does NOT fetch data - YOU provide it!")
    
    # Run examples
    example_1_simple_usage()
    example_2_from_database()
    example_3_from_api()
    example_4_with_filtering()
    example_5_with_context()
    example_6_error_handling()
    
    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80)
    print("\nKey Takeaway: Always provide data to the agent.")
    print("The agent's job is ONLY to generate layouts, not fetch data.")
    print("="*80 + "\n")

