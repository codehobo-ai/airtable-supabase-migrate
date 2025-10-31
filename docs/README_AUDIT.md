# Airtable Formula Auditor - Quick Start

## Prerequisites

1. **Python 3.8+** ✅ (You have Python 3.12.3)
2. **Airtable Personal Access Token** (Get from: https://airtable.com/create/tokens)
3. **Airtable Base ID** (Found in URL: `https://airtable.com/appXXXXXXXX`)

## Setup

### Step 1: Install Dependencies

```bash
cd /home/megaboss/Projects-Cursor/n8n-claude
python3 -m pip install --user -r scripts/requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

**Required values in `.env`:**
```env
AIRTABLE_TOKEN=patYourPersonalAccessToken
AIRTABLE_BASE_ID=appXxw3xiKyRARR2g
```

### Step 3: Edit Table Names

Open `scripts/audit_formulas.py` and update the `TABLE_NAMES` list (around line 209):

```python
TABLE_NAMES = [
    'Reservations',
    'Transactions',
    'Properties',        # Add your tables here
    'Guests',
    # etc...
]
```

## Running the Auditor

### Option 1: Using environment variables

```bash
export AIRTABLE_TOKEN="patYourToken"
export AIRTABLE_BASE_ID="appYourBaseId"
python3 scripts/audit_formulas.py
```

### Option 2: Using .env file

```bash
python3 -c "
from dotenv import load_dotenv
load_dotenv()
exec(open('scripts/audit_formulas.py').read())
"
```

### Option 3: Direct run (edit script first)

```bash
# Edit the script and hardcode your token temporarily
python3 scripts/audit_formulas.py
```

## Output Files

After running, you'll get 3 files:

1. **`airtable_formulas.json`** - Detailed analysis in JSON format
2. **`conversion_plan.txt`** - Human-readable conversion plan
3. **`formula_conversion.sql`** - SQL templates for Supabase

## Example Output

```
================================================================================
🔍 AIRTABLE FORMULA AUDITOR
================================================================================

📋 Analyzing table: Reservations
--------------------------------------------------------------------------------
   🔸 Nights                          → date_diff            | DATETIME_DIFF calculation
   🔸 Total Revenue                   → rollup_sum           | SUM of linked records
   🔸 Status Label                    → conditional_label    | IF/SWITCH conditional
   Found 3 computed fields

📋 Analyzing table: Transactions
--------------------------------------------------------------------------------
   🔸 Tax Amount                      → rollup_sum           | SUM of linked records
   Found 1 computed fields
```

## What It Detects

✅ **Date calculations** (DATETIME_DIFF)
✅ **Rollup formulas** (SUM, COUNT, AVG)
✅ **Conditional logic** (IF, SWITCH)
✅ **String concatenation**
✅ **Boolean formulas**
✅ **Linked records**

## Next Steps

1. **Review** the generated files
2. **Verify** detected formulas in Airtable UI
3. **Update** `formula_conversion.sql` with correct table/field names
4. **Run** the SQL in Supabase after migration
5. **Test** that PostgreSQL formulas match Airtable results

## Troubleshooting

### "AIRTABLE_TOKEN not set"
Make sure you've exported the environment variable or created a `.env` file.

### "No records found"
Check that your table names are correct (case-sensitive).

### "Permission denied"
Make sure your token has read access to the base.

### Fields not detected as formulas
Some formulas look like regular fields. Manually verify in Airtable UI and document them in the conversion plan.

## Get Your Airtable Token

1. Go to: https://airtable.com/create/tokens
2. Click "Create new token"
3. Name it: "Migration Auditor"
4. Scopes needed:
   - `data.records:read`
   - `schema.bases:read`
5. Add access to your base
6. Copy the token (starts with `pat...`)

## Need Help?

Check the Airtable API docs: https://airtable.com/developers/web/api/introduction
