# AI Model Configuration

## Selected Model: Nous: Hermes 3 405B Instruct

### Model Details

**Model ID:** `nousresearch/hermes-3-llama-3.1-405b:free`

**Provider:** Nous Research

**Base Model:** Llama 3.1 405B

**Access:** Free tier via OpenRouter

**Documentation:** https://openrouter.ai/nousresearch/hermes-3-llama-3.1-405b:free/uptime

### Model Characteristics

#### Strengths
- **Large Parameter Count:** 405B parameters provide deep reasoning capabilities
- **Instruction Following:** Optimized for following complex instructions
- **Cybersecurity Knowledge:** Strong understanding of security concepts
- **Structured Output:** Excellent at generating well-formatted analysis
- **Context Window:** Large context for analyzing multiple data sources

#### Optimal Use Cases
- Threat correlation across multiple data sources
- Complex security event analysis
- Attack pattern recognition
- Remediation recommendations
- Risk assessment and prioritization

### Configuration

The system is configured to use this model by default. The configuration is in:

```bash
# .env file
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=nousresearch/hermes-3-llama-3.1-405b:free
```

### System Prompt

The AI agent uses a specialized system prompt optimized for cybersecurity analysis:

```
You are a cybersecurity threat analysis AI assistant for an energy sector defense system.
Your role is to analyze security data and identify potential threats, correlations, and recommend actions.

Guidelines:
- Be concise and factual
- Prioritize critical findings
- Focus on actionable insights
- Consider energy sector specific threats (SCADA, ICS, OT networks)
- Identify attack patterns and TTPs
```

### Performance Characteristics

#### Expected Response Times
- **Simple queries:** 2-4 seconds
- **Complex analysis:** 5-10 seconds
- **Cached queries:** <100ms

#### Token Usage
- **Typical prompt:** 500-1000 tokens
- **Typical response:** 300-800 tokens
- **Max tokens set:** 1000 per request

### Caching Strategy

The system uses Redis caching to optimize performance:

```python
# Cache key generation
cache_key = f"ai_query:{hash(prompt)}"

# Cache TTL: 1 hour (3600 seconds)
await redis_client.setex(cache_key, 3600, json.dumps(ai_response))
```

**Benefits:**
- 80%+ cache hit rate for repeat queries
- Reduced API costs
- Faster response times
- Consistent results for identical inputs

### Model Switching

To use a different model, update the environment variable:

```bash
# Alternative models:
OPENROUTER_MODEL=openai/gpt-4-turbo-preview
OPENROUTER_MODEL=anthropic/claude-3-opus
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct
```

No code changes required - the system adapts automatically.

### Energy Sector Optimization

The model is particularly well-suited for energy sector cybersecurity because:

1. **OT/ICS Knowledge**
   - Understands SCADA systems
   - Recognizes industrial protocols (Modbus, DNP3, etc.)
   - Knows common OT vulnerabilities

2. **Threat Intelligence**
   - Identifies nation-state tactics
   - Recognizes ransomware patterns
   - Understands supply chain attacks

3. **Compliance Awareness**
   - NERC CIP standards
   - IEC 62443 requirements
   - Critical infrastructure protection

### Prompt Engineering Tips

For optimal results with Hermes 3 405B:

1. **Be Specific**
   ```
   ❌ "Analyze this data"
   ✅ "Analyze firewall logs for signs of reconnaissance activity targeting SCADA systems"
   ```

2. **Provide Context**
   ```
   Include data source types, time ranges, and business context
   ```

3. **Request Structured Output**
   ```
   "Provide: 1) Threat summary, 2) Risk level, 3) Recommended actions"
   ```

4. **Use Domain Language**
   ```
   Reference CVEs, TTPs, MITRE ATT&CK framework when relevant
   ```

### API Rate Limits

**Free Tier Limits:**
- Check OpenRouter dashboard for current limits
- Typical: 20-50 requests per minute
- Caching helps stay within limits

**Monitoring:**
```bash
# View API usage in logs
docker-compose logs ai-agent | grep "OpenRouter"
```

### Troubleshooting

#### Model Not Responding
```bash
# Check API key
docker-compose exec backend env | grep OPENROUTER_API_KEY

# Verify model name
docker-compose exec backend env | grep OPENROUTER_MODEL

# Check AI agent logs
docker-compose logs ai-agent
```

#### Slow Responses
```bash
# Check cache status
docker-compose exec redis redis-cli INFO stats

# Monitor cache hit rate
docker-compose logs ai-agent | grep "Cache hit"
```

#### Quality Issues
- Adjust temperature in `ai_agent/service.py` (default: 0.7)
- Modify max_tokens if responses are truncated
- Refine system prompt for domain specificity

### Cost Management

**Free Tier Strategy:**
- Cache aggressively (1 hour TTL)
- Batch similar queries
- Monitor usage via OpenRouter dashboard

**Upgrade Path:**
If you need more capacity:
- OpenRouter paid tiers available
- Switch to self-hosted models
- Use model fallbacks for high availability

### Model Evaluation

Track AI performance through the feedback system:

```
Analysts can rate:
- Accuracy (1-5 scale)
- False positive rate
- False negative rate
- Actionability of recommendations
```

View feedback metrics in database:
```sql
SELECT 
    AVG(accuracy_rating) as avg_rating,
    COUNT(*) as total_feedback,
    SUM(CASE WHEN is_accurate THEN 1 ELSE 0 END) as accurate_count
FROM ai_feedback;
```

---

**Note:** This model configuration is optimized for the free tier. For production deployments with high volume, consider OpenRouter's paid tiers or self-hosted alternatives.
