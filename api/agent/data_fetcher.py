"""
Data Fetcher

Single responsibility: Fetch data based on query analysis.

Currently provides mock data. In production, this would connect to a real database.
"""

from typing import List, Dict, Any
from loguru import logger

from agent.schemas.query_schemas import QueryAnalysis


class DataFetcher:
    """
    Fetches data based on query analysis
    
    Responsibilities:
    - Fetch data from data source (currently mock)
    - Apply filters from query analysis
    - Apply sorting and limits
    - Return structured data
    
    In production, this would:
    - Connect to database
    - Execute queries
    - Handle pagination
    - Cache results
    """
    
    def __init__(self, data_source: str = "mock"):
        """
        Initialize data fetcher
        
        Args:
            data_source: Data source type ("mock", "database", "api", etc.)
        """
        self.data_source = data_source
        logger.info(f"Initialized DataFetcher with source: {data_source}")
    
    def fetch(self, analysis: QueryAnalysis) -> List[Dict[str, Any]]:
        """
        Fetch data based on query analysis
        
        Args:
            analysis: Query analysis with object type, filters, etc.
            
        Returns:
            List of data records
        """
        logger.debug(f"Fetching data for object type: {analysis.object_type}")
        
        if self.data_source == "mock":
            data = self._fetch_mock_data(analysis)
        else:
            # In production, connect to real database
            data = self._fetch_from_database(analysis)
        
        # Apply filters
        data = self._apply_filters(data, analysis)
        
        # Apply sorting
        data = self._apply_sorting(data, analysis)
        
        # Apply limit
        data = self._apply_limit(data, analysis)
        
        logger.info(f"Fetched {len(data)} records")
        return data
    
    def _fetch_mock_data(self, analysis: QueryAnalysis) -> List[Dict[str, Any]]:
        """
        Fetch mock data based on object type
        
        Args:
            analysis: Query analysis
            
        Returns:
            Mock data records
        """
        object_type = analysis.object_type.lower()
        
        if "lead" in object_type:
            return [
                {"id": 1, "name": "Acme Corp", "revenue": 75000, "status": "qualified", "contact": "John Smith", "created": "2024-01-15"},
                {"id": 2, "name": "TechStart Inc", "revenue": 120000, "status": "negotiation", "contact": "Jane Doe", "created": "2024-01-20"},
                {"id": 3, "name": "Global Solutions", "revenue": 95000, "status": "qualified", "contact": "Bob Johnson", "created": "2024-01-25"},
                {"id": 4, "name": "Innovation Labs", "revenue": 150000, "status": "won", "contact": "Alice Brown", "created": "2024-02-01"},
                {"id": 5, "name": "Future Systems", "revenue": 60000, "status": "qualified", "contact": "Charlie Wilson", "created": "2024-02-05"},
                {"id": 6, "name": "Smart Tech", "revenue": 85000, "status": "negotiation", "contact": "Diana Prince", "created": "2024-02-08"},
                {"id": 7, "name": "Digital Dynamics", "revenue": 110000, "status": "qualified", "contact": "Ethan Hunt", "created": "2024-02-10"}
            ]
        
        elif "contact" in object_type or "user" in object_type:
            return [
                {"id": 1, "name": "John Smith", "email": "john@example.com", "role": "CEO", "company": "Acme Corp", "phone": "+1-555-0101"},
                {"id": 2, "name": "Jane Doe", "email": "jane@example.com", "role": "CTO", "company": "TechStart", "phone": "+1-555-0102"},
                {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "role": "VP Sales", "company": "Global Solutions", "phone": "+1-555-0103"},
                {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "role": "Director", "company": "Innovation Labs", "phone": "+1-555-0104"},
                {"id": 5, "name": "Charlie Wilson", "email": "charlie@example.com", "role": "Manager", "company": "Future Systems", "phone": "+1-555-0105"}
            ]
        
        elif "deal" in object_type or "opportunity" in object_type:
            return [
                {"id": 1, "title": "Enterprise License", "value": 50000, "stage": "proposal", "probability": 75, "close_date": "2024-03-15"},
                {"id": 2, "title": "Cloud Migration", "value": 120000, "stage": "negotiation", "probability": 60, "close_date": "2024-04-01"},
                {"id": 3, "title": "Support Contract", "value": 25000, "stage": "closed_won", "probability": 100, "close_date": "2024-02-01"}
            ]

        elif "case" in object_type or "ticket" in object_type:
            return [
                {"id": 1, "case_number": "CASE-001", "subject": "Login Issue", "priority": "high", "status": "open", "assigned_to": "John Smith", "created_date": "2024-02-01", "customer": "Acme Corp"},
                {"id": 2, "case_number": "CASE-002", "subject": "Payment Failed", "priority": "critical", "status": "in_progress", "assigned_to": "Jane Doe", "created_date": "2024-02-03", "customer": "TechStart Inc"},
                {"id": 3, "case_number": "CASE-003", "subject": "Feature Request", "priority": "low", "status": "open", "assigned_to": "Bob Johnson", "created_date": "2024-02-05", "customer": "Global Solutions"},
                {"id": 4, "case_number": "CASE-004", "subject": "Data Export Issue", "priority": "medium", "status": "resolved", "assigned_to": "Alice Brown", "created_date": "2024-02-06", "customer": "Innovation Labs"},
                {"id": 5, "case_number": "CASE-005", "subject": "API Integration", "priority": "high", "status": "in_progress", "assigned_to": "Charlie Wilson", "created_date": "2024-02-08", "customer": "Future Systems"},
                {"id": 6, "case_number": "CASE-006", "subject": "Performance Slow", "priority": "medium", "status": "open", "assigned_to": "Diana Prince", "created_date": "2024-02-09", "customer": "Smart Tech"}
            ]

        elif "account" in object_type or "company" in object_type or "organization" in object_type:
            return [
                {"id": 1, "account_name": "Acme Corporation", "industry": "Technology", "revenue": 5000000, "employees": 250, "status": "active", "owner": "John Smith", "location": "San Francisco, CA", "tier": "enterprise"},
                {"id": 2, "account_name": "TechStart Inc", "industry": "Software", "revenue": 2500000, "employees": 120, "status": "active", "owner": "Jane Doe", "location": "Austin, TX", "tier": "mid-market"},
                {"id": 3, "account_name": "Global Solutions Ltd", "industry": "Consulting", "revenue": 8000000, "employees": 450, "status": "active", "owner": "Bob Johnson", "location": "New York, NY", "tier": "enterprise"},
                {"id": 4, "account_name": "Innovation Labs", "industry": "Research", "revenue": 1500000, "employees": 80, "status": "prospect", "owner": "Alice Brown", "location": "Boston, MA", "tier": "small"},
                {"id": 5, "account_name": "Future Systems", "industry": "Manufacturing", "revenue": 12000000, "employees": 600, "status": "active", "owner": "Charlie Wilson", "location": "Chicago, IL", "tier": "enterprise"},
                {"id": 6, "account_name": "Smart Tech Co", "industry": "Technology", "revenue": 3500000, "employees": 180, "status": "active", "owner": "Diana Prince", "location": "Seattle, WA", "tier": "mid-market"}
            ]

        elif "branch" in object_type or "office" in object_type or "location" in object_type:
            return [
                {"id": 1, "branch_name": "Downtown Branch", "location": "123 Main St, San Francisco, CA", "manager": "John Smith", "employees": 45, "revenue": 2500000, "region": "West", "status": "active", "opened_date": "2020-01-15"},
                {"id": 2, "branch_name": "North Side Branch", "location": "456 Oak Ave, Austin, TX", "manager": "Jane Doe", "employees": 32, "revenue": 1800000, "region": "South", "status": "active", "opened_date": "2019-06-20"},
                {"id": 3, "branch_name": "East End Branch", "location": "789 Pine Rd, New York, NY", "manager": "Bob Johnson", "employees": 58, "revenue": 3200000, "region": "East", "status": "active", "opened_date": "2018-03-10"},
                {"id": 4, "branch_name": "Harbor Branch", "location": "321 Beach Blvd, Boston, MA", "manager": "Alice Brown", "employees": 28, "revenue": 1500000, "region": "East", "status": "active", "opened_date": "2021-09-05"},
                {"id": 5, "branch_name": "Central Branch", "location": "654 Center St, Chicago, IL", "manager": "Charlie Wilson", "employees": 52, "revenue": 2800000, "region": "Central", "status": "active", "opened_date": "2017-11-12"},
                {"id": 6, "branch_name": "Tech Hub Branch", "location": "987 Innovation Dr, Seattle, WA", "manager": "Diana Prince", "employees": 38, "revenue": 2100000, "region": "West", "status": "active", "opened_date": "2020-07-22"}
            ]

        elif "product" in object_type or "item" in object_type or "inventory" in object_type:
            return [
                {"id": 1, "product_name": "Enterprise Suite Pro", "category": "Software", "price": 999.99, "stock": 150, "rating": 4.8, "status": "available", "image_url": "https://example.com/product1.jpg", "sku": "PRD-001"},
                {"id": 2, "product_name": "Cloud Storage Plus", "category": "Services", "price": 49.99, "stock": 999, "rating": 4.6, "status": "available", "image_url": "https://example.com/product2.jpg", "sku": "PRD-002"},
                {"id": 3, "product_name": "Analytics Dashboard", "category": "Software", "price": 299.99, "stock": 75, "rating": 4.9, "status": "available", "image_url": "https://example.com/product3.jpg", "sku": "PRD-003"},
                {"id": 4, "product_name": "Mobile App Builder", "category": "Tools", "price": 199.99, "stock": 45, "rating": 4.5, "status": "low_stock", "image_url": "https://example.com/product4.jpg", "sku": "PRD-004"},
                {"id": 5, "product_name": "API Gateway", "category": "Infrastructure", "price": 499.99, "stock": 0, "rating": 4.7, "status": "out_of_stock", "image_url": "https://example.com/product5.jpg", "sku": "PRD-005"},
                {"id": 6, "product_name": "Security Suite", "category": "Software", "price": 799.99, "stock": 120, "rating": 4.9, "status": "available", "image_url": "https://example.com/product6.jpg", "sku": "PRD-006"},
                {"id": 7, "product_name": "Collaboration Hub", "category": "Services", "price": 29.99, "stock": 999, "rating": 4.4, "status": "available", "image_url": "https://example.com/product7.jpg", "sku": "PRD-007"}
            ]

        else:
            # Generic data for any other object type
            return [
                {"id": 1, "name": "Item 1", "value": 100, "status": "active", "category": "A", "created_date": "2024-01-15"},
                {"id": 2, "name": "Item 2", "value": 200, "status": "pending", "category": "B", "created_date": "2024-01-20"},
                {"id": 3, "name": "Item 3", "value": 150, "status": "active", "category": "A", "created_date": "2024-01-25"},
                {"id": 4, "name": "Item 4", "value": 300, "status": "completed", "category": "C", "created_date": "2024-02-01"},
                {"id": 5, "name": "Item 5", "value": 175, "status": "active", "category": "B", "created_date": "2024-02-05"}
            ]
    
    def _fetch_from_database(self, analysis: QueryAnalysis) -> List[Dict[str, Any]]:
        """
        Fetch data from real database (placeholder)
        
        Args:
            analysis: Query analysis
            
        Returns:
            Data records from database
        """
        # TODO: Implement real database connection
        logger.warning("Database fetching not implemented, using mock data")
        return self._fetch_mock_data(analysis)
    
    def _apply_filters(self, data: List[Dict[str, Any]], analysis: QueryAnalysis) -> List[Dict[str, Any]]:
        """Apply filters from query analysis"""
        if not analysis.filters:
            return data
        
        # Simple filter implementation
        # In production, this would be done at database level
        filtered_data = data
        for filter_obj in analysis.filters:
            # Basic filtering logic
            # TODO: Implement proper filter operators
            pass
        
        return filtered_data
    
    def _apply_sorting(self, data: List[Dict[str, Any]], analysis: QueryAnalysis) -> List[Dict[str, Any]]:
        """Apply sorting from query analysis"""
        if not analysis.sort:
            return data
        
        # Simple sorting implementation
        # TODO: Implement proper sorting logic
        return data
    
    def _apply_limit(self, data: List[Dict[str, Any]], analysis: QueryAnalysis) -> List[Dict[str, Any]]:
        """Apply limit from query analysis"""
        if analysis.limit:
            return data[:analysis.limit]
        return data

