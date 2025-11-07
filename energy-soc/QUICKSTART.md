# Energy SOC - Quick Start

Get up and running in 3 minutes! 🚀

## 30-Second Start (Mock Mode)

```bash
cd /workspace/energy-soc
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

**That's it!** The system runs with synthetic data. No database required.

## 3-Minute Start (With Supabase)

```bash
# 1. Install
cd /workspace/energy-soc
npm install

# 2. Configure
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials

# 3. Setup Database
# Go to Supabase SQL Editor
# Run the contents of: supabase/schema.sql

# 4. Start
npm run dev
```

## What You Get

### Three Views (No Login Required)

1. **Admin** 👨‍💼
   - Configure AI model weights
   - Adjust threat thresholds
   - View all system activity

2. **Analyst** 👨‍💻
   - Investigate security alerts
   - Run AI threat analysis
   - Update alert status

3. **Observer** 👀
   - Monitor trends and metrics
   - View charts and statistics
   - Read-only dashboard

### Key Features

- ✅ **Live Updates**: Alerts appear automatically every 15s
- ✅ **AI Analysis**: Click any alert for instant AI threat scoring
- ✅ **Real-Time Charts**: System metrics update every 10s
- ✅ **Beautiful UI**: Dark theme, color-coded severity
- ✅ **No Setup Required**: Works immediately with mock data

## Try These Actions

### As Admin
1. Click "Admin" role button
2. Scroll to "AI Model Configuration"
3. Adjust any weight slider
4. Click "Apply Configuration"

### As Analyst
1. Click "Analyst" role button
2. Click any alert in the queue
3. Wait for AI analysis (~1 second)
4. Click "Start Investigation"

### As Observer
1. Click "Observer" role button
2. Scroll through the charts
3. Watch the Activity Feed update
4. Check the statistics cards

## What's Running?

- **Frontend**: Next.js server on port 3000
- **AI**: TensorFlow.js in your browser
- **Data**: Mock generator OR Supabase (if configured)

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+K` or `Cmd+K` | Search alerts (Analyst view) |
| `1` | Switch to Admin |
| `2` | Switch to Analyst |
| `3` | Switch to Observer |

*Shortcuts to be implemented*

## Common First-Time Questions

**Q: Where's the login?**
A: No login! Switch roles with the buttons in the header.

**Q: Why aren't alerts showing up?**
A: Wait 15 seconds. New alerts generate automatically.

**Q: How do I see AI analysis?**
A: Go to Analyst view, click any alert, wait 1 second.

**Q: Can I use this without Supabase?**
A: Yes! It runs in mock mode by default.

**Q: How do I deploy this?**
A: Run `npm run build` then `npm start` or use Docker.

## File Structure (Simplified)

```
energy-soc/
├── app/page.tsx              # Main dashboard
├── components/views/         # Admin/Analyst/Observer
├── lib/ai-agent.ts          # TensorFlow AI
├── lib/supabase.ts          # Database client
├── supabase/schema.sql      # Database setup
└── README.md                # Full documentation
```

## Next Steps

1. ✅ Explore all three role views
2. ✅ Test AI analysis on alerts
3. ✅ Try configuring AI weights (Admin)
4. ✅ Check out the charts (Observer)
5. 📖 Read [README.md](README.md) for full details
6. 🔧 Read [SETUP.md](SETUP.md) for Supabase setup
7. 🏗️ Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the code

## Troubleshooting

**Port 3000 in use?**
```bash
PORT=3001 npm run dev
```

**Build errors?**
```bash
rm -rf node_modules .next
npm install
npm run dev
```

**AI analysis not working?**
- Make sure you're using a modern browser (Chrome/Firefox/Edge)
- Check browser console for errors
- Try refreshing the page

## Commands Cheat Sheet

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm start            # Run production build
npm run lint         # Check code quality
npm run setup        # Automated setup script
npm run verify       # Verify installation
npm run docker:build # Build Docker image
npm run docker:run   # Run in Docker
```

## Resources

- **Full Docs**: [README.md](README.md)
- **Setup Guide**: [SETUP.md](SETUP.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**🎯 You're ready to go! Open http://localhost:3000 and start exploring!**
