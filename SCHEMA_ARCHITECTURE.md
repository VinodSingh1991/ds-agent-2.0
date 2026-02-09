# 🏗️ Schema Architecture: How Query, Pattern, and Component Schemas Work Together

## 📊 Overview

The Disposable UI Agent uses **three core JSON schema types** that work together in a pipeline to generate UI layouts from natural language queries:

1. **Query Schemas** - Understand what the user wants
2. **Pattern Schemas** - Find the best UI pattern to use
3. **Component Schemas** - Build the actual UI components

---

## 🔄 The Complete Flow

```
User Query → Query Analysis → Pattern Retrieval → Component Generation → Final Layout
```

---

## 1️⃣ Query Schemas (`query_schemas.py`)

### Purpose
Analyze and structure the user's natural language query into machine-readable format.

### Key Schema: `QueryAnalysis`

**Input Example:**
```
"show me top 10 high-value leads with revenue over $50,000, sorted by revenue descending"
```

**Output Example:**
```json
{
  "object_type": "lead",
  "intent": "view_list",
  "layout_type": "list",
  "filters": [
    {
      "field": "revenue",
      "operator": ">",
      "value": 50000
    }
  ],
  "sort": "revenue DESC",
  "limit": 10,
  "fields_mentioned": ["revenue"],
  "fields_required": ["name", "revenue", "status"],
  "reasoning": "User wants a filtered, sorted list of leads with revenue threshold"
}
```

### Key Fields
- `object_type` - What CRM object (lead, contact, opportunity)
- `intent` - What action (view_list, view_detail, view_dashboard)
- `layout_type` - Best layout (list, table, dashboard, grid)
- `filters` - Array of filter conditions
- `sort` - Sorting specification
- `limit` - Number of records to show

---

## 2️⃣ Pattern Schemas (`pattern_schemas.py`)

### Purpose
Select the best UI pattern based on query analysis and available data.

### Key Schema: `PatternMetadata`

**Pattern Database Example** (`component_patterns_metadata.json`):
```json
{
  "pattern_id": "user_avatar_list",
  "pattern_name": "User Avatar List Pattern",
  "description": "Display a list of people/users with avatars, names, and metadata",
  "use_cases": [
    "contact list with photos",
    "lead list with avatars",
    "team member directory"
  ],
  "data_requirements": {
    "min_fields": ["name"],
    "recommended_fields": ["avatar_url", "role", "status", "company"]
  },
  "schema_structure": {
    "type": "Stack",
    "props": {"direction": "vertical", "gap": "small"},
    "children": [
      {
        "type": "ListCard",
        "repeat": "data",
        "children": [
          {"type": "Avatar", "binds_to": "avatar_url"},
          {"type": "Heading", "binds_to": "name", "level": 3},
          {"type": "Text", "binds_to": "role"},
          {"type": "Badge", "binds_to": "status"}
        ]
      }
    ]
  }
}
```

### Pattern Selection Output
```json
{
  "pattern_id": "user_avatar_list",
  "pattern_name": "User Avatar List Pattern",
  "confidence": 0.92,
  "reasoning": "Query requests a list of leads. Data includes name and status fields. Pattern matches requirements.",
  "required_components": ["Stack", "ListCard", "Avatar", "Heading", "Badge"],
  "data_requirements_met": true,
  "missing_fields": [],
  "alternative_patterns": ["simple_list", "table_view"]
}
```

---

## 3️⃣ Component Schemas (`component_schemas.py`)

### Purpose
Define the actual UI components that will be rendered.

### Key Schema: `Component`

**Component Structure:**
```json
{
  "type": "Stack",
  "props": {
    "direction": "vertical",
    "gap": "medium"
  },
  "children": [
    {
      "type": "ListCard",
      "repeat": "data",
      "children": [
        {
          "type": "Avatar",
          "binds_to": "avatar_url",
          "optional": true
        },
        {
          "type": "Heading",
          "binds_to": "name",
          "props": {"level": 3}
        },
        {
          "type": "Metric",
          "binds_to": "revenue",
          "props": {"format": "currency", "size": "large"}
        },
        {
          "type": "Badge",
          "binds_to": "status",
          "props": {"variant": "outlined"}
        }
      ]
    }
  ]
}
```

### Component Features

