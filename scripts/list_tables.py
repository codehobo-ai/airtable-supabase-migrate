#!/usr/bin/env python3
"""
Airtable Table Discovery
Automatically discovers all tables in your Airtable base
"""

import os
import sys
import json
import requests

def get_base_schema(base_id, token):
    """
    Get base schema using Airtable Meta API
    https://airtable.com/developers/web/api/get-base-schema
    """

    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("❌ Error: Permission denied")
            print("   Your token needs 'schema.bases:read' scope")
            print("   Create a new token at: https://airtable.com/create/tokens")
        elif e.response.status_code == 404:
            print(f"❌ Error: Base not found: {base_id}")
            print("   Check your base ID is correct")
        else:
            print(f"❌ Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def list_tables(base_id, token, verbose=True):
    """List all tables in the base"""

    if verbose:
        print("="*80)
        print("🔍 AIRTABLE TABLE DISCOVERY")
        print("="*80)
        print(f"\nBase ID: {base_id}")
        print("Fetching schema...\n")

    schema = get_base_schema(base_id, token)

    if not schema or 'tables' not in schema:
        return []

    tables = schema['tables']

    if verbose:
        print(f"✅ Found {len(tables)} tables:\n")
        print("-"*80)

        for i, table in enumerate(tables, 1):
            table_name = table['name']
            table_id = table['id']
            field_count = len(table.get('fields', []))

            print(f"{i:2}. {table_name:40} ({field_count} fields) [ID: {table_id}]")

        print("-"*80)

    return [table['name'] for table in tables]


def generate_table_names_list(tables):
    """Generate Python list format"""

    print("\n" + "="*80)
    print("📋 PYTHON LIST (copy to audit_formulas.py):")
    print("="*80)
    print("\nTABLE_NAMES = [")
    for table in tables:
        print(f"    '{table}',")
    print("]")


def generate_detailed_schema(base_id, token):
    """Generate detailed schema with field information"""

    schema = get_base_schema(base_id, token)

    if not schema or 'tables' not in schema:
        return

    print("\n" + "="*80)
    print("📊 DETAILED SCHEMA:")
    print("="*80)

    for table in schema['tables']:
        print(f"\n{'='*80}")
        print(f"📋 {table['name']} (ID: {table['id']})")
        print('='*80)

        if 'description' in table and table['description']:
            print(f"Description: {table['description']}")

        fields = table.get('fields', [])
        print(f"\nFields ({len(fields)}):")
        print("-"*80)

        for field in fields:
            field_name = field['name']
            field_type = field['type']
            field_id = field['id']

            # Detect formula/computed fields
            marker = ""
            if field_type == 'formula':
                marker = " 🔸 FORMULA"
            elif field_type == 'rollup':
                marker = " 🔸 ROLLUP"
            elif field_type == 'lookup':
                marker = " 🔸 LOOKUP"
            elif field_type == 'multipleRecordLinks':
                marker = " 🔗 LINKED"

            print(f"  • {field_name:35} [{field_type:20}]{marker}")

            # Show formula if available
            if field_type == 'formula' and 'options' in field:
                formula = field['options'].get('formula', '')
                if formula:
                    print(f"    Formula: {formula[:100]}...")

    # Save to JSON
    with open('airtable_schema.json', 'w') as f:
        json.dump(schema, indent=2, fp=f)

    print("\n" + "="*80)
    print("✅ Full schema saved to: airtable_schema.json")
    print("="*80)


def main():
    """Main function"""

    # Get credentials
    token = os.getenv('AIRTABLE_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID', 'appXxw3xiKyRARR2g')

    if not token:
        print("❌ Error: AIRTABLE_TOKEN not set")
        print("\nUsage:")
        print("  export AIRTABLE_TOKEN='patXXXXXXXX'")
        print("  python3 scripts/list_tables.py")
        print("\nOr:")
        print("  python3 scripts/list_tables.py patXXXXXX appYYYYYY")
        sys.exit(1)

    # Allow command-line args
    if len(sys.argv) > 1:
        token = sys.argv[1]
    if len(sys.argv) > 2:
        base_id = sys.argv[2]

    # List tables
    tables = list_tables(base_id, token, verbose=True)

    if not tables:
        print("\n❌ No tables found or error occurred")
        sys.exit(1)

    # Generate Python list
    generate_table_names_list(tables)

    # Ask if user wants detailed schema
    print("\n" + "="*80)
    print("Options:")
    print("  1. Run detailed schema analysis (shows all fields + formulas)")
    print("  2. Exit")
    print("="*80)

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == '1':
        generate_detailed_schema(base_id, token)

    print("\n✅ Done! Copy the TABLE_NAMES list to audit_formulas.py")


if __name__ == '__main__':
    main()
