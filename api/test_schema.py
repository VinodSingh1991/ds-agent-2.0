"""Test script to check the generated JSON schema"""
import json
from agent.schemas.layout_schemas import LayoutResponse, get_openai_schema

print("="*60)
print("TESTING OPENAI SCHEMA GENERATION")
print("="*60)

# Generate the OpenAI schema
schema = get_openai_schema()

print("\nGenerated OpenAI Schema:")
print(json.dumps(schema, indent=2))

print("\n" + "="*60)
print("CHECKING SCHEMA VALIDITY FOR OPENAI:")
print("="*60)

# Check strict mode
print(f"\nStrict mode: {schema.get('strict', False)}")

# Check required fields
if 'required' in schema:
    print(f"\nRequired fields: {schema['required']}")
else:
    print("\n⚠️  No 'required' field in schema!")

# Check properties
if 'properties' in schema:
    print(f"\nProperties: {list(schema['properties'].keys())}")
else:
    print("\n⚠️  No 'properties' field in schema!")

# Check sections
if 'properties' in schema and 'sections' in schema['properties']:
    sections_schema = schema['properties']['sections']
    print(f"\nSections schema:")
    print(f"  - Type: {sections_schema.get('type')}")
    if 'items' in sections_schema:
        items = sections_schema['items']
        print(f"  - Items type: {items.get('type')}")
        print(f"  - Items additionalProperties: {items.get('additionalProperties')}")
        if 'properties' in items and 'rows' in items['properties']:
            rows = items['properties']['rows']
            print(f"  - Rows type: {rows.get('type')}")
            if 'items' in rows:
                print(f"  - Rows items type: {rows['items'].get('type')}")
                print(f"  - Rows items additionalProperties: {rows['items'].get('additionalProperties')}")

# Check metadata
if 'properties' in schema and 'metadata' in schema['properties']:
    metadata_schema = schema['properties']['metadata']
    print(f"\nMetadata schema:")
    if 'anyOf' in metadata_schema:
        print(f"  - Has anyOf with {len(metadata_schema['anyOf'])} variants")
        for i, variant in enumerate(metadata_schema['anyOf']):
            print(f"  - Variant {i}: type={variant.get('type')}, additionalProperties={variant.get('additionalProperties')}")
    else:
        print(f"  - Type: {metadata_schema.get('type')}")
        print(f"  - additionalProperties: {metadata_schema.get('additionalProperties')}")

print("\n" + "="*60)
print("✅ Schema generation complete!")
print("="*60)

