"""
Query Normalizer

Single responsibility: Normalize user queries and extract structured information.

Uses OpenAI's JSON mode to guarantee valid QueryNormalization objects.
"""

from typing import Optional, Dict, Any
from loguru import logger

import json
try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.schemas.query_schemas import QueryNormalization


class QueryNormalizer:
    """
    Normalizes user queries using JSON mode
    
    Responsibilities:
    - Parse user query
    - Extract normalized query
    - Determine if retrieval-augmented generation is needed
    - Determine if the query is CRM-related
    """
    
    def __init__(self, client: Optional[Any] = None, model: str = "gpt-4o-mini"):
        """
        Initialize query normalizer

        Args:
            client: OpenAI client instance (optional)
            model: Model to use for analysis
        """
        self.client = client
        self.model = model

        if not self.client:
            logger.warning("QueryNormalizer initialized without OpenAI client")
        else:
            logger.info(f"Initialized QueryNormalizer with model: {model}")
    
    def normalize(
        self,
        query: str
        ) -> QueryNormalization:
        """
        Normalize query and extract structured information
        
        Args:
            query: User query (e.g., "show me top 5 leads")
            
        Returns:
            QueryNormalization with normalized_query, is_crm_related
        """
        logger.debug(f"Normalizing query: {query}")

        # Check if client is available
        if not self.client:
            logger.error("OpenAI client not available")
            raise ValueError("OpenAI client is required for query normalization. Please provide a valid OpenAI client instance.")

        # Build prompt
        prompt = self._build_prompt(query)

        # Call OpenAI with JSON mode (not strict structured outputs)
        try:
            logger.info("Calling OpenAI with JSON mode (response_format={'type': 'json_object'})")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI query normalizer. Extract structured information from user queries. Focus on determining if the query is CRM-related   . Provide clear reasoning for your choices."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )
            logger.info("OpenAI call successful")

            # Parse the JSON response and create QueryNormalization object
            response_content = completion.choices[0].message.content
            logger.debug(f"OpenAI response: {response_content}")

            layout_dict = json.loads(response_content)
            logger.debug(f"Parsed JSON: {layout_dict}")

            analysis = QueryNormalization(**layout_dict)

            logger.info(f"Query normalized: {analysis.normalized_query} / CRM: {analysis.is_crm_related}")

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {completion.choices[0].message.content if 'completion' in locals() else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"Error normalizing query: {e}")
            logger.exception("Full traceback:")
            raise
    
    def _build_prompt(self, query: str) -> str:
        """
        Build analysis prompt
        """
        prompt = f"""Analyze the following UI query and extract structured information.

        Query: "{query}"

        Your tasks:

        1. First determine whether this query is a greeting or general conversation that is **not CRM-related**.
        - If YES → set "is_crm_related": false
        - Examples of non-CRM queries include: "hi", "hello", "how are you", "what can you do", "help", "thanks"

        2. Convert the query into:
        a. A more professional English version focused on CRM intent.
            Example: "show me top 5 leads" → "show top 5 leads"
        b. A normalized version that standardizes the CRM intent.
            Example: "show me top 5 leads" → "show top 5 leads"

        You must determine the following:

        - "normalized_query": The cleaned and normalized version of the user's query
        - "is_crm_related": true or false
        - "reasoning": Clear explanation of how you reached your conclusion

        Return your answer strictly in this JSON format:

        {{
            "normalized_query": "normalized version of the user's query",
            "is_crm_related": true or false,
            "reasoning": "explanation of the analysis"
        }}

        Provide detailed reasoning for every decision.
        """
        return prompt


