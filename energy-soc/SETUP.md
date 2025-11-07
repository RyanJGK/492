# Energy SOC - Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Energy SOC simulation.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Supabase Configuration](#supabase-configuration)
4. [Docker Setup](#docker-setup)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Node.js**: Version 20.x or later
  ```bash
  node --version  # Should be v20.x.x or higher
  ```

- **npm**: Comes with Node.js
  ```bash
  npm --version  # Should be 10.x.x or higher
  ```

- **Git**: For version control
  ```bash
  git --version
  ```

### Optional Software

- **Docker**: For containerized deployment
  ```bash
  docker --version
  docker-compose --version
  ```

- **Supabase CLI**: For database management
  ```bash
  npm install -g supabase
  supabase --version
  ```

## Local Development Setup

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd energy-soc

# Install dependencies
npm install
```

This will install all required packages including:
- Next.js 15
- React 18
- TensorFlow.js
- Supabase client
- Recharts
- Tailwind CSS

### Step 2: Environment Configuration

```bash
# Copy the environment template
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**Note**: If you don't have Supabase set up yet, you can skip this step. The app will run in mock data mode.

### Step 3: Run Development Server

```bash
npm run dev
```

The application will start at [http://localhost:3000](http://localhost:3000)

You should see:
- ✓ Ready in 2-3 seconds
- ○ Compiling /...
- ✓ Compiled successfully

### Step 4: Verify Installation

1. Open your browser to http://localhost:3000
2. You should see the Energy SOC Dashboard
3. Try switching between Admin, Analyst, and Observer roles
4. Verify that mock alerts are appearing

## Supabase Configuration

### Option 1: Cloud Supabase (Recommended for Production)

#### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in project details:
   - **Name**: energy-soc
   - **Database Password**: Choose a strong password
   - **Region**: Select closest to you

#### Step 2: Get API Keys

1. In your Supabase dashboard, go to Settings → API
2. Copy these values:
   - **Project URL**: Your `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public**: Your `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role**: Your `SUPABASE_SERVICE_ROLE_KEY` (keep secret!)

#### Step 3: Set Up Database Schema

**Method A: Using Supabase Studio**

1. Go to SQL Editor in your Supabase dashboard
2. Click "New Query"
3. Copy and paste contents from `supabase/schema.sql`
4. Click "Run"

**Method B: Using Supabase CLI**

```bash
# Initialize Supabase in your project
supabase init

# Link to your project
supabase link --project-ref your-project-ref

# Push schema to database
supabase db push
```

#### Step 4: Deploy Edge Functions

```bash
# Deploy alert generation function
supabase functions deploy generate-alerts

# Deploy threat analysis function
supabase functions deploy analyze-threats

# Set up function secrets
supabase secrets set SUPABASE_URL=your-url
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=your-key
```

#### Step 5: Set Up Periodic Alert Generation

**Using Supabase Cron Jobs** (if available):

```sql
-- Schedule alert generation every 30 seconds
SELECT cron.schedule(
  'generate-alerts',
  '30 seconds',
  $$SELECT generate_synthetic_alert()$$
);
```

**Using External Cron**:

Set up a service like [cron-job.org](https://cron-job.org) to call your edge function:

```
URL: https://your-project.supabase.co/functions/v1/generate-alerts
Method: POST
Headers: Authorization: Bearer YOUR_ANON_KEY
Schedule: */30 * * * * (every 30 seconds)
```

### Option 2: Local Supabase with Docker

```bash
# Initialize Supabase locally
supabase init

# Start Supabase services
supabase start

# This will output:
# - API URL (use as NEXT_PUBLIC_SUPABASE_URL)
# - anon key (use as NEXT_PUBLIC_SUPABASE_ANON_KEY)
# - service_role key (use as SUPABASE_SERVICE_ROLE_KEY)

# Apply database schema
supabase db reset
```

Update your `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key-from-output>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key-from-output>
```

## Docker Setup

### Option 1: Docker Compose (Full Stack)

```bash
# Update docker-compose.yml with your settings
nano docker-compose.yml

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Access application
# http://localhost:3000 - Main application
# http://localhost:3001 - Supabase Studio
```

### Option 2: Docker Only (App Container)

```bash
# Build the image
docker build -t energy-soc:latest .

# Run the container
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_SUPABASE_URL=your-url \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY=your-key \
  --name energy-soc \
  energy-soc:latest

# View logs
docker logs -f energy-soc

# Stop container
docker stop energy-soc
```

### Option 3: Production Deployment

```bash
# Build optimized production image
docker build --target runner -t energy-soc:prod .

# Run in production mode
docker run -d \
  -p 80:3000 \
  -e NODE_ENV=production \
  -e NEXT_PUBLIC_SUPABASE_URL=your-url \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY=your-key \
  --restart unless-stopped \
  --name energy-soc-prod \
  energy-soc:prod
```

## Troubleshooting

### Issue: "Cannot find module" errors

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules
rm package-lock.json
npm install
```

### Issue: TensorFlow.js backend initialization fails

**Solution**:
```bash
# The app automatically handles this, but if you see warnings:
# 1. Check that you're using a modern browser (Chrome, Firefox, Edge)
# 2. Try disabling browser extensions
# 3. Clear browser cache
```

### Issue: Supabase connection fails

**Solution**:

1. Verify environment variables are correct:
   ```bash
   echo $NEXT_PUBLIC_SUPABASE_URL
   echo $NEXT_PUBLIC_SUPABASE_ANON_KEY
   ```

2. Check Supabase project status in dashboard

3. Test connection manually:
   ```bash
   curl https://your-project.supabase.co/rest/v1/ \
     -H "apikey: YOUR_ANON_KEY"
   ```

4. The app will fall back to mock data if Supabase is unavailable

### Issue: Realtime subscriptions not working

**Solution**:

1. Verify Realtime is enabled in Supabase:
   - Go to Database → Replication
   - Enable replication for `alerts` and `system_metrics` tables

2. Check browser console for connection errors

3. Verify network allows WebSocket connections

### Issue: Docker build fails

**Solution**:

```bash
# Clear Docker cache
docker builder prune -a

# Rebuild with no cache
docker build --no-cache -t energy-soc .

# Check Docker resources (ensure sufficient memory)
docker system df
```

### Issue: Port 3000 already in use

**Solution**:

```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or run on different port
PORT=3001 npm run dev
```

### Issue: Mock data not appearing

**Solution**:

This is normal! Mock data generation happens at these intervals:
- New alerts: Every 15 seconds
- System metrics: Every 10 seconds

Wait a few seconds after loading the page.

## Testing Your Setup

### 1. Test Dashboard Access

Visit each view and verify functionality:
- **Admin**: Can you adjust AI weights?
- **Analyst**: Can you click alerts and see AI analysis?
- **Observer**: Are charts displaying correctly?

### 2. Test Real-Time Updates

1. Open two browser windows side by side
2. In one window, use Admin or Analyst view
3. Change an alert status
4. Verify the change appears in the second window

### 3. Test AI Analysis

1. Switch to Analyst view
2. Click on any alert
3. Wait for AI analysis to complete
4. Verify you see:
   - Threat score
   - Confidence level
   - Findings
   - Recommendations

### 4. Test Docker Deployment

```bash
# Build and run
docker-compose up -d

# Check all services are healthy
docker-compose ps

# All services should show "Up"
```

## Next Steps

Once setup is complete:

1. **Explore the Dashboard**: Try all three role views
2. **Review AI Analysis**: See how the TensorFlow agent evaluates threats
3. **Customize Configuration**: Adjust AI weights in Admin view
4. **Review Code**: Explore the codebase structure
5. **Extend Functionality**: Add new features or customize existing ones

## Getting Help

If you encounter issues not covered here:

1. Check the main [README.md](./README.md)
2. Review error messages in browser console
3. Check application logs
4. Create an issue with:
   - Detailed description
   - Steps to reproduce
   - Error messages
   - Environment info (OS, Node version, etc.)

---

**Happy simulating! 🚀**
