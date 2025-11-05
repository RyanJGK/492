# Setting Up Your OpenRouter API Key

## Quick Setup for Nous: Hermes 3 405B Instruct

Your system is pre-configured to use **Nous: Hermes 3 405B Instruct** - an excellent free model for cybersecurity analysis.

### Step 1: Add Your API Key

The `.env` file has been created for you. Just add your API key:

```bash
cd /workspace/492-energy-defense
nano .env
```

Replace this line:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

With your actual key:
```bash
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
```

Save and exit (Ctrl+X, Y, Enter)

### Step 2: Verify Configuration

Check that everything is set correctly:

```bash
cat .env | grep OPENROUTER
```

You should see:
```bash
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
OPENROUTER_MODEL=nousresearch/hermes-3-llama-3.1-405b:free
```

### Step 3: Start the System

```bash
docker-compose up --build
```

Wait 30-60 seconds for initialization, then access:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/api/docs

### Model Details

**Model:** Nous: Hermes 3 405B Instruct  
**Provider:** Nous Research  
**Access:** Free tier via OpenRouter  
**Documentation:** https://openrouter.ai/nousresearch/hermes-3-llama-3.1-405b:free/uptime

**Why This Model is Great for Energy Defense:**
- ✅ 405B parameters - powerful reasoning
- ✅ Excellent cybersecurity knowledge
- ✅ Strong instruction following
- ✅ Understands SCADA/ICS/OT systems
- ✅ Free tier available
- ✅ Good for threat correlation

### Testing the AI Agent

Once the system is running:

1. **Login** as admin (admin/admin123)
2. **Navigate** to Dashboard
3. **Wait** for data simulator to generate events (5 minutes)
4. **Trigger Analysis** (future feature) or check AI analysis logs:

```bash
docker-compose logs ai-agent
```

### Expected AI Response Time

- **First query:** 3-8 seconds (no cache)
- **Repeat queries:** <100ms (cached)
- **Complex analysis:** 5-10 seconds

### Monitoring AI Usage

```bash
# View AI agent activity
docker-compose logs -f ai-agent

# Check cache performance
docker-compose exec redis redis-cli INFO stats

# View API calls
docker-compose logs backend | grep OpenRouter
```

### Troubleshooting

#### "Missing required environment variables"
```bash
# Verify API key is set
docker-compose exec backend env | grep OPENROUTER_API_KEY

# Should show your key, not "your_openrouter_api_key_here"
```

#### "API authentication failed"
```bash
# Check your API key at OpenRouter dashboard
# Ensure it starts with: sk-or-v1-

# Restart services after updating .env
docker-compose down
docker-compose up
```

#### "Model not found"
```bash
# Verify model name is correct
docker-compose exec backend env | grep OPENROUTER_MODEL

# Should show: nousresearch/hermes-3-llama-3.1-405b:free
```

### Rate Limits (Free Tier)

The free tier has limits. To check your usage:
1. Visit https://openrouter.ai/
2. Login and check your dashboard
3. Monitor remaining credits/requests

**Tips to stay within limits:**
- System uses aggressive caching (1 hour)
- Repeat queries hit cache, not API
- Data simulator doesn't trigger AI automatically

### Upgrading

If you need more capacity:

**Option 1: OpenRouter Paid Tier**
- More requests per minute
- Higher token limits
- Same integration (just add credits)

**Option 2: Different Model**
Edit `.env`:
```bash
OPENROUTER_MODEL=openai/gpt-4-turbo-preview  # More expensive
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct  # Good balance
```

**Option 3: Self-Hosted**
- Deploy your own LLM
- Update AI agent to point to local endpoint
- No rate limits, but requires GPU

### Security Notes

⚠️ **Important:**
- Never commit `.env` file to git (already in .gitignore)
- Don't share your API key
- Rotate keys periodically
- Monitor usage for unexpected spikes

### Next Steps

1. ✅ Add your API key to `.env`
2. ✅ Start the system with `docker-compose up --build`
3. ✅ Login at http://localhost:3000
4. ✅ Explore the dashboard
5. ✅ Try different user roles
6. ✅ Monitor AI agent logs

For more details, see:
- `MODEL_INFO.md` - Detailed model configuration
- `README.md` - Full system documentation
- `QUICKSTART.md` - Quick start guide

---

**You're ready to go! The system is optimized for your Nous: Hermes 3 405B model.**
