"""
LangGraph UI Agent

Converts the StructuredUIAgent to use LangGraph while maintaining the exact same logic.

Architecture:
- Same 3-step pipeline: QueryAnalyzer → CandidateRetriever → LayoutGenerator
- Uses LangGraph StateGraph for orchestration
- Maintains all existing functionality

This is a drop-in replacement for StructuredUIAgent with graph-based workflow.
"""

import os
from typing import Dict, Any, List, Optional, TypedDict
from xml.parsers.expat import model
from loguru import logger

from agent.intent_analizer import IntentAnalyzer
from agent.layout_analyzer import LayoutAnalyzer
from agent.query_normalizer import QueryNormalizer

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    logger.warning("LangGraph not installed. Install with: pip install langgraph")
    StateGraph = None
    END = None

from agent.object_analyzer import ObjectAnalyzer
from agent.query_analyzer import QueryAnalyzer
from agent.candidate_retriever import CandidateRetriever
from agent.layout_generator import LayoutGenerator
from agent.schemas.layout_schemas import LayoutResponse
from core.enhanced_vector_store import EnhancedVectorStore


# Define the state that flows through the graph
class AgentState(TypedDict):
    """State that flows through the LangGraph pipeline"""
    # Input
    query: str
    #step 1 output
    normalized_query: Optional[str]
    is_crm_related: Optional[bool]
    reasoning: Optional[str]

    #step 2 output
    intent: Optional[str]
    #step 3 output
    layout_type: Optional[str]

    #step 4 output
    object_type: Optional[str]
    confidence: Optional[float]

    # Input
    data: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]]
    
    # # Step 1 output
    #analysis: Optional[QueryAnalysis]
    
    # # Step 2 output
    candidates: Optional[List[Dict[str, Any]]]
    
    # # Step 3 output
    layout: Optional[LayoutResponse]
    
    # Final output
    result: Optional[Dict[str, Any]]


