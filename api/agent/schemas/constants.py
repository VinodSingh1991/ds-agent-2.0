from enum import Enum


class LayoutType(str, Enum):
    """
    Minimal, universal, composable layout types for agent-driven UI.
    """

    # Core primitives
    LIST = "list"                  # list of any data
    TABLE = "table"                # tabular view
    DETAIL = "detail"              # key-value blocks
    CARD = "card"                  # card-based layout
    FORM = "form"                  # input forms

    # Higher-order derived UI
    SUMMARY = "summary"            # summary headers / overviews
    KPI = "kpi"                    # metric blocks
    INSIGHTS = "insights"          # AI insights / analysis
    CHART = "chart"                # charts, graphs, funnel, etc.
    TIMELINE = "timeline"          # timeline or activity history
    BIRTHDAY = "birthday"            # birthday layout (special case of timeline)
    DASHBOARD = "dashboard"        # dashboard (composite of multiple types)
    WELCOME = "welcome"            # welcome layout (special case of summary)

    # Meta layouts
    COMPOSITE = "composite"        # combo of multiple types
    EMPTY = "empty"                # no data / empty state
    ERROR = "error"                # error layout
    LOADING = "loading"            # loading screen


from enum import Enum


class CompositePattern(str, Enum):
    """
    Universal composite layout patterns.
    
    These patterns describe how multiple layout types 
    can be combined to build complex pages.
    """

    BASIC_SUMMARY = "basic_summary"                  # summary + detail
    SUMMARY_WITH_LIST = "summary_with_list"          # summary + table/list
    SUMMARY_WITH_INSIGHTS = "summary_with_insights"  # summary + insights + kpi
    DASHBOARD = "dashboard"                          # kpi + insights + charts + tables
    RECORD_OVERVIEW = "record_overview"              # summary + detail + related lists
    ACTIVITY_VIEW = "activity_view"                  # timeline + insights
    FULL_COMPOSITE = "full_composite"                # dynamic everything

    

COMPOSITE_PATTERN_LAYOUTS = {
    CompositePattern.BASIC_SUMMARY: 
        ["summary", "detail"],

    CompositePattern.SUMMARY_WITH_LIST:
        ["summary", "detail", "table"],

    CompositePattern.SUMMARY_WITH_INSIGHTS:
        ["summary", "kpi", "insights"],

    CompositePattern.DASHBOARD:
        ["kpi", "insights", "chart", "table"],

    CompositePattern.RECORD_OVERVIEW:
        ["summary", "detail", "list", "table"],

    CompositePattern.ACTIVITY_VIEW:
        ["timeline", "insights"],

    CompositePattern.FULL_COMPOSITE:
        ["summary", "detail", "table", "list", "insights", "kpi", "chart", "timeline"]
}


class FilterOperator(str, Enum):
    """
    Supported filter operators for query analysis
    
    These operators are used to interpret user queries and apply the correct filters when retrieving data.
    
    Examples:
        - "revenue > 50000" would use operator ">"
        - "name contains 'tech'" would use operator "contains"
        - "status in 'open, pending'" would use operator "in"
    """
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUALS = "greater_than_or_equals"
    LESS_THAN_OR_EQUALS = "less_than_or_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    EMPTY = "empty"
    NOT_EMPTY = "not_empty"
    BEFORE = "before"
    AFTER = "after"
    ON_OR_BEFORE = "on_or_before"
    ON_OR_AFTER = "on_or_after"
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    NEXT_WEEK = "next_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    NEXT_MONTH = "next_month"
    # Add more operators as needed


class SortDirection(str, Enum):
    """
    Supported sort directions for query analysis
    """
    ASCENDING = "ascending"
    DESCENDING = "descending"


class IntentType(str, Enum):
    """
    Supported intent types for query analysis
    
    These intent types help categorize the user's query and determine the appropriate response format.
    """
    GET = "get"
    POST = "post"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    SEARCH = "search"
    ANALYZE = "analyze"
    COMPARE = "compare"
    UNKNOWN = "unknown"


class ReasoningType(str, Enum):
    """
    Supported reasoning types for query analysis
    
    These reasoning types provide insight into how the agent interpreted the user's query and arrived at its conclusions.
    """
    DIRECT = "direct"
    INFERRED = "inferred"
    AMBIGUOUS = "ambiguous"
    DEFAULT = "default"


class ResponseFormatType(str, Enum):
    """
    Supported response format types for layout generation
    
    These format types guide the agent in structuring its response to fit the user's needs and the UI's capabilities.
    """
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"

class ObjectType(str, Enum):
    """
    Supported CRM object types for query analysis
    
    These object types help the agent identify which CRM entities the user is referring to in their query.
    """
    LEAD = "lead"
    CONTACT = "contact"
    OPPORTUNITY = "opportunity"
    ACCOUNT = "account"
    ACTIVITY = "activity"
    CASE = "case"
    CAMPAIGN = "campaign"
    PRODUCT = "product"
    QUOTE = "quote"
    INVOICE = "invoice"
    GENERAL = "general"


class LimitType(str, Enum):
    """
    Supported limit types for query analysis

    These limit types indicate whether the user's query includes a limit on the number of records to retrieve.
    """
    NONE = "none"
    SINGLE = "single"
    MULTIPLE = "multiple"


