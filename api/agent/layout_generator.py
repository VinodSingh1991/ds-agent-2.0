"""
Layout Generator

Single responsibility: Generate UI layouts using structured outputs.

Uses OpenAI's structured outputs to guarantee valid LayoutResponse objects.
"""

import json
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.schemas.query_schemas import QueryAnalysis
from agent.schemas.layout_schemas import LayoutResponse


class LayoutGenerator:
    """
    Generates UI layouts using structured outputs
    
    Responsibilities:
    - Generate layout from query, analysis, candidates, and data
    - Format prompts with examples
    - Suggest appropriate components for data fields
    - Ensure proper data binding
    """
    
    def __init__(self, client: OpenAI, model: str = "gpt-4o-2024-08-06"):
        """
        Initialize layout generator
        
        Args:
            client: OpenAI client instance
            model: Model to use for generation
        """
        self.client = client
        self.model = model
        logger.info(f"Initialized LayoutGenerator with model: {model}")
    
    def generate(
        self,
        query: str,
        analysis: QueryAnalysis,
        candidates: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> LayoutResponse:
        """
        Generate layout using structured output
        
        Args:
            query: User query
            analysis: Query analysis
            candidates: Candidate layouts from RAG
            data: Data to bind to layout
            context: Optional context
            
        Returns:
            LayoutResponse with complete layout
        """
        logger.debug("Generating layout with structured output...")
        
        # Build prompt
        prompt = self._build_prompt(query, analysis, candidates, data, context)
        
        # Call OpenAI with structured output
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI layout generator. Create structured layouts with proper data binding."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=LayoutResponse
            )
            
            layout = completion.choices[0].message.parsed
            
            # Ensure data is included
            if not layout.data:
                layout.data = data
            
            logger.info(f"Layout generated with {len(layout.sections)} sections")
            return layout
        
        except Exception as e:
            logger.error(f"Error generating layout: {e}")
            raise
    
    def _build_prompt(
        self,
        query: str,
        analysis: QueryAnalysis,
        candidates: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build generation prompt
        
        Args:
            query: User query
            analysis: Query analysis
            candidates: Candidate layouts
            data: Data records
            context: Optional context
            
        Returns:
            Formatted prompt
        """
        # Format candidates
        candidate_examples = self._format_candidates(candidates)
        
        # Get data sample
        data_sample = data[:2] if len(data) > 2 else data
        
        # Get data fields with suggestions
        data_fields = self._get_data_fields(data)
        
        prompt = f"""Generate a UI layout for this query.

Query: "{query}"

Analysis:
- Object Type: {analysis.object_type}
- Intent: {analysis.intent}
- Layout Type: {analysis.layout_type}
- Reasoning: {analysis.reasoning}

Data Sample (first 2 records):
{json.dumps(data_sample, indent=2)}

Available Data Fields:
{data_fields}

Similar Layouts (for reference):
{candidate_examples}

Generate a complete layout that:
1. Uses appropriate components for each data field
2. Binds components to data fields using "binds_to"
3. Organizes components into sections and rows
4. Uses the layout_type: {analysis.layout_type}
5. Includes all data records in the response

Component Types Available:
- Stack (container for vertical/horizontal layout)
- Card (container with border and padding)
- ListCard (card optimized for list items)
- Heading (titles and headings)
- Text (labels and text values)
- Metric (numbers, currency, percentages)
- Badge (status, tags, labels)
- Avatar (images, user initials)
- Button (actions and links)
- Table (tabular data with columns)

Data Binding Rules:
- Use "binds_to" to connect components to data fields
- Use "repeat" on containers to repeat for each data record
- Use appropriate component types for data types:
  * Numbers/Currency → Metric
  * Status/Tags → Badge
  * Names/Titles → Heading
  * Images/Photos → Avatar
  * Descriptions → Text
  * Actions → Button

Layout Structure:
- Sections contain rows
- Rows contain components
- Components can have children
- Use "repeat" for dynamic lists
"""

        if context:
            prompt += f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}"

        return prompt

    def _format_candidates(self, candidates: List[Dict[str, Any]]) -> str:
        """
        Format candidate layouts for prompt

        Args:
            candidates: List of candidate layouts

        Returns:
            Formatted string
        """
        if not candidates:
            return "No similar layouts found."

        formatted = []
        for i, candidate in enumerate(candidates[:3], 1):  # Top 3
            chunk = candidate["chunk"]
            source = candidate["source"]
            score = candidate["score"]

            formatted.append(f"\n{i}. [{source.upper()}] (score: {score:.3f})")

            # Add relevant info based on source
            if source == "query_example":
                content = chunk.get("content", {})
                formatted.append(f"   Query: {content.get('query', 'N/A')}")
                formatted.append(f"   Layout Type: {content.get('layout', {}).get('layout_type', 'N/A')}")
            elif source == "ui_pattern":
                metadata = chunk.get("metadata", {})
                formatted.append(f"   Pattern: {metadata.get('pattern_name', 'N/A')}")
                use_cases = metadata.get('use_cases', [])
                if use_cases:
                    formatted.append(f"   Use Cases: {', '.join(use_cases[:3])}")

        return "\n".join(formatted)

    def _get_data_fields(self, data: List[Dict[str, Any]]) -> str:
        """
        Get list of available data fields with component suggestions

        Args:
            data: Data records

        Returns:
            Formatted field list
        """
        if not data:
            return "No fields available."

        # Get fields from first record
        fields = list(data[0].keys())

        # Infer types and suggest components
        field_info = []
        for field in fields:
            value = data[0][field]
            field_type = type(value).__name__

            # Suggest component type
            component_suggestion = self._suggest_component_for_field(field, value)

            field_info.append(f"- {field} ({field_type}) → {component_suggestion}")

        return "\n".join(field_info)

    def _suggest_component_for_field(self, field_name: str, value: Any) -> str:
        """
        Suggest component type for a field

        Args:
            field_name: Field name
            value: Field value

        Returns:
            Suggested component type
        """
        field_lower = field_name.lower()

        # Check field name patterns
        if "status" in field_lower or "state" in field_lower or "stage" in field_lower:
            return "Badge"
        elif "image" in field_lower or "photo" in field_lower or "avatar" in field_lower:
            return "Avatar"
        elif "name" in field_lower or "title" in field_lower:
            return "Heading"
        elif "email" in field_lower or "phone" in field_lower or "address" in field_lower:
            return "Text"
        elif "description" in field_lower or "notes" in field_lower or "comment" in field_lower:
            return "Text"

        # Check value type
        if isinstance(value, (int, float)):
            if "revenue" in field_lower or "price" in field_lower or "amount" in field_lower or "value" in field_lower:
                return "Metric (currency)"
            elif "count" in field_lower or "total" in field_lower or "quantity" in field_lower:
                return "Metric (number)"
            elif "percent" in field_lower or "probability" in field_lower:
                return "Metric (percentage)"
            else:
                return "Metric"
        elif isinstance(value, bool):
            return "Badge"
        elif isinstance(value, str):
            if len(value) > 50:
                return "Text"
            else:
                return "Text or Heading"

        return "Text"