class LangGraphUIAgent:
    """
    LangGraph UI Agent
    
    Same logic as StructuredUIAgent but using LangGraph for orchestration.
    
    Graph Flow:
    START → analyze_query → retrieve_candidates → generate_layout → END
    
    Components (same as before):
    - QueryAnalyzer: Analyzes queries
    - CandidateRetriever: Retrieves candidates
    - LayoutGenerator: Generates layouts
    """
    
    def __init__(
        self,
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY"),
        model: str = "gpt-4o-2024-08-06",
        vector_store: Optional[EnhancedVectorStore] = None
    ):
        """
        Initialize LangGraph UI Agent
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: OpenAI model with structured output support
            vector_store: Enhanced vector store instance
        """
        if OpenAI is None:
            raise ImportError("OpenAI not installed. Install with: pip install openai>=1.12.0")
        
        if StateGraph is None:
            raise ImportError("LangGraph not installed. Install with: pip install langgraph")
        
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
        
        # Initialize components (same as before)
        self.query_normalizer = QueryNormalizer(client=self.client, model=model)
        self.object_analyzer = ObjectAnalyzer(client=self.client, model=model)
        self.layout_analyzer = LayoutAnalyzer(client=self.client, model=model)
        self.intent_analyzer = IntentAnalyzer(client=self.client, model=model)

        self.candidate_retriever = CandidateRetriever(vector_store=self.vector_store)
        self.layout_generator = LayoutGenerator(client=self.client, model=model)
        
        
        # Build the LangGraph
        self.graph = self._build_graph()
        
        logger.info(f"Initialized LangGraphUIAgent with model: {model}")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow

        Flow:
        START → normalize_query → analyze_intent → analyze_layout → analyze_object → [route]
                                                                                        ↓
                                                                    greeting → handle_greeting → END
                                                                    crm_query → retrieve_candidates → generate_layout → END

        Returns:
            Compiled StateGraph
        """
        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes (each wraps one of our existing components)
        workflow.add_node("normalize_query", self._normalize_query_node)
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("analyze_layout", self._analyze_layout_node)
        workflow.add_node("analyze_object", self._analyze_object_node)
        workflow.add_node("handle_greeting", self._handle_greeting_node)
        workflow.add_node("retrieve_candidates", self._retrieve_candidates_node)
        workflow.add_node("generate_layout", self._generate_layout_node)

        # Define the flow
        workflow.set_entry_point("normalize_query")

        # Linear flow through analyzers
        workflow.add_edge("normalize_query", "analyze_intent")
        workflow.add_edge("analyze_intent", "analyze_layout")
        workflow.add_edge("analyze_layout", "analyze_object")

        # After object analysis, route based on intent
        workflow.add_conditional_edges(
            "analyze_object",
            self._route_after_analysis,
            {
                "greeting": "handle_greeting",
                "crm_query": "retrieve_candidates"
            }
        )

        # Greeting path: handle_greeting → END
        workflow.add_edge("handle_greeting", END)

        # CRM query path: retrieve_candidates → generate_layout → END
        workflow.add_edge("retrieve_candidates", "generate_layout")
        workflow.add_edge("generate_layout", END)

        # Compile the graph
        return workflow.compile()

    def _normalize_query_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Normalize query

        Wraps QueryNormalizer.normalize()

        Args:
            state: Current state

        Returns:
            Updated state with normalized query
        """
        logger.debug("Node 1: Normalizing query...")
        normalization = self.query_normalizer.normalize(
            query=state["query"]
        )
        state["normalized_query"] = normalization.normalized_query
        state["is_crm_related"] = normalization.is_crm_related
        state["reasoning"] = normalization.reasoning
        return state
    
    def _analyze_intent_node(self, state: AgentState) -> AgentState:
        """Node 2: Analyze intent

        Wraps IntentAnalyzer.analyze()

        Args:
            state: Current state

        Returns:
            Updated state with intent
        """        
        logger.debug("Node 2: Analyzing intent...")
        intent = self.intent_analyzer.analyze(
            query=state["normalized_query"],
            use_llm_fallback=True
        )
        state["intent"] = intent.get("intent")
        return state
    
    def _analyze_layout_node(self, state: AgentState) -> AgentState:
        """Node 3: Analyze layout type

        Wraps LayoutAnalyzer.analyze()

        Args:
            state: Current state

        Returns:
            Updated state with layout type
        """        
        logger.debug("Node 3: Analyzing layout type...")
        layout_type = self.layout_analyzer.analyze(
            query=state["normalized_query"],
            intent=state.get("intent"),
            use_llm_fallback=True,
            data=state["data"]
        )
        state["layout_type"] = layout_type.get("layout_type")
        return state
    
    def _analyze_object_node(self, state: AgentState) -> AgentState:
        """Node 4: Analyze object type
        
        Wraps ObjectAnalyzer.analyze()

        Args:
            state: Current state
        
        Returns:
            Updated state with object type
        """
        logger.debug("Node 4: Analyzing object type...")
        object_info = self.object_analyzer.analyze(
            query=state["normalized_query"],
            use_llm_fallback=True
        )
        state["object_type"] = object_info.get("object_type")
        state["confidence"] = object_info.get("confidence")
        return state

    def _route_after_analysis(self, state: AgentState) -> str:
        """
        Route based on query analysis

        Args:
            state: Current state with analysis

        Returns:
            Next node name ("greeting" or "crm_query")
        """
        if state["intent"] == "greeting":
            logger.info("Routing to greeting handler")
            return "greeting"
        else:
            logger.info("Routing to CRM query pipeline")
            return "crm_query"

    def _handle_greeting_node(self, state: AgentState) -> AgentState:
        """
        Node: Handle greeting/general conversation

        Generates a friendly response using ChatGPT and wraps it in a simple layout.

        Args:
            state: Current state

        Returns:
            Updated state with greeting response in default layout
        """
        logger.debug("Handling greeting/general conversation...")

        query = state["query"]

        try:
            # Get a friendly response from ChatGPT
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful CRM assistant. Respond to greetings and general questions in a friendly, concise way.

If the user asks what you can do, explain that you can help them:
- View and analyze CRM data (leads, contacts, opportunities, accounts)
- Create custom layouts and dashboards
- Filter and sort records
- Generate reports and insights

