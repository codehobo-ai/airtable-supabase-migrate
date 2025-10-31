# Simple Netlify Setup Guide

**Goal:** Add dashboard to your existing Netlify site in 5 minutes.

## Quick Overview

```
Your Netlify Site
├── index.html          # Your form (existing)
├── dashboard/          # Dashboard (new)
│   ├── index.html      # Dashboard page
│   └── data.json       # Dashboard data
└── netlify.toml        # Config (new)
```

**URLs:**
- Form: `https://yourdomain.com/`
- Dashboard: `https://yourdomain.com/dashboard`

---

## Setup Steps

### Step 1: Copy Dashboard Files to Your Netlify Repo

I've created template files in `netlify-dashboard-template/`. Copy them to your Netlify repo:

```bash
# Navigate to YOUR Netlify repo
cd /path/to/your-netlify-site

# Copy dashboard folder from n8n-claude repo
cp -r /home/megaboss/Projects-Cursor/n8n-claude/netlify-dashboard-template/index.html ./dashboard/
cp -r /home/megaboss/Projects-Cursor/n8n-claude/netlify-dashboard-template/data.json ./dashboard/

# Copy netlify.toml (if you don't have one)
cp /home/megaboss/Projects-Cursor/n8n-claude/netlify-dashboard-template/netlify.toml ./

# OR if you already have netlify.toml, just add the redirects manually
```

### Step 2: Commit and Push

```bash
git add dashboard/ netlify.toml
git commit -m "Add monitoring dashboard"
git push origin main
```

**Netlify will auto-deploy!** ✅

### Step 3: View Your Dashboard

Visit: `https://yourdomain.com/dashboard`

You'll see:
- Empty dashboard with placeholder data
- Message: "Run GitHub Actions workflows to populate this data"

---

## Step 4: Connect GitHub Actions (Auto-update)

Now configure GitHub Actions to update the dashboard automatically.

### Add GitHub Secrets

In your **n8n-claude repo** (not Netlify repo), add these secrets:

```bash
# Method 1: Using GitHub CLI
gh secret set NETLIFY_REPO --body "YOUR-USERNAME/YOUR-NETLIFY-REPO-NAME"
gh secret set NETLIFY_DEPLOY_TOKEN --body "PASTE-GITHUB-TOKEN-HERE"
gh secret set NETLIFY_BUILD_HOOK --body "https://api.netlify.com/build_hooks/PASTE-HERE"

# Method 2: Via Web UI
# Go to: github.com/your-username/n8n-claude/settings/secrets/actions
# Click "New repository secret"
```

**What you need:**

1. **NETLIFY_REPO**: Your Netlify repo name
   - Example: `megaboss/my-netlify-site`

2. **NETLIFY_DEPLOY_TOKEN**: GitHub personal access token
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Scopes: Check `repo` (full control of repositories)
   - Copy the token (starts with `ghp_`)

3. **NETLIFY_BUILD_HOOK**: Netlify build hook URL
   - Netlify Dashboard → Your site → Site settings
   - Build & deploy → Build hooks
   - Click "Add build hook"
   - Name: "GitHub Actions Update"
   - Copy the URL (looks like `https://api.netlify.com/build_hooks/xxxxx`)

### Step 5: Test the Workflow

```bash
# In n8n-claude repo
gh workflow run deploy-to-netlify.yml
```

Or via GitHub web UI:
1. Go to Actions tab in n8n-claude repo
2. Click "Deploy Dashboard to Netlify"
3. Click "Run workflow"

**This will:**
1. Fetch latest audit data
2. Generate dashboard data.json
3. Push to your Netlify repo
4. Trigger Netlify rebuild
5. Dashboard updates! 🎉

---

## Your Workflow

### Daily Auto-update

The workflow runs automatically when:
- ✅ Audit workflow completes
- ✅ Sync workflow completes
- ✅ Daily at 10 AM (scheduled)

### Manual Update

Anytime you want to refresh:

```bash
gh workflow run deploy-to-netlify.yml
```

---

## File Structure (Final)

### Your Netlify Repo

```
your-netlify-site/
├── index.html              # Your form ✅
├── styles.css              # Your styles ✅
├── dashboard/              # Dashboard folder ✅
│   ├── index.html          # Dashboard UI
│   └── data.json           # Data (updated by GitHub Actions)
└── netlify.toml            # Config ✅
```

### Your n8n-claude Repo

```
n8n-claude/
├── .github/workflows/
│   ├── airtable-audit.yml          # Runs audits
│   ├── airtable-sync.yml           # Runs syncs
│   └── deploy-to-netlify.yml       # Updates dashboard
├── scripts/
│   ├── audit_formulas.py
│   └── export_dashboard_data.py
└── netlify-dashboard-template/     # Template files
    ├── index.html
    ├── data.json
    └── netlify.toml
```

---

## Testing

### Test 1: View Empty Dashboard

After Step 2 above:
```bash
open https://yourdomain.com/dashboard
```

Should show:
- ✅ Dashboard loads
- ✅ Shows "0" for all stats
- ✅ Message about running workflows

