"""
Chunk generator - Main orchestrator for generating all chunks

This module reads pattern metadata and generates all 5 types of chunks:
1. Pattern chunks from component_patterns_metadata.json
2. Query-layout pairs from example queries
3. Component documentation
4. Intent mappings
5. Data shape patterns
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from .chunk_builder import ChunkBuilder
from .chunk_types import Chunk


class ChunkGenerator:
    """Generates all chunks for enhanced RAG"""
    
    def __init__(self, patterns_dir: str = None):
        """
        Initialize chunk generator

        Args:
            patterns_dir: Path to patterns directory containing individual pattern JSON files
        """
        if patterns_dir is None:
            # Default to local disposableUIAgent dataset/patterns folder
            base_dir = Path(__file__).parent.parent.parent
            patterns_dir = base_dir / "dataset" / "patterns"

        self.patterns_dir = Path(patterns_dir)
        self.builder = ChunkBuilder()

        logger.info(f"Initialized ChunkGenerator with patterns from: {self.patterns_dir}")

    def load_patterns(self) -> List[Dict[str, Any]]:
        """Load pattern metadata from individual JSON files in patterns folder"""
        patterns = []

        if not self.patterns_dir.exists():
            logger.error(f"Patterns directory not found: {self.patterns_dir}")
            return []

        if not self.patterns_dir.is_dir():
            logger.error(f"Patterns path is not a directory: {self.patterns_dir}")
            return []

        # Load all JSON files from the patterns directory
        pattern_files = sorted(self.patterns_dir.glob("*.json"))

        if not pattern_files:
            logger.warning(f"No pattern files found in: {self.patterns_dir}")
            return []

        for pattern_file in pattern_files:
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    pattern = json.load(f)
                    patterns.append(pattern)
                    logger.debug(f"Loaded pattern: {pattern.get('pattern_id')} from {pattern_file.name}")
            except Exception as e:
                logger.error(f"Error loading pattern from {pattern_file}: {e}")

        logger.info(f"Loaded {len(patterns)} patterns from {len(pattern_files)} files")
        return patterns
    
    def generate_pattern_chunks(self, patterns: List[Dict[str, Any]]) -> List[Chunk]:
        """Generate pattern chunks from pattern metadata"""
        chunks = []
        
        for pattern in patterns:
            try:
                chunk = self.builder.build_pattern_chunk(pattern)
                chunks.append(chunk)
                logger.debug(f"Generated pattern chunk: {chunk.chunk_id}")
            except Exception as e:
                logger.error(f"Error generating pattern chunk for {pattern.get('pattern_id')}: {e}")
        
        logger.info(f"Generated {len(chunks)} pattern chunks")
        return chunks
    
    def generate_query_layout_chunks(self) -> List[Chunk]:
        """
        Generate query-layout pair chunks from example queries
        
        These are hand-crafted examples showing how queries map to layouts
        """
        examples = [
            {
                "query": "show me all leads",
                "analysis": {
                    "object_type": "lead",
                    "intent": "view_list",
                    "layout_type": "list",
                    "filters": [],
                    "sort": None,
                    "limit": None
                },
                "layout": {"type": "simple_list"}
            },
            {
                "query": "show me top 5 leads with revenue > 50k",
                "analysis": {
                    "object_type": "lead",
                    "intent": "view_list",
                    "layout_type": "list",
                    "filters": [{"field": "revenue", "operator": ">", "value": 50000}],
                    "sort": "revenue DESC",
                    "limit": 5
                },
                "layout": {"type": "filtered_list_with_metrics"}
            },
            {
                "query": "display contact details for John Doe",
                "analysis": {
                    "object_type": "contact",
                    "intent": "view_detail",
                    "layout_type": "detail",
                    "filters": [{"field": "name", "operator": "=", "value": "John Doe"}],
                    "sort": None,
                    "limit": 1
                },
                "layout": {"type": "detail_view"}
            },
            {
                "query": "sales dashboard with metrics",
                "analysis": {
                    "object_type": "opportunity",
                    "intent": "view_dashboard",
                    "layout_type": "dashboard",
                    "filters": [],
                    "sort": None,
                    "limit": None
                },
                "layout": {"type": "metric_dashboard"}
            },
            {
                "query": "list all contacts with photos",
                "analysis": {
                    "object_type": "contact",
                    "intent": "view_list",
                    "layout_type": "list",
                    "filters": [],
                    "sort": None,
                    "limit": None
                },
                "layout": {"type": "user_avatar_list"}
            }
        ]
        
        chunks = []
        for example in examples:
            try:
                chunk = self.builder.build_query_layout_chunk(
                    query=example["query"],
                    layout=example["layout"],
                    analysis=example["analysis"]
                )
                chunks.append(chunk)
                logger.debug(f"Generated query-layout chunk: {chunk.chunk_id}")
            except Exception as e:
                logger.error(f"Error generating query-layout chunk: {e}")
        
        logger.info(f"Generated {len(chunks)} query-layout chunks")
        return chunks
    
    def generate_component_doc_chunks(self) -> List[Chunk]:
        """Generate component documentation chunks"""
        component_docs = [
            {
                "component_type": "Metric",
                "description": "Display numeric values with formatting",
                "category": "data_display",
                "use_for": ["numbers", "currency", "percentages", "KPIs", "statistics"],
                "data_types": ["number", "currency", "percentage"],
                "common_bindings": ["revenue", "count", "amount", "total", "average", "price"]
            },
            {
                "component_type": "Badge",
                "description": "Display status or category labels",
                "category": "data_display",
                "use_for": ["status", "categories", "tags", "labels"],
                "data_types": ["enum", "string"],
                "common_bindings": ["status", "category", "type", "priority", "stage"]
            },
            {
                "component_type": "Avatar",
                "description": "Display user photos or initials",
                "category": "media",
                "use_for": ["user photos", "profile pictures", "contact images"],
                "data_types": ["url", "string"],
                "common_bindings": ["avatar_url", "photo", "image", "picture"]
            }
        ]
        
        chunks = []
        for doc in component_docs:
            try:
                chunk = self.builder.build_component_doc_chunk(
                    component_type=doc["component_type"],
                    documentation=doc
                )
                chunks.append(chunk)
            except Exception as e:
                logger.error(f"Error generating component doc chunk: {e}")
        
        logger.info(f"Generated {len(chunks)} component doc chunks")
        return chunks

    def generate_intent_mapping_chunks(self) -> List[Chunk]:
        """Generate intent-to-pattern mapping chunks"""
        intent_mappings = [
            {
                "intent": "view_list",
                "user_phrases": ["show me", "display", "list", "get all", "find"],
                "indicators": {
                    "has_filters": ["with", "where", "that have", ">", "<", "="],
                    "has_sorting": ["top", "best", "highest", "lowest", "sorted by"],
                    "has_limit": ["top 5", "first 10", "limit"]
                },
                "recommended_patterns": [
                    {"pattern_id": "user_avatar_list", "when": "data has images or people", "confidence": 0.9},
                    {"pattern_id": "data_table_pattern", "when": "need to compare fields", "confidence": 0.85},
                    {"pattern_id": "status_list_compact", "when": "focus on status", "confidence": 0.8}
                ]
            },
            {
                "intent": "view_detail",
                "user_phrases": ["details for", "show", "view", "get info about"],
                "indicators": {
                    "single_record": ["details", "info", "about", "for"],
                    "has_name": ["John", "specific name"]
                },
                "recommended_patterns": [
                    {"pattern_id": "detail_view_card", "when": "single record", "confidence": 0.95},
                    {"pattern_id": "profile_view", "when": "person/contact", "confidence": 0.9}
                ]
            },
            {
                "intent": "view_dashboard",
                "user_phrases": ["dashboard", "metrics", "analytics", "overview", "summary"],
                "indicators": {
                    "has_metrics": ["metrics", "KPIs", "statistics", "numbers"],
                    "has_aggregation": ["total", "average", "sum", "count"]
                },
                "recommended_patterns": [
                    {"pattern_id": "metric_dashboard", "when": "multiple metrics", "confidence": 0.95},
                    {"pattern_id": "analytics_view", "when": "charts and graphs", "confidence": 0.85}
                ]
            }
        ]

        chunks = []
        for mapping in intent_mappings:
            try:
                chunk = self.builder.build_intent_mapping_chunk(
                    intent=mapping["intent"],
                    mapping=mapping
                )
                chunks.append(chunk)
            except Exception as e:
                logger.error(f"Error generating intent mapping chunk: {e}")

        logger.info(f"Generated {len(chunks)} intent mapping chunks")
        return chunks

    def generate_data_shape_chunks(self) -> List[Chunk]:
        """Generate data shape pattern chunks"""
        data_shapes = [
            {
                "shape_id": "small_list_with_metrics",
                "data_characteristics": {
                    "record_count": {"min": 3, "max": 10},
                    "has_numeric_fields": True,
                    "has_images": False,
                    "has_status_fields": True,
                    "field_count": {"min": 3, "max": 8}
                },
                "recommended_layout_type": "list",
                "recommended_components": ["ListCard", "Metric", "Badge", "Heading"],
                "reasoning": "Small datasets with metrics work best in list format where each item can show detailed metrics."
            },
            {
                "shape_id": "large_table_data",
                "data_characteristics": {
                    "record_count": {"min": 20, "max": 1000},
                    "has_numeric_fields": True,
                    "has_images": False,
                    "has_status_fields": True,
                    "field_count": {"min": 5, "max": 15}
                },
                "recommended_layout_type": "table",
                "recommended_components": ["Table", "Badge", "Metric"],
                "reasoning": "Large datasets need table format for comparison and scanning."
            },
            {
                "shape_id": "single_record_detail",
                "data_characteristics": {
                    "record_count": {"min": 1, "max": 1},
                    "has_numeric_fields": True,
                    "has_images": True,
                    "has_status_fields": True,
                    "field_count": {"min": 5, "max": 20}
                },
                "recommended_layout_type": "detail",
                "recommended_components": ["Card", "Heading", "Text", "Metric", "Badge", "Avatar"],
                "reasoning": "Single record needs detail view with all fields organized in sections."
            },
            {
                "shape_id": "people_list_with_photos",
                "data_characteristics": {
                    "record_count": {"min": 3, "max": 100},
                    "has_numeric_fields": False,
                    "has_images": True,
                    "has_status_fields": True,
                    "field_count": {"min": 3, "max": 8}
                },
                "recommended_layout_type": "list",
                "recommended_components": ["Stack", "ListCard", "Avatar", "Heading", "Text", "Badge"],
                "reasoning": "People/contacts with photos need avatar list for visual identification."
            }
        ]

        chunks = []
        for shape in data_shapes:
            try:
                chunk = self.builder.build_data_shape_chunk(
                    shape_id=shape["shape_id"],
                    shape_pattern=shape
                )
                chunks.append(chunk)
            except Exception as e:
                logger.error(f"Error generating data shape chunk: {e}")

        logger.info(f"Generated {len(chunks)} data shape chunks")
        return chunks

    def generate_all_chunks(self) -> List[Chunk]:
        """
        Generate all chunks

        Returns:
            List of all chunks ready for indexing
        """
        logger.info("Starting chunk generation...")

        all_chunks = []

        # 1. Load patterns and generate pattern chunks
        patterns = self.load_patterns()
        pattern_chunks = self.generate_pattern_chunks(patterns)
        all_chunks.extend(pattern_chunks)

        # 2. Generate query-layout pair chunks
        query_chunks = self.generate_query_layout_chunks()
        all_chunks.extend(query_chunks)

        # 3. Generate component documentation chunks
        component_chunks = self.generate_component_doc_chunks()
        all_chunks.extend(component_chunks)

        # 4. Generate intent mapping chunks
        intent_chunks = self.generate_intent_mapping_chunks()
        all_chunks.extend(intent_chunks)

        # 5. Generate data shape chunks
        data_shape_chunks = self.generate_data_shape_chunks()
        all_chunks.extend(data_shape_chunks)

        logger.info(f"Generated {len(all_chunks)} total chunks")
        logger.info(f"  - Pattern chunks: {len(pattern_chunks)}")
        logger.info(f"  - Query-layout chunks: {len(query_chunks)}")
        logger.info(f"  - Component doc chunks: {len(component_chunks)}")
        logger.info(f"  - Intent mapping chunks: {len(intent_chunks)}")
        logger.info(f"  - Data shape chunks: {len(data_shape_chunks)}")

        return all_chunks

    def save_chunks(self, chunks: List[Chunk], output_path: str = None):
        """
        Save chunks to JSON file

        Args:
            chunks: List of chunks to save
            output_path: Path to output file
        """
        if output_path is None:
            base_dir = Path(__file__).parent.parent.parent
            output_path = base_dir / "dataset" / "enhanced_chunks.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert chunks to dict
        chunks_data = [chunk.model_dump() for chunk in chunks]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(chunks)} chunks to {output_path}")


def main():
    """Main entry point for chunk generation"""
    generator = ChunkGenerator()
    chunks = generator.generate_all_chunks()
    generator.save_chunks(chunks)
    print(f"✅ Generated {len(chunks)} chunks successfully!")


if __name__ == "__main__":
    main()