1. **Data Binding** - `binds_to: "field_name"`
   - Connects component to data field
   - Example: `{"type": "Heading", "binds_to": "name"}`

2. **Static Values** - `value: {...}`
   - Fixed content not from data
   - Example: `{"type": "Text", "value": "Welcome"}`

3. **Repetition** - `repeat: "data"`
   - Repeats component for each data item
   - Example: `{"type": "ListCard", "repeat": "data"}`

4. **Hierarchy** - `children: [...]`
   - Nested components
   - Example: Stack contains Cards, Cards contain Text

5. **Props** - `props: {...}`
   - Component configuration
   - Example: `{"level": 3, "variant": "primary"}`

---

## 🔗 How They Work Together: Complete Example

### Step 1: User Input
```
Query: "show me top 10 high-value leads with revenue over $50,000"
Data: [{id: 1, name: "Acme Corp", revenue: 125000, status: "active", avatar_url: "..."}]
```

### Step 2: Query Analysis (QueryAnalysis Schema)
```json
{
  "object_type": "lead",
  "intent": "view_list",
  "layout_type": "list",
  "filters": [{"field": "revenue", "operator": ">", "value": 50000}],
  "sort": "revenue DESC",
  "limit": 10,
  "fields_mentioned": ["revenue"],
  "fields_required": ["name", "revenue", "status", "avatar_url"]
}
```

### Step 3: Pattern Retrieval (PatternMetadata Schema)

**Vector Search in Pattern Database:**
- Searches `component_patterns_metadata.json`
- Searches `query_patterns_metadata.json`
- Searches `layout_patterns_metadata.json`

**Selected Pattern:**
```json
{
  "pattern_id": "user_avatar_list",
  "pattern_name": "User Avatar List Pattern",
  "confidence": 0.92,
  "reasoning": "Query requests a list view. Data has avatar_url field. Pattern supports revenue metrics.",
  "required_components": ["Stack", "ListCard", "Avatar", "Heading", "Metric", "Badge"],
  "data_requirements_met": true
}
```

### Step 4: Component Generation (Component Schema)

**Generated Layout:**
```json
{
  "id": "layout_leads_001",
  "query": "show me top 10 high-value leads with revenue over $50,000",
  "object_type": "lead",
  "layout_type": "list",
  "sections": [
    {
      "id": "section_main",
      "title": "High-Value Leads",
      "components": [
        {
          "type": "Stack",
          "props": {"direction": "vertical", "gap": "medium"},
          "children": [
            {
              "type": "ListCard",
              "repeat": "data",
              "children": [
                {
                  "type": "Avatar",
                  "binds_to": "avatar_url",
                  "optional": true,
                  "props": {"size": "medium"}
                },
                {
                  "type": "Heading",
                  "binds_to": "name",
                  "props": {"level": 3, "weight": "semibold"}
                },
                {
                  "type": "Metric",
                  "binds_to": "revenue",
                  "props": {"format": "currency", "size": "large"}
                },
                {
                  "type": "Badge",
                  "binds_to": "status",
                  "props": {"variant": "outlined"}
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "data": [
    {"id": 1, "name": "Acme Corp", "revenue": 125000, "status": "active"}
  ],
  "metadata": {
    "pattern_used": "user_avatar_list",
    "components_count": 5,
    "data_fields_used": ["name", "revenue", "status", "avatar_url"]
  }
}
```

### Step 5: UI Rendering

The frontend receives this JSON and renders:

```jsx
<Stack direction="vertical" gap="medium">
  {data.map(item => (
    <ListCard key={item.id}>
      <Avatar src={item.avatar_url} size="medium" />
      <Heading level={3} weight="semibold">{item.name}</Heading>
      <Metric value={item.revenue} format="currency" size="large" />
      <Badge variant="outlined">{item.status}</Badge>
    </ListCard>
  ))}
</Stack>
```

---

## 📁 Pattern Database Files

### 1. `component_patterns_metadata.json`
**Purpose:** Defines reusable UI patterns with their component structures

**Contains:**
- Pattern definitions (user_avatar_list, metric_dashboard, data_table, etc.)
- Component requirements
- Data requirements
- Schema structures (templates)

