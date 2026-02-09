"""
Structured UI Agent (Refactored)

Main orchestrator that coordinates single-responsibility components.

Architecture:
- QueryAnalyzer: Analyzes user queries
- CandidateRetriever: Retrieves candidate layouts from vector store
- LayoutGenerator: Generates final layout

Data is provided from outside - this agent ONLY generates layouts.

This follows SOLID principles with clear separation of concerns.
"""

import os
from typing import Dict, Any, List, Optional
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.query_analyzer import QueryAnalyzer
from agent.candidate_retriever import CandidateRetriever
from agent.layout_generator import LayoutGenerator
from core.enhanced_vector_store import EnhancedVectorStore


class StructuredUIAgent:
    """
    Structured UI Agent (Refactored)

    Orchestrates the layout generation pipeline using single-responsibility components.

    Components:
    - QueryAnalyzer: Analyzes queries
    - CandidateRetriever: Retrieves candidates
    - LayoutGenerator: Generates layouts

    Data is provided from outside - this agent ONLY generates layouts.

    Responsibilities:
    - Initialize components
    - Coordinate pipeline execution
    - Handle errors
    - Provide statistics
    """

    def __init__(
        self,
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY"),
        model: str = "gpt-4o-2024-08-06",
        vector_store: Optional[EnhancedVectorStore] = None
    ):
        """
        Initialize Structured UI Agent

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: OpenAI model with structured output support
            vector_store: Enhanced vector store instance
        """
        if OpenAI is None:
            raise ImportError("OpenAI not installed. Install with: pip install openai>=1.12.0")

        # Get API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter.")

        self.model = model

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Initialize or load vector store
        if vector_store is None:
            logger.info("Loading vector store...")
            self.vector_store = EnhancedVectorStore()
            if not self.vector_store.load_index():
                logger.warning("Vector store not loaded. Run 'python build_vector_index.py' first.")
        else:
            self.vector_store = vector_store

        # Initialize components
        self.query_analyzer = QueryAnalyzer(client=self.client, model=model)
        self.candidate_retriever = CandidateRetriever(vector_store=self.vector_store)
        self.layout_generator = LayoutGenerator(client=self.client, model=model)

        logger.info(f"Initialized StructuredUIAgent (v2) with model: {model}")
    
    def generate(
        self,
        query: str,
        data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate UI layout from query and data

        This is the main entry point that orchestrates the entire pipeline.

        Args:
            query: User query (e.g., "show me top 5 leads")
            data: Data to bind to layout (REQUIRED - must be provided from outside)
            context: Optional context (user preferences, etc.)

        Returns:
            Complete layout response with sections, rows, components, and data

        Example:
            agent = StructuredUIAgent()

            # You provide the data
            leads_data = [
                {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
                {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"}
            ]

            # Agent generates layout
            layout = agent.generate(
                query="show me all leads",
                data=leads_data
            )
        """
        logger.info(f"Generating layout for query: {query}")

        if not data:
            raise ValueError("Data is required. Please provide data from your application.")

        try:
            # Step 1: Analyze query
            logger.debug("Step 1: Analyzing query...")
            analysis = self.query_analyzer.analyze(query, context)

            # Step 2: Get candidate layouts from RAG
            logger.debug("Step 2: Retrieving candidate layouts...")
            candidates = self.candidate_retriever.retrieve(query, analysis, k=5)

            # Step 3: Generate layout using structured output
            logger.debug("Step 3: Generating layout with provided data...")
            layout = self.layout_generator.generate(
                query=query,
                analysis=analysis,
                candidates=candidates,
                data=data,
                context=context
            )

            # Convert to dict
            result = layout.model_dump()

            logger.info("Layout generation complete")
            return result

        except Exception as e:
            logger.error(f"Error generating layout: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics

        Returns:
            Statistics about the agent and its components
        """
        vector_stats = self.vector_store.get_stats() if self.vector_store else {}

        return {
            "model": self.model,
            "components": {
                "query_analyzer": "QueryAnalyzer",
                "candidate_retriever": "CandidateRetriever",
                "layout_generator": "LayoutGenerator"
            },
            "data_handling": "external",
            "vector_store": vector_stats,
            "status": "ready"
        }

