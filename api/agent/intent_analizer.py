"""
Intent Analyzer - Hybrid Approach

SINGLE RESPONSIBILITY: Detect user intent only (greeting, view_list, view_detail, etc.)

Uses keyword-based detection first (fast), then falls back to LLM (accurate).

Architecture:
1. Keyword matching for common patterns (greetings, common intents)
2. LLM fallback for ambiguous or complex queries
3. Confidence scoring for both approaches

NOTE: Object type and layout type detection are handled by separate analyzers.
"""
from typing import Optional, Dict, Any
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.schemas.constants import QueryIntent, INTENT_KEYWORDS


class IntentAnalyzer:
    """
    Hybrid Intent Analyzer

    SINGLE RESPONSIBILITY: Detect user intent only

    Uses a two-stage approach:
    1. Fast keyword-based detection (90% of queries)
    2. LLM fallback for complex/ambiguous queries (10% of queries)

    Responsibilities:
    - Detect user intent (greeting, view_list, view_detail, etc.)
    - Provide confidence score
    - Provide reasoning for detection method

    Does NOT handle:
    - Object type detection (see ObjectAnalyzer)
    - Layout type detection (see LayoutAnalyzer)
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "gpt-4o-2024-08-06",
        keyword_confidence_threshold: float = 0.7
    ):
        """
        Initialize Intent Analyzer

        Args:
            client: OpenAI client instance (optional, only needed for LLM fallback)
            model: Model to use for LLM fallback
            keyword_confidence_threshold: Minimum confidence to trust keyword detection
        """
        self.client = client
        self.model = model
        self.keyword_confidence_threshold = keyword_confidence_threshold

        logger.info(f"Initialized IntentAnalyzer (hybrid mode, threshold={keyword_confidence_threshold})")

    def analyze(
        self,
        query: str,
        use_llm_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze query intent using hybrid approach

        Args:
            query: User query string
            use_llm_fallback: Whether to use LLM if keyword detection has low confidence

        Returns:
            Dict with intent, confidence, method, reasoning
        """
        logger.debug(f"Analyzing intent for query: '{query}'")

        # Stage 1: Keyword-based detection
        keyword_result = self._keyword_detection(query)

        # If high confidence, return keyword result
        if keyword_result["confidence"] >= self.keyword_confidence_threshold:
            logger.info(f"Intent detected via keywords: {keyword_result['intent']} (confidence: {keyword_result['confidence']:.2f})")
            return keyword_result

        # Stage 2: LLM fallback for low confidence
        if use_llm_fallback and self.client:
            logger.debug(f"Low keyword confidence ({keyword_result['confidence']:.2f}), using LLM fallback...")
            llm_result = self._llm_detection(query)
            logger.info(f"Intent detected via LLM: {llm_result['intent']} (confidence: {llm_result['confidence']:.2f})")
            return llm_result

        # No LLM available or disabled, return keyword result anyway
        logger.warning(f"Low keyword confidence ({keyword_result['confidence']:.2f}) but LLM fallback disabled/unavailable")
        return keyword_result

    def _keyword_detection(self, query: str) -> Dict[str, Any]:
        """
        Fast keyword-based intent detection

        Args:
            query: User query string

        Returns:
            Dict with intent, confidence, method, reasoning
        """
        query_lower = query.lower().strip()

        # Detect intent
        intent_scores = {}
        for intent, keywords in INTENT_KEYWORDS.items():
            score = 0
            matched_keywords = []

            for keyword in keywords:
                if keyword in query_lower:
                    # Exact phrase match gets higher score
                    if keyword == query_lower:
                        score += 2.0
                    # Word boundary match
                    elif f" {keyword} " in f" {query_lower} ":
                        score += 1.5
                    # Starts with keyword
                    elif query_lower.startswith(keyword):
                        score += 1.2
                    # Contains keyword
                    else:
                        score += 0.8

                    matched_keywords.append(keyword)

            if score > 0:
                intent_scores[intent] = {
                    "score": score,
                    "matched_keywords": matched_keywords
                }

        # Get best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1]["score"])
            intent = best_intent[0]
            intent_data = best_intent[1]

            # Normalize confidence (0-1 scale)
            # Max score is roughly 2.0 for exact match, 5.0 for multiple matches
            confidence = min(intent_data["score"] / 3.0, 1.0)
        else:
            intent = QueryIntent.HTML_VIEW
            intent_data = {"score": 0, "matched_keywords": []}
            confidence = 0.0

        # Build reasoning
        reasoning = f"Matched keywords: {', '.join(intent_data['matched_keywords'])}" if intent_data["matched_keywords"] else "No clear keyword matches"

        return {
            "intent": intent.value,
            "confidence": confidence,
            "method": "keyword",
            "reasoning": reasoning,
            "matched_keywords": intent_data["matched_keywords"]
        }

    def _llm_detection(self, query: str) -> Dict[str, Any]:
        """
        LLM-based intent detection (fallback for ambiguous queries)

        Args:
            query: User query string

        Returns:
            Dict with intent, confidence, method, reasoning
        """
        if not self.client:
            logger.error("LLM fallback requested but OpenAI client not available")
            return {
                "intent": QueryIntent.HTML_VIEW.value,
                "confidence": 0.0,
                "method": "llm_error",
                "reasoning": "OpenAI client not available"
            }

        # Build prompt for LLM
        prompt = f"""Analyze this user query and determine the intent ONLY.

Query: "{query}"

Available Intents:
- greeting: User is greeting or saying hello
- help: User needs help or guidance
- view_list: User wants to see a list of multiple records
- view_detail: User wants to see details of a single record
- view_summary: User wants a summary or overview
- view_dashboard: User wants metrics, analytics, or KPIs
- view_table: User wants data in tabular format
- view_trends: User wants to see trends over time
- view_comparison: User wants to compare records
- view_cards: User wants card-based layout
- create: User wants to create a new record
- update: User wants to update/edit a record
- delete: User wants to delete a record
- search: User wants to search for something
- html_view: Intent is unclear, show HTML view by default

Respond in JSON format:
{{
    "intent": "the detected intent",
    "confidence": 0.95,
    "reasoning": "brief explanation of why you chose this intent"
}}"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent detection expert. Analyze user queries and return structured JSON with intent, confidence, and reasoning. Focus ONLY on intent, not object type or layout."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=150
            )

            import json
            result = json.loads(completion.choices[0].message.content)

            return {
                "intent": result.get("intent", QueryIntent.HTML_VIEW.value),
                "confidence": result.get("confidence", 0.8),
                "method": "llm",
                "reasoning": result.get("reasoning", "LLM analysis")
            }

        except Exception as e:
            logger.error(f"LLM intent detection failed: {e}")
            return {
                "intent": QueryIntent.HTML_VIEW.value,
                "confidence": 0.0,
                "method": "llm_error",
                "reasoning": f"LLM error: {str(e)}"
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get analyzer statistics

        Returns:
            Statistics about the analyzer
        """
        return {
            "analyzer": "IntentAnalyzer",
            "mode": "hybrid",
            "keyword_threshold": self.keyword_confidence_threshold,
            "llm_available": self.client is not None,
            "model": self.model if self.client else None,
            "total_intents": len(INTENT_KEYWORDS)
        }