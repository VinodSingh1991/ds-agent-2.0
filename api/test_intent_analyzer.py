"""
Test script for Hybrid Intent Analyzer

Demonstrates:
1. Keyword-based detection (fast)
2. LLM fallback (accurate)
3. Confidence scoring
"""
import os
from loguru import logger
from openai import OpenAI

from agent.intent_analizer import IntentAnalyzer


def test_keyword_detection():
    """Test keyword-based detection (no LLM needed)"""
    print("\n" + "="*80)
    print("TEST 1: Keyword-Based Detection (Fast)")
    print("="*80)
    
    # Initialize without OpenAI client (keyword-only mode)
    analyzer = IntentAnalyzer(client=None)
    
    test_queries = [
        "hello",
        "hi there",
        "show me all leads",
        "display contacts",
        "dashboard for opportunities",
        "table of accounts",
        "summary of this lead",
        "compare these deals",
        "help me",
        "what can you do",
        "show me all leads in a table",
        "show me all leads in a card view",
        "show me all leads in a list view",
        "show me all leads in a summary view",
        "show me all leads in a dashboard"
    ]
    
    for query in test_queries:
        result = analyzer.analyze(query, use_llm_fallback=False)
        print(f"\nQuery: '{query}'")
        print(f"  Intent: {result['intent']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Method: {result['method']}")
        print(f"  Reasoning: {result['reasoning']}")


def test_llm_fallback():
    """Test LLM fallback for ambiguous queries"""
    print("\n" + "="*80)
    print("TEST 2: LLM Fallback (Accurate)")
    print("="*80)
    
    # Initialize with OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set, skipping LLM tests")
        return
    
    client = OpenAI(api_key=api_key)
    analyzer = IntentAnalyzer(client=client, keyword_confidence_threshold=0.7)
    
    # Ambiguous queries that need LLM
    test_queries = [
        "I need to see the performance metrics",
        "Can you pull up the recent activity?",
        "What's the status on our pipeline?",
        "Give me an overview of Q4 results",
        "I want to analyze customer engagement"
    ]
    
    for query in test_queries:
        result = analyzer.analyze(query, use_llm_fallback=True)
        print(f"\nQuery: '{query}'")
        print(f"  Intent: {result['intent']}")
        print(f"  Object: {result['object_type']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Method: {result['method']}")
        print(f"  Reasoning: {result['reasoning']}")


def test_hybrid_mode():
    """Test hybrid mode (keyword first, LLM fallback)"""
    print("\n" + "="*80)
    print("TEST 3: Hybrid Mode (Best of Both)")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set, using keyword-only mode")
        client = None
    else:
        client = OpenAI(api_key=api_key)
    
    analyzer = IntentAnalyzer(client=client, keyword_confidence_threshold=0.7)
    
    test_queries = [
        # Clear queries (keyword detection)
        "hello",
        "show me all leads",
        
        # Ambiguous queries (LLM fallback)
        "I need insights on our sales performance",
        "What's happening with our customers?",
        
        # Edge cases
        "leads",  # Just object type
        "show",   # Just action
    ]
    
    for query in test_queries:
        result = analyzer.analyze(query, use_llm_fallback=True)
        print(f"\nQuery: '{query}'")
        print(f"  Intent: {result['intent']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Method: {result['method']} {'✓ (fast)' if result['method'] == 'keyword' else '⚡ (accurate)'}")
        print(f"  Reasoning: {result['reasoning']}")


def test_stats():
    """Test analyzer statistics"""
    print("\n" + "="*80)
    print("TEST 4: Analyzer Statistics")
    print("="*80)
    
    analyzer = IntentAnalyzer(client=None)
    stats = analyzer.get_stats()
    
    print(f"\nAnalyzer Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    logger.info("Starting Intent Analyzer Tests...")
    
    # Run tests
    test_keyword_detection()
    test_llm_fallback()
    test_hybrid_mode()
    test_stats()
    
    print("\n" + "="*80)
    print("✅ All tests complete!")
    print("="*80)

