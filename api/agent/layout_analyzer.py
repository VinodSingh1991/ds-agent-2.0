"""
Layout Analyzer - Hybrid Approach

SINGLE RESPONSIBILITY: Determine best layout type based on data shape and query

Uses data analysis first (fast), then falls back to LLM (accurate).

Architecture:
1. Data shape analysis (record count, field types, structure)
2. Query keyword matching for layout hints
3. LLM fallback for complex decisions
4. Confidence scoring for both approaches
"""
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.schemas.constants import LayoutType, LAYOUT_KEYWORDS


class LayoutAnalyzer:
    """
    Hybrid Layout Type Analyzer

    SINGLE RESPONSIBILITY: Determine best layout type

    Uses a multi-stage approach:
    1. Data shape analysis (record count, field types)
    2. Query keyword matching
    3. LLM fallback for complex decisions

    Responsibilities:
    - Analyze data shape (count, fields, types)
    - Detect layout hints in query
    - Recommend best layout type
    - Provide confidence score

    Does NOT handle:
    - Intent detection (see IntentAnalyzer)
    - Object type detection (see ObjectAnalyzer)
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "gpt-4o-2024-08-06",
        rule_confidence_threshold: float = 0.7
    ):
        """
        Initialize Layout Analyzer

        Args:
            client: OpenAI client instance (optional, only needed for LLM fallback)
            model: Model to use for LLM fallback
            rule_confidence_threshold: Minimum confidence to trust rule-based detection
        """
        self.client = client
        self.model = model
        self.rule_confidence_threshold = rule_confidence_threshold

        logger.info(f"Initialized LayoutAnalyzer (hybrid mode, threshold={rule_confidence_threshold})")

    def analyze(
        self,
        query: str,
        data: Optional[List[Dict[str, Any]]] = None,
        intent: Optional[str] = None,
        use_llm_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze query and data to determine best layout type

        Args:
            query: User query string
            data: Optional data to analyze shape
            intent: Optional detected intent (helps with layout selection)
            use_llm_fallback: Whether to use LLM if rule-based detection has low confidence

        Returns:
            Dict with layout_type, confidence, method, reasoning
        """
        logger.debug(f"Analyzing layout type for query: '{query}' with {len(data) if data else 0} records")

        # Stage 1: Rule-based detection (data shape + query keywords)
        rule_result = self._rule_based_detection(query, data, intent)

        # If high confidence, return rule result
        if rule_result["confidence"] >= self.rule_confidence_threshold:
            logger.info(f"Layout type detected via rules: {rule_result['layout_type']} (confidence: {rule_result['confidence']:.2f})")
            return rule_result

        # Stage 2: LLM fallback for low confidence
        if use_llm_fallback and self.client:
            logger.debug(f"Low rule confidence ({rule_result['confidence']:.2f}), using LLM fallback...")
            llm_result = self._llm_detection(query, data, intent)
            logger.info(f"Layout type detected via LLM: {llm_result['layout_type']} (confidence: {llm_result['confidence']:.2f})")
            return llm_result

        # No LLM available or disabled, return rule result anyway
        logger.warning(f"Low rule confidence ({rule_result['confidence']:.2f}) but LLM fallback disabled/unavailable")
        return rule_result

    def _analyze_data_shape(self, data: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Analyze data shape to infer layout preferences

        Args:
            data: Data to analyze

        Returns:
            Dict with data characteristics
        """
        if not data:
            return {
                "record_count": 0,
                "has_data": False,
                "field_count": 0,
                "has_numeric_fields": False,
                "has_text_fields": False,
                "has_nested_data": False
            }

        record_count = len(data)
        first_record = data[0] if data else {}
        field_count = len(first_record.keys()) if first_record else 0

        # Analyze field types
        has_numeric = False
        has_text = False
        has_nested = False

        for key, value in first_record.items():
            if isinstance(value, (int, float)):
                has_numeric = True
            elif isinstance(value, str):
                has_text = True
            elif isinstance(value, (dict, list)):
                has_nested = True

        return {
            "record_count": record_count,
            "has_data": True,
            "field_count": field_count,
            "has_numeric_fields": has_numeric,
            "has_text_fields": has_text,
            "has_nested_data": has_nested
        }



    def _rule_based_detection(
        self,
        query: str,
        data: Optional[List[Dict[str, Any]]],
        intent: Optional[str]
    ) -> Dict[str, Any]:
        """
        Rule-based layout detection using data shape + query keywords

        Args:
            query: User query string
            data: Optional data to analyze
            intent: Optional detected intent

        Returns:
            Dict with layout_type, confidence, method, reasoning
        """
        query_lower = query.lower().strip()

        # Analyze data shape
        data_shape = self._analyze_data_shape(data)

        # Default layout and confidence
        layout_type = LayoutType.DETAIL
        confidence = 0.5
        reasoning_parts = []

        # Rule 1: No data -> EMPTY layout
        if not data_shape["has_data"]:
            layout_type = LayoutType.DETAIL  # Default to detail for empty state
            confidence = 0.9
            reasoning_parts.append("No data provided, using default detail layout")

        # Rule 2: Single record -> DETAIL or SUMMARY
        elif data_shape["record_count"] == 1:
            layout_type = LayoutType.DETAIL
            confidence = 0.85
            reasoning_parts.append("Single record detected, using detail layout")

        # Rule 3: Small dataset (2-9 records) -> LIST or CARD
        elif 2 <= data_shape["record_count"] < 10:
            layout_type = LayoutType.LIST
            confidence = 0.8
            reasoning_parts.append(f"{data_shape['record_count']} records, using list layout")

        # Rule 4: Medium dataset (10-50 records) -> TABLE
        elif 10 <= data_shape["record_count"] <= 50:
            layout_type = LayoutType.TABLE
            confidence = 0.85
            reasoning_parts.append(f"{data_shape['record_count']} records, using table layout")

        # Rule 5: Large dataset (>50 records) -> TABLE
        elif data_shape["record_count"] > 50:
            layout_type = LayoutType.TABLE
            confidence = 0.9
            reasoning_parts.append(f"{data_shape['record_count']} records (large dataset), using table layout")

        # Rule 6: Intent-based overrides
        if intent == "view_dashboard":
            layout_type = LayoutType.COMPOSITE
            confidence = 0.9
            reasoning_parts.append("Dashboard intent detected")
        elif intent == "view_summary":
            layout_type = LayoutType.SUMMARY
            confidence = 0.9
            reasoning_parts.append("Summary intent detected")
        elif intent == "view_detail":
            layout_type = LayoutType.DETAIL
            confidence = 0.9
            reasoning_parts.append("Detail intent detected")
        elif intent == "view_table":
            layout_type = LayoutType.TABLE
            confidence = 0.9
            reasoning_parts.append("Table intent detected")

        # Rule 7: Query keyword matching (can override data-based rules)
        keyword_scores = {}
        for layout, keywords in LAYOUT_KEYWORDS.items():
            score = 0
            matched = []

            for keyword in keywords:
                if keyword in query_lower:
                    if keyword == query_lower:
                        score += 2.0
                    elif f" {keyword} " in f" {query_lower} ":
                        score += 1.5
                    elif query_lower.startswith(keyword):
                        score += 1.2
                    else:
                        score += 0.8
                    matched.append(keyword)

            if score > 0:
                keyword_scores[layout] = {"score": score, "matched": matched}

        # If strong keyword match, override data-based layout
        if keyword_scores:
            best_keyword_layout = max(keyword_scores.items(), key=lambda x: x[1]["score"])
            keyword_confidence = min(best_keyword_layout[1]["score"] / 2.0, 1.0)

            if keyword_confidence > confidence:
                layout_type = best_keyword_layout[0]
                confidence = keyword_confidence
                reasoning_parts.append(f"Query keywords matched: {', '.join(best_keyword_layout[1]['matched'])}")

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "Default layout selection"

        return {
            "layout_type": layout_type.value,
            "confidence": confidence,
            "method": "rule_based",
            "reasoning": reasoning,
            "data_shape": data_shape
        }

    def _llm_detection(
        self,
        query: str,
        data: Optional[List[Dict[str, Any]]],
        intent: Optional[str]
    ) -> Dict[str, Any]:
        """
        LLM-based layout detection (fallback for complex decisions)

        Args:
            query: User query string
            data: Optional data to analyze
            intent: Optional detected intent

        Returns:
            Dict with layout_type, confidence, method, reasoning
        """
        if not self.client:
            logger.error("LLM fallback requested but OpenAI client not available")
            return {
                "layout_type": LayoutType.LIST.value,
                "confidence": 0.0,
                "method": "llm_error",
                "reasoning": "OpenAI client not available"
            }

        # Analyze data shape
        data_shape = self._analyze_data_shape(data)

        # Build prompt for LLM
        prompt = f"""Analyze this query and data characteristics to determine the best layout type.

Query: "{query}"
Intent: {intent or "unknown"}

Data Characteristics:
- Record count: {data_shape["record_count"]}
- Has data: {data_shape["has_data"]}
- Field count: {data_shape["field_count"]}
- Has numeric fields: {data_shape["has_numeric_fields"]}
- Has text fields: {data_shape["has_text_fields"]}
- Has nested data: {data_shape["has_nested_data"]}

Available Layout Types:
- list: Simple list of items (good for 2-10 records)
- table: Tabular data grid (good for 10+ records, many fields)
- detail: Single record detail view (good for 1 record)
- card: Card-based layout (good for visual data)
- summary: Summary/overview (good for aggregated data)
- kpi: Key metrics display (good for numeric data, dashboards)
- insights: Analysis and insights (good for trends, patterns)
- chart: Charts and graphs (good for numeric data, trends)
- timeline: Timeline view (good for chronological data)
- composite: Dashboard with multiple sections (good for complex views)

Respond in JSON format:
{{
    "layout_type": "the best layout type",
    "confidence": 0.95,
    "reasoning": "brief explanation of why you chose this layout"
}}"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI/UX expert specializing in data visualization. Analyze queries and data characteristics to recommend the best layout type. Focus on user intent and data shape."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=200
            )

            import json
            result = json.loads(completion.choices[0].message.content)

            return {
                "layout_type": result.get("layout_type", LayoutType.LIST.value),
                "confidence": result.get("confidence", 0.8),
                "method": "llm",
                "reasoning": result.get("reasoning", "LLM analysis"),
                "data_shape": data_shape
            }

        except Exception as e:
            logger.error(f"LLM layout detection failed: {e}")
            return {
                "layout_type": LayoutType.LIST.value,
                "confidence": 0.0,
                "method": "llm_error",
                "reasoning": f"LLM error: {str(e)}",
                "data_shape": data_shape
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get analyzer statistics

        Returns:
            Statistics about the analyzer
        """
        return {
            "analyzer": "LayoutAnalyzer",
            "mode": "hybrid",
            "rule_threshold": self.rule_confidence_threshold,
            "llm_available": self.client is not None,
            "model": self.model if self.client else None,
            "total_layout_types": len(LAYOUT_KEYWORDS)
        }