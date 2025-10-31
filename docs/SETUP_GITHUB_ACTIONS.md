# GitHub Actions Setup Guide

## Overview

This repository includes automated workflows for:
1. **Schema Auditing** - Monitor Airtable schema changes
2. **Data Syncing** - Automated Airtable → Supabase migration
3. **Notifications** - Email alerts for changes and failures

---

## Quick Setup (5 minutes)

### Step 1: Add Secrets to GitHub

Go to: **Repository Settings → Secrets and variables → Actions**

Add these secrets:

```
AIRTABLE_TOKEN          = patYourPersonalAccessToken
AIRTABLE_BASE_ID        = appXxw3xiKyRARR2g
SUPABASE_URL            = https://your-project.supabase.co
SUPABASE_KEY            = eyXXXXXXXXXXXXXXXXXX
NOTIFICATION_EMAIL      = your-email@example.com
SMTP_USERNAME           = your-smtp@gmail.com (optional)
SMTP_PASSWORD           = your-app-password (optional)
```

### Step 2: Enable GitHub Actions

1. Go to **Actions** tab
2. Enable workflows if prompted
3. You should see 2 workflows:
   - `Airtable Schema Audit`
   - `Airtable to Supabase Sync`

### Step 3: Run Your First Audit

1. Go to **Actions** tab
2. Select **Airtable Schema Audit**
3. Click **Run workflow**
4. Select options:
   - Action: `audit_formulas`
   - Send email: `true`
5. Click **Run workflow**

---

## Workflows Available

### 1. Airtable Schema Audit

**File:** `.github/workflows/airtable-audit.yml`

**Triggers:**
- ✅ Manual (on-demand)
- ✅ Scheduled (weekly on Mondays at 9 AM)
- ✅ On push to main branch

**Actions:**
- `audit_formulas` - Analyze all formula fields
- `list_tables` - List all tables in base
- `full_schema` - Generate complete schema
- `compare_changes` - Compare with previous run

**Outputs:**
- Formula conversion plan (TXT)
- Full schema (JSON)
- SQL conversion templates
- Downloadable artifacts (90 days)

**Use Cases:**
- Monitor schema changes
- Track formula modifications
- Plan migration updates
- Documentation

---

### 2. Airtable to Supabase Sync

**File:** `.github/workflows/airtable-sync.yml`

**Triggers:**
- ✅ Manual (on-demand)
- ✅ Scheduled (daily at 2 AM)
- ✅ Callable from other workflows

**Modes:**
- `test` - Sync 10 records (safe testing)
- `preview` - Dry run with 100 records
- `incremental` - Sync only new/changed records
- `full` - Complete migration (with backup)

**Features:**
- ✅ Pre-flight connection checks
- ✅ Automatic backups before full sync
- ✅ Verification after sync
- ✅ Email notifications
- ✅ Automatic rollback on failure

**Outputs:**
- Migration logs
- Verification reports
- Backup files (if full sync)

---

## Manual Trigger Examples

### Run Schema Audit

```bash
# Via GitHub CLI (if installed)
gh workflow run airtable-audit.yml \
  -f action=audit_formulas \
  -f notify_email=true

# Or via web UI
# Actions → Airtable Schema Audit → Run workflow
```

### Run Incremental Sync

```bash
gh workflow run airtable-sync.yml \
  -f mode=incremental \
  -f notify=true

# Or via web UI
# Actions → Airtable to Supabase Sync → Run workflow
```

### Test with Specific Tables

```bash
gh workflow run airtable-sync.yml \
  -f mode=test \
  -f tables="Reservations,Transactions" \
  -f notify=false
```

---

## Scheduled Operations

### Current Schedule

| Workflow | Frequency | Time (UTC) | Purpose |
|----------|-----------|------------|---------|
| Schema Audit | Weekly | Mon 9:00 AM | Track schema changes |
| Data Sync | Daily | 2:00 AM | Keep Supabase updated |

### Customize Schedule

Edit the cron expression in workflow files:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM
  # - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 */6 * * *'   # Every 6 hours
  # - cron: '0 0 * * 0'     # Weekly on Sunday
