"""
Object Analyzer - Hybrid Approach

SINGLE RESPONSIBILITY: Detect CRM object type (lead, contact, opportunity, etc.)

Uses keyword-based detection first (fast), then falls back to LLM (accurate).

Architecture:
1. Keyword matching for common object types
2. LLM fallback for ambiguous or complex queries
3. Confidence scoring for both approaches
"""
from typing import Optional, Dict, Any
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.schemas.constants import ObjectType, OBJECT_TYPE_KEYWORDS


class ObjectAnalyzer:
    """
    Hybrid Object Type Analyzer

    SINGLE RESPONSIBILITY: Detect CRM object type only

    Uses a two-stage approach:
    1. Fast keyword-based detection (90% of queries)
    2. LLM fallback for complex/ambiguous queries (10% of queries)

    Responsibilities:
    - Detect object type (lead, contact, opportunity, etc.)
    - Provide confidence score
    - Provide reasoning for detection method

    Does NOT handle:
    - Intent detection (see IntentAnalyzer)
    - Layout type detection (see LayoutAnalyzer)
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "gpt-4o-2024-08-06",
        keyword_confidence_threshold: float = 0.7
    ):
        """
        Initialize Object Analyzer

        Args:
            client: OpenAI client instance (optional, only needed for LLM fallback)
            model: Model to use for LLM fallback
            keyword_confidence_threshold: Minimum confidence to trust keyword detection
        """
        self.client = client
        self.model = model
        self.keyword_confidence_threshold = keyword_confidence_threshold

        logger.info(f"Initialized ObjectAnalyzer (hybrid mode, threshold={keyword_confidence_threshold})")

    def analyze(
        self,
        query: str,
        use_llm_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze query to detect object type using hybrid approach

        Args:
            query: User query string
            use_llm_fallback: Whether to use LLM if keyword detection has low confidence

        Returns:
            Dict with object_type, confidence, method, reasoning
        """
        logger.debug(f"Analyzing object type for query: '{query}'")

        # Stage 1: Keyword-based detection
        keyword_result = self._keyword_detection(query)

        # If high confidence, return keyword result
        if keyword_result["confidence"] >= self.keyword_confidence_threshold:
            logger.info(f"Object type detected via keywords: {keyword_result['object_type']} (confidence: {keyword_result['confidence']:.2f})")
            return keyword_result

        # Stage 2: LLM fallback for low confidence
        if use_llm_fallback and self.client:
            logger.debug(f"Low keyword confidence ({keyword_result['confidence']:.2f}), using LLM fallback...")
            llm_result = self._llm_detection(query)
            logger.info(f"Object type detected via LLM: {llm_result['object_type']} (confidence: {llm_result['confidence']:.2f})")
            return llm_result

        # No LLM available or disabled, return keyword result anyway
        logger.warning(f"Low keyword confidence ({keyword_result['confidence']:.2f}) but LLM fallback disabled/unavailable")
        return keyword_result

    def _keyword_detection(self, query: str) -> Dict[str, Any]:
        """
        Fast keyword-based object type detection

        Args:
            query: User query string

        Returns:
            Dict with object_type, confidence, method, reasoning
        """
        query_lower = query.lower().strip()

        # Detect object type
        object_type = ObjectType.GENERAL
        best_score = 0.0
        matched_keywords = []

        for obj_type, keywords in OBJECT_TYPE_KEYWORDS.items():
            score = 0
            current_matches = []

            for keyword in keywords:
                if keyword in query_lower:
                    # Exact match
                    if keyword == query_lower:
                        score += 2.0
                    # Word boundary match
                    elif f" {keyword} " in f" {query_lower} ":
                        score += 1.5
                    # Starts with
                    elif query_lower.startswith(keyword):
                        score += 1.2
                    # Contains
                    else:
                        score += 0.8

                    current_matches.append(keyword)

            if score > best_score:
                best_score = score
                object_type = obj_type
                matched_keywords = current_matches

        # Normalize confidence (0-1 scale)
        confidence = min(best_score / 2.0, 1.0) if best_score > 0 else 0.0

        # Build reasoning
        reasoning = f"Matched keywords: {', '.join(matched_keywords)}" if matched_keywords else "No clear keyword matches"

        return {
            "object_type": object_type.value,
            "confidence": confidence,
            "method": "keyword",
            "reasoning": reasoning,
            "matched_keywords": matched_keywords
        }

    def _llm_detection(self, query: str) -> Dict[str, Any]:
        """
        LLM-based object type detection (fallback for ambiguous queries)

        Args:
            query: User query string

        Returns:
            Dict with object_type, confidence, method, reasoning
        """
        if not self.client:
            logger.error("LLM fallback requested but OpenAI client not available")
            return {
                "object_type": ObjectType.GENERAL.value,
                "confidence": 0.0,
                "method": "llm_error",
                "reasoning": "OpenAI client not available"
            }

        # Build prompt for LLM
        prompt = f"""Analyze this user query and determine the CRM object type ONLY.

Query: "{query}"

Available Object Types:
- lead: Potential customers, prospects
- contact: People, individuals
- opportunity: Deals, sales opportunities
- account: Companies, organizations, customers
- activity: Tasks, events, meetings
- case: Support tickets, issues
- campaign: Marketing campaigns
- product: Products, items for sale
- quote: Price quotes, quotations
- invoice: Bills, invoices
- general: Not related to any specific CRM object

Respond in JSON format:
{{
    "object_type": "the detected object type",
    "confidence": 0.95,
    "method": "llm",
    "reasoning": "brief explanation of why you chose this object type"
}}"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a CRM object type detection expert. Analyze user queries and return structured JSON with object_type, confidence, and reasoning. Focus ONLY on object type, not intent or layout."
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
                "object_type": result.get("object_type", ObjectType.GENERAL.value),
                "confidence": result.get("confidence", 0.8),
                "method": "llm",
                "reasoning": result.get("reasoning", "LLM analysis")
            }

        except Exception as e:
            logger.error(f"LLM object type detection failed: {e}")
            return {
                "object_type": ObjectType.GENERAL.value,
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
            "analyzer": "ObjectAnalyzer",
            "mode": "hybrid",
            "keyword_threshold": self.keyword_confidence_threshold,
            "llm_available": self.client is not None,
            "model": self.model if self.client else None,
            "total_object_types": len(OBJECT_TYPE_KEYWORDS)
        }

