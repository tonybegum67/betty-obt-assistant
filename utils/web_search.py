"""
Web search utility for Betty AI Assistant.

This module provides web search capabilities using multiple search providers
with fallback support and result caching.
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import streamlit as st


class WebSearchTool:
    """Web search tool with multiple provider support."""

    def __init__(self):
        """Initialize the web search tool with available providers."""
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")

        # Cache for search results (simple in-memory cache)
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)

    def _get_cache_key(self, query: str, max_results: int) -> str:
        """Generate cache key for search query."""
        return f"{query}:{max_results}"

    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict]]:
        """Get cached search result if still valid."""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return result
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, result: List[Dict]):
        """Cache search result with timestamp."""
        self.cache[cache_key] = (result, datetime.now())

    def search_tavily(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search using Tavily API (optimized for AI applications).

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, url, and snippet
        """
        if not self.tavily_api_key:
            return []

        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": False
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "score": item.get("score", 0)
                })

            return results

        except Exception as e:
            print(f"Tavily search error: {e}")
            return []

    def search_serper(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search using Serper.dev API (Google Search API).

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, url, and snippet
        """
        if not self.serper_api_key:
            return []

        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": max_results
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "position": item.get("position", 0)
                })

            return results

        except Exception as e:
            print(f"Serper search error: {e}")
            return []

    def search_brave(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search using Brave Search API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, url, and snippet
        """
        if not self.brave_api_key:
            return []

        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "X-Subscription-Token": self.brave_api_key,
                "Accept": "application/json"
            }
            params = {
                "q": query,
                "count": max_results
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", "")
                })

            return results

        except Exception as e:
            print(f"Brave search error: {e}")
            return []

    def search_perplexity(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search using Perplexity AI API (sonar model with web search).

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, url, and snippet
        """
        if not self.perplexity_api_key:
            return []

        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "sonar",  # Perplexity's web search model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a web search assistant. Provide a comprehensive answer with sources."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.2,
                "return_citations": True,
                "return_images": False
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            results = []

            # Extract search results from Perplexity's response
            search_results = data.get("search_results", [])

            if search_results:
                for item in search_results[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", "")
                    })
            else:
                # Fallback: if no search_results, use the AI-generated answer
                answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if answer:
                    results.append({
                        "title": "Perplexity AI Answer",
                        "url": "https://www.perplexity.ai/",
                        "snippet": answer[:500]
                    })

            return results

        except Exception as e:
            print(f"Perplexity search error: {e}")
            return []

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform web search with automatic provider fallback.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, url, and snippet
        """
        # Check cache first
        cache_key = self._get_cache_key(query, max_results)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result

        # Try providers in order of preference
        results = []

        # 1. Try Perplexity (AI-powered with citations)
        if self.perplexity_api_key:
            results = self.search_perplexity(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        # 2. Try Tavily (optimized for AI)
        if self.tavily_api_key:
            results = self.search_tavily(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        # 3. Fallback to Serper (Google results)
        if self.serper_api_key:
            results = self.search_serper(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        # 4. Fallback to Brave
        if self.brave_api_key:
            results = self.search_brave(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        return []

    def format_results_for_context(self, results: List[Dict]) -> str:
        """
        Format search results for inclusion in LLM context.

        Args:
            results: List of search results

        Returns:
            Formatted string with search results
        """
        if not results:
            return "No search results found."

        formatted = "Web Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   {result['snippet']}\n\n"

        return formatted


# Tool definition for Claude API
WEB_SEARCH_TOOL_DEFINITION = {
    "name": "web_search",
    "description": "Search the web for current information, news, and facts not available in the knowledge base. Use this when you need up-to-date information, external references, or when the knowledge base doesn't contain relevant information. This tool should NOT be used for questions that can be answered from the internal knowledge base.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to find relevant information on the web. Be specific and include key terms."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return (default: 5, max: 10)",
                "default": 5
            }
        },
        "required": ["query"]
    }
}


# Global instance
web_search_tool = WebSearchTool()


def execute_web_search(query: str, max_results: int = 5) -> str:
    """
    Execute a web search and return formatted results.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Formatted search results as string
    """
    results = web_search_tool.search(query, max_results)
    return web_search_tool.format_results_for_context(results)