Keep responses brief and friendly (2-3 sentences max)."""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.7,
                max_tokens=150
            )

            response_text = completion.choices[0].message.content
            logger.info(f"Generated greeting response: {response_text[:50]}...")

            # Wrap response in default layout
            layout_dict = self.get_fallback_layout(response_text)

            # Create LayoutResponse object
            layout = LayoutResponse(**layout_dict)

            state["layout"] = layout
            state["result"] = layout.model_dump(exclude_none=True, exclude_unset=True)

            return state

        except Exception as e:
            logger.error(f"Error handling greeting: {e}")
            # Fallback to simple response
            fallback_text = "Hello! I'm your CRM assistant. I can help you view and analyze your CRM data. Try asking me to show leads, contacts, or opportunities!"
            layout_dict = self.get_fallback_layout(fallback_text)
            layout = LayoutResponse(**layout_dict)
            state["layout"] = layout
            state["result"] = layout.model_dump(exclude_none=True, exclude_unset=True)
            return state

    def _retrieve_candidates_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Retrieve candidate layouts

        Wraps CandidateRetriever.retrieve()

        Args:
            state: Current state

        Returns:
            Updated state with candidates
        """
        logger.debug("Node 5: Retrieving candidate layouts...")

        candidates = self.candidate_retriever.retrieve(
            query=state["normalized_query"],
            k=5,
            intent=state.get("intent"),
            layout_type=state.get("layout_type"),
            object_type=state.get("object_type")
        )

        state["candidates"] = candidates
        return state

    def _generate_layout_node(self, state: AgentState) -> AgentState:
        """
        Node 6: Generate final layout

        Wraps LayoutGenerator.generate()

        Args:
            state: Current state

        Returns:
            Updated state with layout and result
        """
        logger.debug("Node 6: Generating layout with provided data...")

        # Select best candidate (RAG already ranked them, so use first one)
        candidates = state["candidates"]
        if not candidates:
            raise ValueError("No candidates available for layout generation")

        # Prepare context with query
        context = state.get("context", {})
        if isinstance(context, dict):
            context["query"] = state.get("normalized_query", "")
        else:
            context = {"query": state.get("normalized_query", "")}

        # Generate layout by populating data into candidate structure
        layout = self.layout_generator.generate(
            layout=candidates,
            data=state["data"],
            context=context
        )

        state["layout"] = layout
        # Use model_dump with exclude_none and exclude_unset to remove null fields
        state["result"] = layout.model_dump(exclude_none=True, exclude_unset=True)

        return state

    def generate(
        self,
        query: str,
        data: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate UI layout from query and data

        This is the main entry point - same interface as StructuredUIAgent.

        Args:
            query: User query (e.g., "show me top 5 leads" or "hello")
            data: Data to bind to layout (OPTIONAL for greetings, REQUIRED for CRM queries)
            context: Optional context (user preferences, etc.)

        Returns:
            Complete layout response with sections, rows, components, and data

        Example:
            agent = LangGraphUIAgent()

            # Greeting (no data needed)
            layout = agent.generate(query="hello")

            # CRM query (data required)
            leads_data = [
                {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified"},
                {"id": 2, "name": "TechStart", "revenue": 120000, "status": "negotiation"}
            ]

            layout = agent.generate(
                query="show me all leads",
                data=leads_data
            )
        """
        logger.info(f"Generating layout for query: {query}")

        try:
            # Create initial state (data can be None for greetings)
            initial_state: AgentState = {
                "query": query,
                "data": data or [],
                "context": context,
                "candidates": None,
                "layout": None,
                "result": None,
                "normalized_query": None,
                "is_crm_related": None,
                "reasoning": None,
                "intent": None,
                "layout_type": None,
                "object_type": None,
                "confidence": None
            }

            # Run the graph
            final_state = self.graph.invoke(initial_state)

            # Extract result
            result = final_state["result"]

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
            "orchestration": "LangGraph",
            "components": {
                "query_analyzer": "QueryAnalyzer",
                "candidate_retriever": "CandidateRetriever",
                "layout_generator": "LayoutGenerator"
            },
            "graph_nodes": ["normalize_query", "analyze_intent", "analyze_layout", "analyze_object", "handle_greeting", "retrieve_candidates", "generate_layout"],
            "data_handling": "external",
            "vector_store": vector_stats,
            "status": "ready"
        }

    def get_fallback_layout(self, message: str) -> Dict[str, Any]:
        """
        Get fallback layout for greetings and general responses

        Args:
            message: The message to display

        Returns:
            Simple layout with the message in an HtmlText component
        """
        return {
            "id": "greeting_layout",
            "query": "greeting",
            "object_type": "general",
            "layout_type": "detail",
            "sections": [
                {
                    "id": "body",
                    "title": None,
                    "description": None,
                    "rows": [
                        {
                            "type": "Stack",
                            "direction": "vertical",
                            "gap": 8,
                            "children": [
                                {
                                    "llm_instruction": "if the user query is a greeting or general question, respond with a friendly message. Wrap the message in a simple layout with an HtmlText component. also add the role of the message as 'greeting' in the component. like i am your assistant and i can help you with your CRM data. how can i assist you today?",
                                    "type": "HtmlText",
                                    "value": f"<div class='greeting-message'>{message}</div>"
                                }
                            ]
                        }
                    ]
                }
            ],
            "summary": "Greeting response"
        }

