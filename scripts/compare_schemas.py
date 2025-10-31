#!/usr/bin/env python3
"""
Compare two Airtable schemas and detect changes
"""

import json
import sys

def compare_schemas(old_schema_path, new_schema_path):
    """Compare two schema files and report differences"""

    with open(old_schema_path) as f:
        old_schema = json.load(f)

    with open(new_schema_path) as f:
        new_schema = json.load(f)

    old_tables = {t['id']: t for t in old_schema.get('tables', [])}
    new_tables = {t['id']: t for t in new_schema.get('tables', [])}

    changes = []

    # Check for new tables
    for table_id, table in new_tables.items():
        if table_id not in old_tables:
            changes.append(f"➕ NEW TABLE: {table['name']}")

    # Check for removed tables
    for table_id, table in old_tables.items():
        if table_id not in new_tables:
            changes.append(f"➖ REMOVED TABLE: {table['name']}")

    # Check for field changes in existing tables
    for table_id in set(old_tables.keys()) & set(new_tables.keys()):
        old_table = old_tables[table_id]
        new_table = new_tables[table_id]

        old_fields = {f['id']: f for f in old_table.get('fields', [])}
        new_fields = {f['id']: f for f in new_table.get('fields', [])}

        table_name = new_table['name']

        # New fields
        for field_id, field in new_fields.items():
            if field_id not in old_fields:
                changes.append(f"   ➕ {table_name}: New field '{field['name']}' ({field['type']})")

        # Removed fields
        for field_id, field in old_fields.items():
            if field_id not in new_fields:
                changes.append(f"   ➖ {table_name}: Removed field '{field['name']}'")

        # Changed field types
        for field_id in set(old_fields.keys()) & set(new_fields.keys()):
            old_field = old_fields[field_id]
            new_field = new_fields[field_id]

            if old_field['type'] != new_field['type']:
                changes.append(f"   🔄 {table_name}: '{new_field['name']}' type changed: {old_field['type']} → {new_field['type']}")

    if changes:
        print("\n".join(changes))
    else:
        print("No schema changes detected")

    return len(changes)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 compare_schemas.py <old_schema.json> <new_schema.json>")
        sys.exit(1)

    change_count = compare_schemas(sys.argv[1], sys.argv[2])
    sys.exit(0 if change_count == 0 else 1)
