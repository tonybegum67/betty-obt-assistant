# Web Search Setup Guide

Betty now supports web search capabilities to find current information beyond her knowledge base!

## Overview

The web search tool allows Betty to:
- Find up-to-date information not available in the knowledge base
- Search for current news, facts, and external references
- Provide real-time data when needed

**Important**: Betty will intelligently decide when to use web search vs. her internal knowledge base.

## Supported Search Providers

Betty supports four search APIs with automatic fallback:

### 1. **Perplexity AI** (⭐ RECOMMENDED)
- **Best for**: AI-powered search with citations, comprehensive answers
- **Cost**: Free tier available with generous limits
- **Sign up**: https://www.perplexity.ai/settings/api
- **Model**: Uses Perplexity's Sonar model with web search
- **Unique**: Returns AI-synthesized answers with source citations

### 2. **Tavily AI**
- **Best for**: AI applications, clean results
- **Cost**: Free tier available (1,000 requests/month)
- **Sign up**: https://tavily.com/
- **Pricing**: https://tavily.com/pricing

### 3. **Serper.dev** (Google Search)
- **Best for**: Google search results
- **Cost**: Free tier (2,500 queries)
- **Sign up**: https://serper.dev/
- **Pricing**: https://serper.dev/pricing

### 4. **Brave Search**
- **Best for**: Privacy-focused search
- **Cost**: Free tier available
- **Sign up**: https://brave.com/search/api/
- **Pricing**: https://brave.com/search/api/

## Setup Instructions

### Step 1: Get API Keys

Choose one or more providers and sign up for API keys:

1. **Perplexity AI** (⭐ Recommended):
   - Go to https://www.perplexity.ai/settings/api
   - Sign in to your Perplexity account
   - Generate an API key from the API settings
   - Note: Uses the Sonar model with built-in web search

2. **Tavily** (AI-optimized):
   - Go to https://tavily.com/
   - Sign up for a free account
   - Get your API key from the dashboard

3. **Serper.dev** (Google results):
   - Go to https://serper.dev/
   - Sign up with Google
   - Copy your API key

4. **Brave Search**:
   - Visit https://brave.com/search/api/
   - Request API access
   - Get your subscription token

### Step 2: Add API Keys to Environment

Add your API key(s) to your `.env` file:

```env
# Web Search API Keys (choose one or more)
PERPLEXITY_API_KEY=your_perplexity_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SERPER_API_KEY=your_serper_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
```

**Note**: You only need ONE provider, but having multiple enables fallback if one fails.

### Step 3: Enable Web Search in Betty

1. Open Betty's chat interface
2. In the sidebar, check the box: **🔍 Enable Web Search**
3. Start chatting! Betty will now use web search when appropriate

## How It Works

### Intelligent Search Decision

Betty automatically decides when to use web search:
- ✅ **Uses web search for**: Current events, recent news, external facts, real-time data
- ❌ **Uses knowledge base for**: Company policies, internal docs, procedures

### Search Flow

1. User asks a question
2. Betty checks if the knowledge base has the answer
3. If web search is enabled and needed, Betty searches the web
4. Results are integrated into her response
5. Sources are cited in the response

### Example Queries That Trigger Web Search

- "What's the latest news about AI?"
- "What's the current weather in San Francisco?"
- "Who won the latest Super Bowl?"
- "What are the current Python best practices?"

### Example Queries Using Knowledge Base

- "What's our PTO policy?"
- "How do I submit an expense report?"
- "What are our company values?"

## Provider Comparison

| Provider | Free Tier | Best For | Response Time | Quality |
|----------|-----------|----------|---------------|---------|
| **Perplexity** | Generous | AI synthesis | Fast (~1-2s) | Excellent ⭐ |
| **Tavily** | 1K/month | AI apps | Fast (~500ms) | Excellent |
| **Serper** | 2.5K total | Google results | Fast (~300ms) | Excellent |
| **Brave** | Limited | Privacy | Medium (~800ms) | Good |

**Why Perplexity is Recommended:**
- Returns AI-synthesized answers with proper citations
- Leverages Perplexity's Sonar model trained for web search
- Provides more comprehensive and contextual results
- Built-in fact-checking and source verification

## Troubleshooting

### Web search not working?

1. **Check API keys**: Ensure at least one API key is set in `.env`
2. **Enable the feature**: Check the "Enable Web Search" box in sidebar
3. **Test the provider**: Try a simple query like "What's the weather today?"
4. **Check logs**: Look for error messages in the console

### Getting rate limit errors?

- **Tavily**: Free tier is 1,000 requests/month
- **Serper**: Free tier is 2,500 total requests
- **Brave**: Contact them for rate limits

**Solution**: Add a second provider as fallback, or upgrade to paid tier

### Results seem slow?

- First search per query is slower (no cache)
- Subsequent identical searches are cached for 1 hour
- Tavily is typically the fastest provider

## Cost Optimization Tips

1. **Use free tiers wisely**: Start with Tavily (1K/month) or Serper (2.5K total)
2. **Enable only when needed**: Toggle web search on/off via sidebar
3. **Leverage caching**: Identical queries are cached for 1 hour
4. **Use multiple providers**: Set up fallback to maximize free tiers

## Privacy & Security

- API keys are stored locally in `.env` (never committed to git)
- Search queries are sent to third-party APIs
- Results are cached temporarily in memory
- No search history is permanently stored

## Advanced Configuration

### Custom Cache Duration

Edit `utils/web_search.py`:

```python
self.cache_ttl = timedelta(hours=1)  # Change to desired duration
```

### Custom Result Count

In the sidebar or via tool definition:

```python
max_results = 5  # Default, can be 1-10
```

## Support

- **Issues**: Report bugs in the GitHub repository
- **Provider Issues**: Contact the search provider directly
- **Feature Requests**: Open an issue with the label "enhancement"

## Credits

- Built with Anthropic Claude tool use
- Supports Tavily, Serper, and Brave Search APIs
- Caching and fallback mechanisms for reliability