```

**Cron syntax:** `minute hour day month weekday`

---

## Notifications

### Email Setup (Gmail)

1. **Enable 2FA** on your Gmail account
2. **Create App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - App: "Mail"
   - Device: "GitHub Actions"
   - Copy the password
3. **Add to GitHub Secrets:**
   ```
   SMTP_USERNAME = your-email@gmail.com
   SMTP_PASSWORD = your-16-char-app-password
   NOTIFICATION_EMAIL = recipient@example.com
   ```

### Notification Events

You'll receive emails for:
- ✅ Successful syncs (summary + stats)
- ❌ Failed syncs (with error logs)
- ⚠️ Schema changes detected
- 📊 Weekly audit reports

---

## Monitoring & Alerts

### View Workflow Status

```bash
# List recent runs
gh run list --workflow=airtable-sync.yml

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

### Check Logs

1. Go to **Actions** tab
2. Click on workflow run
3. Expand job steps
4. View logs inline or download

### Schema Change Alerts

When schema changes are detected:
1. GitHub Issue is automatically created
2. Email notification sent
3. Labels: `airtable`, `schema-change`, `automated`

---

## Advanced Features

### Auto-create Issues on Schema Change

```yaml
- name: Create Issue on Schema Change
  uses: actions/github-script@v7
  # Automatically creates issue when schema changes
```

### Backup & Rollback

```yaml
- name: Backup Supabase Data
  # Creates backup before full migration

- name: Rollback on Failure
  # Restores from backup if migration fails
```

### Artifact Retention

- **Audit reports:** 90 days
- **Migration logs:** 30 days
- **Previous schema:** 365 days

---

## Security Best Practices

### ✅ DO
- Use GitHub Secrets for all credentials
- Enable 2FA on all accounts
- Use read-only tokens where possible
- Review workflow logs regularly
- Test in `test` or `preview` mode first

### ❌ DON'T
- Commit tokens to repository
- Use production tokens for testing
- Run `full` sync without testing
- Ignore failure notifications
- Skip backups for full migrations

---

## Troubleshooting

### "Secret not found"

**Solution:**
```bash
# Verify secrets are set
gh secret list

# Add missing secret
gh secret set AIRTABLE_TOKEN
```

### "Workflow permission denied"

**Solution:**
1. Settings → Actions → General
2. Workflow permissions → Read and write
3. Save

### "Email notification failed"

**Solution:**
- Verify SMTP credentials
- Check Gmail app password (not regular password)
- Ensure "Less secure apps" is OFF (use app password)

### "Migration timeout"

**Solution:**
- Increase timeout in workflow (default: 60 min)
- Use `incremental` mode instead of `full`
- Sync specific tables only

---

## Cost Considerations

### GitHub Actions

- **Free tier:** 2,000 minutes/month
- **Average run time:**
  - Schema audit: ~2-3 minutes
  - Test sync: ~3-5 minutes
  - Full sync (90k records): ~15-20 minutes

**Monthly usage estimate:**
- Daily incremental sync: ~4 min × 30 days = 120 min
- Weekly audit: ~3 min × 4 weeks = 12 min
- **Total:** ~132 min/month (well within free tier)

### Airtable API

- **Free tier:** 5 requests/second
- **Script stays within limits**

### Supabase

- **Free tier:** 500 MB database
- **Check your data size**

---

## Next Steps

1. ✅ **Run first audit** (manual trigger)
2. ✅ **Test with 10 records** (test mode)
3. ✅ **Review output artifacts**
4. ✅ **Set up email notifications**
5. ✅ **Schedule regular syncs**
6. ✅ **Monitor for schema changes**

---

## Support

- **GitHub Discussions:** Ask questions
- **Issues:** Report bugs
- **Actions Logs:** Debug workflows
- **Documentation:** This file!

---

## Example: Complete First Run

```bash
# 1. Setup
git clone <repo>
cd n8n-claude

# 2. Add secrets (via web UI)
# Repository → Settings → Secrets → Actions

# 3. Run audit
gh workflow run airtable-audit.yml \
  -f action=audit_formulas

# 4. Check status
gh run list

# 5. Download results
gh run download <run-id>

# 6. Review files
cat conversion_plan.txt
cat formula_conversion.sql
```

Done! 🎉