class QueryIntent(str, Enum):
    """
    User query intent types for hybrid intent detection

    These intents are detected using keyword matching first, then LLM fallback.
    """
    # Greeting and general
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"

    # CRM data queries
    VIEW_LIST = "view_list"
    VIEW_DETAIL = "view_detail"
    VIEW_SUMMARY = "view_summary"
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_TABLE = "view_table"
    VIEW_TRENDS = "view_trends"
    VIEW_COMPARISON = "view_comparison"
    VIEW_CARDS = "view_cards"
    HTML_VIEW = "html_view"

    # Actions
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"


# Intent keyword patterns for fast detection
INTENT_KEYWORDS = {
    QueryIntent.GREETING: [
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
        "good evening", "howdy", "what's up", "whats up", "sup", "yo", "hi there",
        "good day", "hey there", "hello there", "greet", "salutations"
    ],

    QueryIntent.HELP: [
        "help", "what can you do", "how do i", "how to", "guide",
        "tutorial", "assist", "support", "explain how", "show me how", "can you", "could you", "would you"
    ],

    QueryIntent.VIEW_LIST: [
        "show me", "display", "list", "get all", "find", "search for",
        "view all", "give me all", "fetch", "retrieve", "show all", "display all", "list all", "get me all", "find all", "search all"
    ],

    QueryIntent.VIEW_DETAIL: [
        "details for", "detail of", "show", "view", "get info about",
        "information on", "tell me about", "explain", "describe", "what is"
    ],

    QueryIntent.VIEW_SUMMARY: [
        "summary", "summarize", "overview", "brief", "give me summary",
        "explain this", "sum up", "recap", "high-level", "key points", "main points", "in a nutshell"
    ],

    QueryIntent.VIEW_DASHBOARD: [
        "dashboard", "metrics", "analytics", "kpis", "statistics",
        "performance", "insights", "report", "stats", "give me a dashboard", "show me a dashboard", "display a dashboard"
    ],

    QueryIntent.VIEW_TABLE: [
        "table", "data table", "spreadsheet", "grid", "matrix",
        "tabular format", "in a table", "as a table", "table view", "show me a table", "display a table", "give me a table", "list in a table", "show all in a table", "display all in a table", "list all in a table", "get all in a table", "find all in a table", "search all in a table", "show me all in a table", "display me all in a table", "give me all in a table"
    ],

    QueryIntent.VIEW_TRENDS: [
        "trends", "trending", "over time", "timeline", "history",
        "progression", "growth", "decline", "pattern", "show me trends", "display trends", "give me trends", "analyze trends", "what are the trends", "how are things trending", "show me how things are trending", "display how things are trending", "give me how things are trending", "analyze how things are trending"
    ],

    QueryIntent.VIEW_COMPARISON: [
        "compare", "comparison", "versus", "vs", "difference between",
        "contrast", "side by side", "compare these", "comparison of these", "versus these", "vs these", "difference between these", "contrast these", "side by side these", "compare all", "comparison of all", "versus all", "vs all", "difference between all", "contrast all", "side by side all"
    ],

    QueryIntent.VIEW_CARDS: [
        "cards", "card view", "as cards", "in cards", "card layout", "show me cards", "display cards", "give me cards", "list in cards", "show all in cards", "display all in cards", "list all in cards", "get all in cards", "find all in cards", "search all in cards", "show me all in cards", "display me all in cards", "give me all in cards", "show me in cards", "display me in cards", "give me in cards", "show in cards", "display in cards", "give in cards"
    ],

    QueryIntent.CREATE: [
        "create", "add", "new", "insert", "make a new"
    ],

    QueryIntent.UPDATE: [
        "update", "edit", "modify", "change", "revise"
    ],

    QueryIntent.DELETE: [
        "delete", "remove", "drop", "erase"
    ],

    QueryIntent.SEARCH: [
        "search", "find", "lookup", "locate"
    ]
}


# Object type keywords for fast detection
OBJECT_TYPE_KEYWORDS = {
    ObjectType.LEAD: ["lead", "leads", "prospect", "prospects"],
    ObjectType.CONTACT: ["contact", "contacts", "person", "people"],
    ObjectType.OPPORTUNITY: ["opportunity", "opportunities", "deal", "deals"],
    ObjectType.ACCOUNT: ["account", "accounts", "company", "companies", "organization"],
    ObjectType.ACTIVITY: ["activity", "activities", "task", "tasks", "event", "events"],
    ObjectType.CASE: ["case", "cases", "ticket", "tickets", "issue", "issues"],
    ObjectType.CAMPAIGN: ["campaign", "campaigns", "marketing"],
    ObjectType.PRODUCT: ["product", "products", "item", "items"],
    ObjectType.QUOTE: ["quote", "quotes", "quotation", "quotations"],
    ObjectType.INVOICE: ["invoice", "invoices", "bill", "bills"],
    ObjectType.GENERAL: ["general", "other"]
}


# Layout type keywords for fast detection
LAYOUT_KEYWORDS = {
    LayoutType.LIST: ["list", "show all", "display all", "view all"],
    LayoutType.TABLE: ["table", "spreadsheet", "grid", "tabular", "matrix"],
    LayoutType.DETAIL: ["detail", "details", "info", "information", "about"],
    LayoutType.CARD: ["card", "cards", "card view"],
    LayoutType.SUMMARY: ["summary", "overview", "summarize", "brief"],
    LayoutType.KPI: ["kpi", "metrics", "statistics", "stats", "numbers"],
    LayoutType.INSIGHTS: ["insights", "analysis", "analytics", "analyze"],
    LayoutType.CHART: ["chart", "graph", "visualization", "plot"],
    LayoutType.TIMELINE: ["timeline", "history", "activity", "chronological"],
    LayoutType.COMPOSITE: ["dashboard", "overview", "complete", "full view"],
}