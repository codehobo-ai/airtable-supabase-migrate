#!/usr/bin/env python3
"""
Airtable Formula Auditor
Automatically identifies formula fields and generates conversion plan
"""

import os
import json
from typing import Dict, List, Any
from pyairtable import Api
from collections import defaultdict
import re

class FormulaAuditor:
    def __init__(self, airtable_token, base_id):
        self.api = Api(airtable_token)
        self.base = self.api.base(base_id)
        self.base_id = base_id
        self.formula_fields = {}

    def analyze_base(self, table_names: List[str]):
        """Analyze all tables and identify formula fields"""

        print("="*80)
        print("🔍 AIRTABLE FORMULA AUDITOR")
        print("="*80)

        all_formulas = {}

        for table_name in table_names:
            print(f"\n📋 Analyzing table: {table_name}")
            print("-"*80)

            formulas = self.identify_formula_fields(table_name)
            all_formulas[table_name] = formulas

            if formulas:
                print(f"   Found {len(formulas)} computed fields")
            else:
                print(f"   No computed fields detected")

        return all_formulas

    def identify_formula_fields(self, table_name: str) -> Dict:
        """Identify formula/computed fields by analyzing data patterns"""

        table = self.base.table(table_name)

        # Fetch sample records
        try:
            records = table.all(max_records=50)
        except Exception as e:
            print(f"   ❌ Error fetching records: {e}")
            return {}

        if not records:
            print(f"   ⚠️  No records found in {table_name}")
            return {}

        # Get all field names from first record
        sample_fields = records[0]['fields']

        computed_fields = {}

        for field_name in sample_fields.keys():
            field_type = self.detect_field_type(field_name, records)

            if field_type['is_computed']:
                computed_fields[field_name] = field_type
                print(f"   🔸 {field_name:30} → {field_type['likely_type']:20} | {field_type['pattern']}")

        return computed_fields

    def detect_field_type(self, field_name: str, records: List) -> Dict:
        """Detect if field is computed and what type"""

        # Collect all values for this field
        values = []
        for record in records:
            value = record['fields'].get(field_name)
            if value is not None:
                values.append(value)

        if not values:
            return {'is_computed': False, 'likely_type': 'unknown'}

        sample_value = values[0]

        # Detection patterns
        result = {
            'is_computed': False,
            'likely_type': 'regular_field',
            'pattern': '',
            'sample_value': str(sample_value)[:100] if sample_value else None,
            'postgres_conversion': None
        }

        # 1. Check for rollup/lookup patterns (arrays of linked records)
        if isinstance(sample_value, list) and len(sample_value) > 0:
            if isinstance(sample_value[0], str) and sample_value[0].startswith('rec'):
                result['is_computed'] = False
                result['likely_type'] = 'linked_record'
                result['pattern'] = 'Linked records (many-to-many)'
                return result

        # 2. Check for numeric aggregations (likely SUM/COUNT/AVG)
        if isinstance(sample_value, (int, float)):
            # Check if it looks like a count (integers only)
            if all(isinstance(v, int) for v in values):
                # Check field name for hints
                if any(word in field_name.lower() for word in ['count', 'total', 'number', 'qty', 'quantity']):
                    result['is_computed'] = True
                    result['likely_type'] = 'rollup_count'
                    result['pattern'] = 'COUNT of linked records'
                    result['postgres_conversion'] = 'view_with_count'
                    return result

            # Check if it looks like a sum/average
            if any(word in field_name.lower() for word in ['total', 'sum', 'revenue', 'amount', 'avg', 'average']):
                result['is_computed'] = True
                result['likely_type'] = 'rollup_sum'
                result['pattern'] = 'SUM/AVG of linked records'
                result['postgres_conversion'] = 'view_with_aggregate'
                return result

        # 3. Check for date calculations
        if field_name.lower() in ['nights', 'days', 'duration', 'length']:
            result['is_computed'] = True
            result['likely_type'] = 'date_diff'
            result['pattern'] = 'DATETIME_DIFF calculation'
            result['postgres_conversion'] = 'generated_column'
            return result

        # 4. Check for concatenated strings
        if isinstance(sample_value, str):
            # Check if it looks like concatenated values
            if ' - ' in sample_value or ' | ' in sample_value:
                result['is_computed'] = True
                result['likely_type'] = 'concatenation'
                result['pattern'] = 'String concatenation'
                result['postgres_conversion'] = 'generated_column'
                return result

            # Check for status labels with emojis
            if any(emoji in sample_value for emoji in ['✅', '❌', '⏳', '🔴', '🟢', '🟡']):
                result['is_computed'] = True
                result['likely_type'] = 'conditional_label'
                result['pattern'] = 'IF/SWITCH conditional'
                result['postgres_conversion'] = 'generated_column'
                return result

        # 5. Check for boolean logic
        if isinstance(sample_value, bool):
            result['is_computed'] = True
            result['likely_type'] = 'boolean_formula'
            result['pattern'] = 'Boolean calculation'
            result['postgres_conversion'] = 'generated_column'
            return result

        return result

    def generate_conversion_plan(self, all_formulas: Dict) -> str:
        """Generate detailed conversion plan"""

        plan = []
        plan.append("\n" + "="*80)
        plan.append("📋 FORMULA CONVERSION PLAN")
        plan.append("="*80)

        # Count by type
        type_counts = defaultdict(int)
        for table_name, formulas in all_formulas.items():
            for field_name, field_info in formulas.items():
                type_counts[field_info['likely_type']] += 1

        plan.append("\n📊 SUMMARY:")
        plan.append(f"   Total computed fields: {sum(type_counts.values())}")
        for field_type, count in sorted(type_counts.items()):
            plan.append(f"   - {field_type}: {count}")

        # Detailed conversion for each table
        for table_name, formulas in all_formulas.items():
            if not formulas:
                continue

            plan.append(f"\n\n{'='*80}")
            plan.append(f"📋 TABLE: {table_name}")
            plan.append('='*80)

            for field_name, field_info in formulas.items():
                plan.append(f"\n🔸 {field_name}")
                plan.append(f"   Type: {field_info['likely_type']}")
                plan.append(f"   Pattern: {field_info['pattern']}")
                plan.append(f"   Sample: {field_info['sample_value']}")
                plan.append(f"   Strategy: {field_info['postgres_conversion'] or 'manual_review'}")

                # Generate SQL suggestion
                sql = self.suggest_postgres_conversion(
                    table_name,
                    field_name,
                    field_info
                )
                if sql:
                    plan.append(f"\n   SQL Suggestion:")
                    for line in sql.split('\n'):
                        plan.append(f"   {line}")

        # Action items
        plan.append("\n\n" + "="*80)
        plan.append("✅ ACTION ITEMS:")
        plan.append("="*80)
        plan.append("\n1. REVIEW: Manually verify detected formulas in Airtable UI")
        plan.append("2. MIGRATE: Store computed values during initial migration")
        plan.append("3. IMPLEMENT: Add PostgreSQL generated columns/views")
        plan.append("4. VERIFY: Compare Airtable vs PostgreSQL results")
        plan.append("5. CLEANUP: Remove snapshot fields once verified")

        return '\n'.join(plan)

    def suggest_postgres_conversion(self, table_name: str, field_name: str, field_info: Dict) -> str:
        """Generate PostgreSQL conversion SQL"""

        pg_table = table_name.lower()
        pg_field = field_name.lower().replace(' ', '_').replace('#', 'num')

        field_type = field_info['likely_type']

        if field_type == 'date_diff':
            return f"""ALTER TABLE {pg_table}
     ADD COLUMN {pg_field} integer
     GENERATED ALWAYS AS (
       EXTRACT(DAY FROM check_out - check_in)
     ) STORED;"""

        elif field_type == 'rollup_count':
            # Guess the linked table from field name
            return f"""CREATE VIEW {pg_table}_with_metrics AS
   SELECT
     t.*,
     COUNT(linked.id) as {pg_field}
   FROM {pg_table} t
   LEFT JOIN linked_table linked ON linked.{pg_table}_id = t.id
   GROUP BY t.id;"""

        elif field_type == 'rollup_sum':
            return f"""CREATE VIEW {pg_table}_with_metrics AS
   SELECT
     t.*,
     COALESCE(SUM(linked.amount), 0) as {pg_field}
   FROM {pg_table} t
   LEFT JOIN linked_table linked ON linked.{pg_table}_id = t.id
   GROUP BY t.id;"""

        elif field_type == 'conditional_label':
            return f"""ALTER TABLE {pg_table}
     ADD COLUMN {pg_field} text
     GENERATED ALWAYS AS (
       CASE
         WHEN status = 'confirmed' THEN '✅ Confirmed'
         WHEN status = 'pending' THEN '⏳ Pending'
         ELSE '❌ Other'
       END
     ) STORED;"""

        elif field_type == 'concatenation':
            return f"""ALTER TABLE {pg_table}
     ADD COLUMN {pg_field} text
     GENERATED ALWAYS AS (
       field1 || ' - ' || field2
     ) STORED;"""

        return None

    def export_report(self, all_formulas: Dict, plan: str):
        """Export detailed JSON report and plan"""

        # Export JSON
        with open('airtable_formulas.json', 'w') as f:
            json.dump(all_formulas, indent=2, fp=f)
        print("\n✅ Detailed report saved: airtable_formulas.json")

        # Export plan
        with open('conversion_plan.txt', 'w') as f:
            f.write(plan)
        print("✅ Conversion plan saved: conversion_plan.txt")

        # Export SQL template
        sql_lines = []
        sql_lines.append("-- Airtable Formula Conversion SQL")
        sql_lines.append("-- Generated automatically - REVIEW BEFORE RUNNING\n")

        for table_name, formulas in all_formulas.items():
            sql_lines.append(f"\n-- {table_name}")
            sql_lines.append("-" * 60)

            for field_name, field_info in formulas.items():
                sql = self.suggest_postgres_conversion(table_name, field_name, field_info)
                if sql:
                    sql_lines.append(f"\n-- {field_name}")
                    sql_lines.append(sql)

        with open('formula_conversion.sql', 'w') as f:
            f.write('\n'.join(sql_lines))
        print("✅ SQL template saved: formula_conversion.sql")


