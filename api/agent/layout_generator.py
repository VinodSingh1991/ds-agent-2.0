"""
Layout Generator

Single responsibility: Populate data into layout structure.

The layout structure comes from RAG (complete LayoutResponse) - we just fill in the data.
"""

import json
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI not installed. Install with: pip install openai>=1.12.0")
    OpenAI = None

from agent.schemas.layout_schemas import LayoutResponse


class LayoutGenerator:
    """
    Populates data into layout structure
    
    Responsibilities:
    - Take layout structure from RAG (complete LayoutResponse)
    - Fill in data values (replace {{placeholders}})
    - DO NOT modify layout structure (except for data)
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
        layout: Dict[str, Any],
        data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> LayoutResponse:
        """
        Populate data into layout structure

        Args:
            layout: Layout structure to populate with data
            data: Data to populate into layout
            context: Optional additional context

        Returns:
            LayoutResponse with data populated into layout structure
        """

        # Build prompt
        prompt = self._build_prompt(layout, data, context)

        logger.debug(f"Prompt length: {len(prompt)} characters")

        use_messages = [
            {
                "role": "system",
                "content": """
You are a strict data filler. Your ONLY job is to fill data into the provided Layout JSON structure.
You MUST follow these rules EXACTLY:

===============================
CRITICAL RULES (DO NOT BREAK)
===============================
1. **RETURN THE EXACT SAME LAYOUT STRUCTURE**
   - Same keys, same order, same nesting
   - No structural changes of any kind

2. **ONLY replace placeholder values**
   - Replace {{title}}, {{columns}}, {{data}}, {{value}} and similar placeholders
   - If there is no placeholder, leave as-is

3. **DO NOT add new fields**
   - No new props, no new keys, no metadata
   - Do NOT add: key, id, variant, className, href, src, etc.

4. **DO NOT remove fields**
   - Keep every field exactly as it exists in the input layout

5. **DO NOT add null/None/empty fields**
   - Only fill values that already exist

6. **props migration rule**
   - If a component has:
        "props": { "a": 1, "b": 2 }
     You MUST move them like:
        "a": 1,
        "b": 2
     And remove "props"

7. **Remove “binds_to” if present**
   - Delete only this key
   - NOTHING else

8. **Content rules**
   - Only fill fields named "value" or placeholders ({{...}})
   - Never generate code, markdown, or explanations
   - Return PURE JSON, no commentary

===============================
WHAT YOU MUST RETURN
===============================
✔ A SINGLE VALID JSON OBJECT  
✔ SAME structure as input layout  
✔ Only values replaced, structure untouched  
✔ PERFECT JSON (no trailing commas, no comments)  
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            # Call OpenAI with JSON mode (not strict structured outputs)
            # We use JSON mode because our schema has extra="allow" which is incompatible with strict mode
            logger.info("Calling OpenAI with JSON mode (response_format={'type': 'json_object'})")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=use_messages,
                response_format={"type": "json_object"}
            )
            logger.info("OpenAI call successful")

            # Parse the JSON response and create LayoutResponse object
            layout_dict = json.loads(completion.choices[0].message.content)
            layout = LayoutResponse(**layout_dict)

            return layout

        except Exception as e:
            logger.error(f"Error generating layout: {e}")
            raise

    def _build_prompt(
        self,
        layout: Dict[str, Any],
        data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build simple prompt for data population

        Args:
            layout: Layout structure to fill with data
            data: Data to populate
            context: Optional additional context

        Returns:
            Prompt string
        """

        prompt = f"""
Fill the data into the layout below.
Follow ALL rules from the system instructions.

=====================
LAYOUT (USE AS-IS)
=====================
{json.dumps(layout, indent=2)}

=====================
DATA (TO INSERT)
=====================
{json.dumps(data, indent=2)}

=====================
RULES FOR YOU
=====================
1. Use EXACT layout structure shown above
2. Replace {{placeholders}} with actual data
3. Only fill fields named "value" or containing placeholders
4. Move `props` values to component level
5. Remove "binds_to"
6. DO NOT add or remove any components
7. DO NOT add any null or extra fields
8. Output must be VALID JSON ONLY
"""

        if context:
            prompt += f"\n\n=====================\nADDITIONAL CONTEXT\n=====================\n{json.dumps(context, indent=2)}"

        return prompt
