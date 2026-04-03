# Supabase Setup Guide for Transit-X

**Time: ~15 minutes**

## Step 1: Create Supabase Account (2 min)

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub/Google or email
4. Verify email

## Step 2: Create Project (5 min)

1. Click "New Project"
2. **Project name**: `transit-delay-predictor`
3. **Database password**: Create a strong password (save it!)
4. **Region**: Choose closest to you (e.g., `ap-southeast-1` for Asia)
5. Click "Create new project"
6. Wait 2-3 minutes for project to initialize

## Step 3: Get API Credentials (1 min)

Once project loads:

1. Go to **Settings** (bottom left)
2. Click **API** in the sidebar
3. Copy these values:
   - **Project URL** (looks like `https://xxxxx.supabase.co`)
   - **anon public** (Project Key)

Save them somewhere safe!

## Step 4: Update App Configuration (3 min)

Edit `.env` file in project root:

```
SUPABASE_URL=https://YOUR_PROJECT_URL.supabase.co
SUPABASE_ANON_KEY=YOUR_ANON_KEY_HERE
```

Example:
```
SUPABASE_URL=https://abc123def456.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Step 5: Run Database Migrations (3 min)

1. In Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **New Query**
3. Copy-paste contents of `supabase/migrations/001_init_schema.sql`
4. Click **Run** (wait for ✓)
5. Repeat for `supabase/migrations/002_flood_zones_events_advanced_reports.sql`

OR use the SQL files in the repo directly in the SQL editor.

## Step 6: Verify Connection (1 min)

The app will automatically connect when:
- You restart `flutter run`
- `.env` file has correct credentials
- Migrations are completed

You should see in terminal:
```
✓ Supabase initialized
✓ Connected to database
```

## Troubleshooting

**Problem**: "Invalid API key"
- Verify you copied the **anon public** key, not the service role key
- Check `.env` file has no extra spaces

**Problem**: "Connection timeout"
- Verify your SUPABASE_URL is correct (includes full domain)
- Check internet connection
- Wait a few seconds and try again

**Problem**: "Table doesn't exist"
- Migrations didn't run properly
- Go to **SQL Editor** and verify tables exist
- Re-run migrations if needed

**Problem**: "RLS policy violation"
- Some queries blocked by Row Level Security
- Go to Tables → select table → RLS tab
- Disable RLS for testing (enable later in production)

## What's Next?

✅ Supabase connected
- App now saves data to database
- Can see data in Supabase dashboard under Tables
- Reports and predictions persist

📊 View your data:
1. Supabase dashboard
2. Click **Table Editor** (left sidebar)
3. Browse: `stops`, `events`, `delay_predictions`, `user_reports`

🚀 Advanced (optional later):
- Set up real-time subscriptions
- Enable auth (user accounts)
- Configure backups
- Monitor database performance

---

**Done!** Your database is ready. Restart the flutter app and it will connect. 🎉