**Example Patterns:**
- `user_avatar_list` - List with avatars and metadata
- `metric_dashboard` - Dashboard with KPI metrics
- `data_table_pattern` - Sortable data tables
- `birthday_celebration` - Special event cards
- `empty_state` - No data placeholders

### 2. `query_patterns_metadata.json`
**Purpose:** Maps query types to layout patterns

**Contains:**
- Query examples and variants
- Query decomposition (intent, filters, sorting)
- Selected layout mappings
- Adaptations made

**Example Mappings:**
- "show top leads" → sorted_list_with_metrics
- "sales dashboard" → metric_dashboard
- "upcoming birthdays" → birthday_celebration

### 3. `layout_patterns_metadata.json`
**Purpose:** Complete layout examples with metadata

**Contains:**
- Full layout definitions
- Metadata (object_type, view_type, complexity)
- Component usage
- Data requirements

**Example Layouts:**
- Lead List with Avatar and Status
- Contact Table with Sorting
- Sales Dashboard with Metrics
- Opportunity Pipeline View

---

## 🎯 Key Concepts

### 1. Data Binding
Components connect to data fields using `binds_to`:
```json
{"type": "Heading", "binds_to": "name"}
```
This tells the UI to display the `name` field from each data record.

### 2. Repetition
Components repeat for arrays using `repeat`:
```json
{"type": "ListCard", "repeat": "data", "children": [...]}
```
This creates one ListCard for each item in the data array.

### 3. Optional Fields
Components can be optional if data is missing:
```json
{"type": "Avatar", "binds_to": "avatar_url", "optional": true}
```
If `avatar_url` is null/missing, the Avatar won't render.

### 4. Props Configuration
Components are configured using `props`:
```json
{"type": "Metric", "props": {"format": "currency", "size": "large"}}
```
This tells the Metric component to format as currency and display large.

### 5. Hierarchical Structure
Components nest using `children`:
```json
{
  "type": "Stack",
  "children": [
    {"type": "Card", "children": [{"type": "Text"}]}
  ]
}
```

---

## 🚀 Testing the Complete Flow

Try this comprehensive query to see all schemas in action:

```json
{
  "query": "show me the top 10 high-value leads with revenue over $50,000, sorted by revenue descending, and highlight any leads from the technology sector that have been contacted in the last 30 days",
  "data": [
    {
      "id": 1,
      "name": "Acme Corp",
      "revenue": 125000,
      "status": "active",
      "sector": "technology",
      "last_contact": "2026-01-15",
      "contact_person": "John Smith",
      "email": "john@acmecorp.com",
      "avatar_url": "https://example.com/avatar1.jpg"
    }
  ]
}
```

**What happens:**
1. **Query Analysis** extracts: filters (revenue > 50k, sector = tech, date range), sorting (revenue DESC), limit (10)
2. **Pattern Retrieval** finds: user_avatar_list pattern (best for lead lists with metadata)
3. **Component Generation** creates: Stack → ListCard (repeating) → Avatar + Heading + Metric + Badge
4. **UI Renders** the final layout with all data bound correctly

---

## 📚 Schema Files Reference

| File | Purpose | Used By |
|------|---------|---------|
| `query_schemas.py` | Define query analysis structure | QueryAnalyzer |
| `pattern_schemas.py` | Define pattern selection structure | CandidateRetriever |
| `component_schemas.py` | Define UI component structure | LayoutGenerator |
| `layout_schemas.py` | Define complete layout structure | LayoutGenerator |
| `component_patterns_metadata.json` | Pattern database | Vector Store |
| `query_patterns_metadata.json` | Query mapping database | Vector Store |
| `layout_patterns_metadata.json` | Layout examples database | Vector Store |

---

## 🎓 Summary

The three schema types work together in a pipeline:

1. **Query Schemas** understand the user's intent and extract structured information
2. **Pattern Schemas** select the best UI pattern based on query analysis and data
3. **Component Schemas** build the actual UI components using the selected pattern

This separation of concerns follows SOLID principles and makes the system:
- ✅ **Modular** - Each schema has a single responsibility
- ✅ **Extensible** - Easy to add new patterns or components
- ✅ **Type-Safe** - Pydantic validates all schemas
- ✅ **Testable** - Each stage can be tested independently
- ✅ **Maintainable** - Clear separation makes debugging easier


