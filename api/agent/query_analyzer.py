"""
Query Analyzer

Single responsibility: Analyze user queries and extract structured information.

Uses OpenAI's structured outputs to guarantee valid QueryAnalysis objects.
"""

from typing import Optional, Dict, Any
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.schemas.query_schemas import QueryAnalysis


class QueryAnalyzer:
    """
    Analyzes user queries using structured outputs
    
    Responsibilities:
    - Parse user query
    - Extract intent, object type, layout type
    - Identify filters, sorting, limits
    - Provide reasoning for choices
    """
    
    def __init__(self, client: OpenAI, model: str = "gpt-4o-2024-08-06"):
        """
        Initialize query analyzer
        
        Args:
            client: OpenAI client instance
            model: Model to use for analysis
        """
        self.client = client
        self.model = model
        logger.info(f"Initialized QueryAnalyzer with model: {model}")
    
    def analyze(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryAnalysis:
        """
        Analyze query and extract structured information
        
        Args:
            query: User query (e.g., "show me top 5 leads")
            context: Optional context (user preferences, etc.)
            
        Returns:
            QueryAnalysis with intent, layout_type, filters, etc.
        """
        logger.debug(f"Analyzing query: {query}")
        
        # Build prompt
        prompt = self._build_prompt(query, context)
        
        # Call OpenAI with structured output
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI query analyzer. Extract structured information from user queries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=QueryAnalysis
            )
            
            analysis = completion.choices[0].message.parsed
            logger.info(f"Query analyzed: {analysis.object_type} / {analysis.intent} / {analysis.layout_type}")
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            raise
    
    def _build_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build analysis prompt
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze this UI query and extract structured information.

Query: "{query}"

Determine:
1. What type of object/entity is being queried (e.g., "lead", "contact", "deal", "user", "product")
2. What is the user's intent:
   - view_list: Show multiple records
   - view_detail: Show single record details
   - view_dashboard: Show metrics/analytics
   - create: Create new record
   - edit: Edit existing record
   - search: Search for records
   - analyze: Analyze data
   - compare: Compare records

3. What layout type is most appropriate:
   - list: Multiple items in list format
   - detail: Single item with all details
   - dashboard: Metrics and charts
   - table: Tabular data for comparison
   - grid: Grid of cards
   - form: Input form
   - timeline: Chronological view

4. Any filters mentioned (e.g., "revenue > 50k", "status = active", "created this month")
5. Any sorting requirements (e.g., "top 5", "highest revenue", "newest first")
6. Any limit on results (e.g., "top 5" = limit 5, "first 10" = limit 10)

Provide clear reasoning for your choices."""

        if context:
            prompt += f"\n\nAdditional Context:\n{context}"
        
        return prompt