### Test 2: Run Audit

```bash
# In n8n-claude repo
gh workflow run airtable-audit.yml -f action=audit_formulas
```

Wait 2-3 minutes, then:

```bash
gh workflow run deploy-to-netlify.yml
```

Wait 1-2 minutes, then refresh dashboard:
```bash
open https://yourdomain.com/dashboard
```

Should show:
- ✅ Real table count
- ✅ Real formula count
- ✅ List of detected formulas

---

## Troubleshooting

### "Dashboard page not found (404)"

**Check:**
1. Did you push `dashboard/` folder to Netlify repo?
2. Is `netlify.toml` in root of repo?
3. Did Netlify deploy successfully?

**Fix:**
```bash
cd your-netlify-site
ls dashboard/  # Should show index.html and data.json
cat netlify.toml  # Should show redirects
git status  # Make sure files are committed
```

### "Dashboard shows 0 for everything"

**This is normal!** It means:
- ✅ Dashboard is working
- ❌ No data yet (run audit workflow first)

**Fix:**
```bash
# Run audit in n8n-claude repo
gh workflow run airtable-audit.yml

# Then update dashboard
gh workflow run deploy-to-netlify.yml
```

### "GitHub Actions can't push to Netlify repo"

**Check:**
1. Is `NETLIFY_DEPLOY_TOKEN` set correctly?
2. Does token have `repo` scope?
3. Is `NETLIFY_REPO` the correct repo name?

**Fix:**
```bash
# Verify secrets
gh secret list

# Re-create token with repo access
# https://github.com/settings/tokens
```

### "Netlify not rebuilding"

**Check build hook:**
```bash
# Test build hook manually
curl -X POST -d '{}' https://api.netlify.com/build_hooks/YOUR-HOOK-ID
```

Should trigger a deploy in Netlify dashboard.

---

## Adding Navigation

Update your form's `index.html` to link to dashboard:

```html
<!-- Add to your form -->
<nav style="padding: 20px; background: #667eea;">
  <a href="/" style="color: white; margin-right: 20px;">Form</a>
  <a href="/dashboard" style="color: white;">Dashboard</a>
</nav>
```

---

## Customization

### Change Dashboard Colors

Edit `dashboard/index.html` (line ~11):

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Try these:
```css
/* Pink gradient */
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Blue gradient */
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

/* Green gradient */
background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
```

### Change Refresh Rate

Edit `dashboard/index.html` (line ~201):

```javascript
// Auto-refresh every 5 minutes
setInterval(loadDashboard, 5 * 60 * 1000);

// Change to 30 minutes:
setInterval(loadDashboard, 30 * 60 * 1000);
```

---

## Complete Command Checklist

### One-time Setup

```bash
# 1. Copy dashboard files to YOUR Netlify repo
cd /path/to/your-netlify-site
mkdir -p dashboard
cp /path/to/n8n-claude/netlify-dashboard-template/index.html dashboard/
cp /path/to/n8n-claude/netlify-dashboard-template/data.json dashboard/
cp /path/to/n8n-claude/netlify-dashboard-template/netlify.toml ./

# 2. Commit and push
git add dashboard/ netlify.toml
git commit -m "Add monitoring dashboard"
git push origin main

# 3. Add GitHub secrets (in n8n-claude repo)
cd /path/to/n8n-claude
gh secret set NETLIFY_REPO --body "your-username/your-netlify-repo"
gh secret set NETLIFY_DEPLOY_TOKEN --body "ghp_xxxxx"
gh secret set NETLIFY_BUILD_HOOK --body "https://api.netlify.com/build_hooks/xxxxx"

# 4. Test
open https://yourdomain.com/dashboard
```

### Regular Usage

```bash
# Run audit (in n8n-claude repo)
gh workflow run airtable-audit.yml -f action=audit_formulas

# Update dashboard (in n8n-claude repo)
gh workflow run deploy-to-netlify.yml

# View dashboard
open https://yourdomain.com/dashboard
```

---

## What Happens Automatically

Once setup is complete:

1. **Daily at 10 AM:** GitHub Actions updates dashboard
2. **After every audit:** Dashboard auto-updates
3. **After every sync:** Dashboard auto-updates

**You do nothing!** The dashboard stays current automatically. ✅

---

## Summary

✅ **Step 1:** Copy 3 files to Netlify repo
✅ **Step 2:** Push to GitHub (Netlify auto-deploys)
✅ **Step 3:** Add 3 secrets to GitHub
✅ **Step 4:** Run workflow once to populate data
✅ **Done!** Dashboard updates automatically forever

**Time:** 5-10 minutes total

---

## Need Help?

**Where's my Netlify repo?**
- Check: https://app.netlify.com/sites/YOUR-SITE/settings/general
- Look for "Repository" under "Build settings"

**Can't find build hook?**
- Netlify Dashboard → Site settings → Build & deploy → Build hooks
- If none exists, click "Add build hook"

**Token permissions?**
- Must have `repo` scope (full control of private repositories)
- Generate at: https://github.com/settings/tokens

---

**Ready? Start with Step 1!** 🚀