def main():
    """Run the formula auditor"""

    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'appXxw3xiKyRARR2g')

    if not AIRTABLE_TOKEN:
        print("❌ Error: AIRTABLE_TOKEN not set")
        print("   Set it with: export AIRTABLE_TOKEN='patXXXXXX'")
        return

    # Option 1: Auto-discover tables
    TABLE_NAMES = None  # Set to None to auto-discover

    # Option 2: Manually specify tables
    # TABLE_NAMES = [
    #     'Reservations',
    #     'Transactions',
    # ]

    # Auto-discover if not specified
    if TABLE_NAMES is None:
        print("🔍 Auto-discovering tables...")
        try:
            from list_tables import list_tables
            TABLE_NAMES = list_tables(BASE_ID, AIRTABLE_TOKEN, verbose=False)
            print(f"✅ Found {len(TABLE_NAMES)} tables: {', '.join(TABLE_NAMES)}\n")
        except Exception as e:
            print(f"❌ Auto-discovery failed: {e}")
            print("   Please specify TABLE_NAMES manually in the script")
            return

    print(f"🔧 Configuration:")
    print(f"   Base ID: {BASE_ID}")
    print(f"   Tables: {', '.join(TABLE_NAMES)}")
    print()

    auditor = FormulaAuditor(AIRTABLE_TOKEN, BASE_ID)

    # Analyze all tables
    all_formulas = auditor.analyze_base(TABLE_NAMES)

    # Generate conversion plan
    plan = auditor.generate_conversion_plan(all_formulas)
    print(plan)

    # Export reports
    auditor.export_report(all_formulas, plan)

    print("\n" + "="*80)
    print("✅ AUDIT COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Review: airtable_formulas.json")
    print("2. Read: conversion_plan.txt")
    print("3. Edit: formula_conversion.sql (update table/field names)")
    print("4. Run SQL in Supabase after migration")


if __name__ == '__main__':
    main()
