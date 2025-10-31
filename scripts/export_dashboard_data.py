#!/usr/bin/env python3
"""
Export dashboard data as JSON for Netlify functions
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def export_data(output_file):
    """Export dashboard data to JSON"""

    # Load audit data
    formulas = []
    try:
        with open('./data/audit/airtable_formulas.json') as f:
            data = json.load(f)

            for table_name, fields in data.items():
                for field_name, field_info in fields.items():
                    formulas.append({
                        'table': table_name,
                        'field': field_name,
                        'type': field_info.get('likely_type'),
                        'pattern': field_info.get('pattern'),
                        'sample': str(field_info.get('sample_value', ''))[:100]
                    })
    except FileNotFoundError:
        print("⚠️  No audit data found")

    # Load sync history
    sync_history = []
    # TODO: Parse actual logs
    sync_history.append({
        'date': datetime.now().isoformat(),
        'records': 1250,
        'mode': 'incremental',
        'status': 'success'
    })

    # Build stats
    stats = {
        'total_tables': len(set(f['table'] for f in formulas)),
        'formula_count': len(formulas),
        'last_sync_records': sync_history[0]['records'] if sync_history else 0,
        'last_sync_date': sync_history[0]['date'] if sync_history else None,
        'sync_status': sync_history[0]['status'] if sync_history else 'unknown',
        'last_updated': datetime.now().isoformat()
    }

    # Export
    output = {
        'stats': stats,
        'formulas': formulas,
        'sync_history': sync_history,
        'schema_changes': [],
        'last_updated': datetime.now().isoformat()
    }

    with open(output_file, 'w') as f:
        json.dump(output, indent=2, fp=f)

    print(f"✅ Exported dashboard data to {output_file}")
    print(f"   Stats: {stats}")
    print(f"   Formulas: {len(formulas)}")
    print(f"   Sync history: {len(sync_history)}")

def main():
    parser = argparse.ArgumentParser(description='Export dashboard data')
    parser.add_argument('--output', default='./dashboard-data.json')
    args = parser.parse_args()

    export_data(args.output)

if __name__ == '__main__':
    main()
