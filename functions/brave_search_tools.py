#!/usr/bin/env python3
"""
Brave Search Tool for Langchain Agent
Provides access to Brave Search API for web search, news, images, videos, and AI summaries
"""

import os
import json
import requests
from logging_utils import get_logger

logger = get_logger()
from datetime import datetime
from typing import Dict, List, Any, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    """Input schema for web search tool"""
    query: str = Field(description="Search query (e.g., 'climate change effects', 'Python programming')")
    count: int = Field(default=10, description="Number of results to return (1-20)")
    country: str = Field(default="US", description="Country code for search results (US, UK, CA, etc.)")
    search_lang: str = Field(default="en", description="Search language (en, es, fr, de, etc.)")
    safesearch: str = Field(default="moderate", description="Safe search level: off, moderate, strict")


class NewsSearchInput(BaseModel):
    """Input schema for news search tool"""
    query: str = Field(description="News search query (e.g., 'Tesla earnings', 'climate summit')")
    count: int = Field(default=10, description="Number of news articles to return (1-20)")
    country: str = Field(default="US", description="Country code for news results")
    search_lang: str = Field(default="en", description="Search language")
    freshness: str = Field(default="", description="Freshness filter: pd (past day), pw (past week), pm (past month), py (past year)")


class ImageSearchInput(BaseModel):
    """Input schema for image search tool"""
    query: str = Field(description="Image search query (e.g., 'golden retriever', 'sunset mountain')")
    count: int = Field(default=10, description="Number of images to return (1-20)")
    safesearch: str = Field(default="strict", description="Safe search level: off, moderate, strict")


class VideoSearchInput(BaseModel):
    """Input schema for video search tool"""
    query: str = Field(description="Video search query (e.g., 'how to cook pasta', 'Bitcoin explained')")
    count: int = Field(default=10, description="Number of videos to return (1-20)")
    country: str = Field(default="US", description="Country code for video results")
    search_lang: str = Field(default="en", description="Search language")


class SummarizerInput(BaseModel):
    """Input schema for AI summarizer tool"""
    query: str = Field(description="Query to search and summarize (e.g., 'latest AI developments', 'renewable energy trends')")
    count: int = Field(default=10, description="Number of sources to use for summary (1-20)")
    country: str = Field(default="US", description="Country code for search results")
    search_lang: str = Field(default="en", description="Search language")


class BraveWebSearchTool(BaseTool):
    """Tool for web search using Brave Search API"""
    
    name: str = "brave_web_search"
    description: str = """Search the web using Brave Search API for current information and real-time data.
    
    Parameters:
    - query: Search query (e.g., 'latest stock market news', 'Python programming tutorials')
    - count: Number of results to return (default: 10, max: 20)
    - country: Country code (default: US)
    - search_lang: Language code (default: en)
    - safesearch: Safe search level (off, moderate, strict)
    
    Returns web search results with titles, URLs, descriptions, and metadata.
    Perfect for getting current information, news, and real-time data."""
    
    args_schema: Type[BaseModel] = WebSearchInput
    
    def _run(self, query: str, count: int = 10, country: str = "US", search_lang: str = "en", safesearch: str = "moderate") -> str:
        try:
            api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not api_key:
                return "Error: BRAVE_SEARCH_API_KEY environment variable not set"
            
            # Validate count
            count = max(1, min(count, 20))
            
            url = "https://api.search.brave.com/res/v1/web/search"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "country": country,
                "search_lang": search_lang,
                "safesearch": safesearch,
                "spellcheck": 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract search results
            results = []
            web_results = data.get("web", {}).get("results", [])
            
            for result in web_results:
                results.append({
                    "title": result.get("title", "N/A"),
                    "url": result.get("url", "N/A"),
                    "description": result.get("description", "N/A"),
                    "age": result.get("age", "N/A"),
                    "type": result.get("type", "web_result"),
                    "source": result.get("profile", {}).get("name", "N/A")
                })
            
            # Format the response
            formatted_results = {
                "search_type": "web_search",
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_metadata": {
                    "country": country,
                    "language": search_lang,
                    "safesearch": safesearch,
                    "spellcheck": data.get("query", {}).get("spellcheck_off", False)
                },
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(formatted_results, indent=2)
            
        except requests.RequestException as e:
            return f"Error performing web search: {str(e)}"
        except Exception as e:
            return f"Error processing web search results: {str(e)}"


class BraveNewsSearchTool(BaseTool):
    """Tool for news search using Brave Search API"""
    
    name: str = "brave_news_search"
    description: str = """Search for recent news articles using Brave Search API.
    
    Parameters:
    - query: News search query (e.g., 'Apple earnings report', 'climate change policy')
    - count: Number of news articles to return (default: 10, max: 20)
    - country: Country code (default: US)
    - search_lang: Language code (default: en)
    - freshness: Time filter (pd=past day, pw=past week, pm=past month, py=past year)
    
    Returns recent news articles with titles, URLs, descriptions, publication dates, and sources.
    Perfect for getting current news and recent developments."""
    
    args_schema: Type[BaseModel] = NewsSearchInput
    
    def _run(self, query: str, count: int = 10, country: str = "US", search_lang: str = "en", freshness: str = "") -> str:
        try:
            api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not api_key:
                return "Error: BRAVE_SEARCH_API_KEY environment variable not set"
            
            # Validate count
            count = max(1, min(count, 20))
            
            url = "https://api.search.brave.com/res/v1/news/search"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "country": country,
                "search_lang": search_lang,
                "spellcheck": 1
            }
            
            if freshness:
                params["freshness"] = freshness
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract news results
            results = []
            news_results = data.get("results", [])
            
            for result in news_results:
                results.append({
                    "title": result.get("title", "N/A"),
                    "url": result.get("url", "N/A"),
                    "description": result.get("description", "N/A"),
                    "age": result.get("age", "N/A"),
                    "page_age": result.get("page_age", "N/A"),
                    "source": result.get("meta_url", {}).get("hostname", "N/A"),
                    "thumbnail": result.get("thumbnail", {}).get("src", "N/A") if result.get("thumbnail") else "N/A"
                })
            
            # Format the response
            formatted_results = {
                "search_type": "news_search",
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_metadata": {
                    "country": country,
                    "language": search_lang,
                    "freshness": freshness or "all_time"
                },
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(formatted_results, indent=2)
            
        except requests.RequestException as e:
            return f"Error performing news search: {str(e)}"
        except Exception as e:
            return f"Error processing news search results: {str(e)}"


class BraveImageSearchTool(BaseTool):
    """Tool for image search using Brave Search API"""
    
    name: str = "brave_image_search"
    description: str = """Search for images using Brave Search API.
    
    Parameters:
    - query: Image search query (e.g., 'golden retriever puppy', 'modern architecture')
    - count: Number of images to return (default: 10, max: 20)
    - safesearch: Safe search level (off, moderate, strict)
    
    Returns image search results with URLs, titles, sources, and metadata.
    Perfect for finding images related to any topic."""
    
    args_schema: Type[BaseModel] = ImageSearchInput
    
    def _run(self, query: str, count: int = 10, safesearch: str = "strict") -> str:
        try:
            api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not api_key:
                return "Error: BRAVE_SEARCH_API_KEY environment variable not set"
            
            # Validate count
            count = max(1, min(count, 20))
            
            url = "https://api.search.brave.com/res/v1/images/search"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "safesearch": safesearch,
                "spellcheck": 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract image results
            results = []
            image_results = data.get("results", [])
            
            for result in image_results:
                results.append({
                    "title": result.get("title", "N/A"),
                    "url": result.get("url", "N/A"),
                    "source": result.get("source", "N/A"),
                    "thumbnail": result.get("thumbnail", {}).get("src", "N/A") if result.get("thumbnail") else "N/A",
                    "image_url": result.get("properties", {}).get("url", "N/A") if result.get("properties") else "N/A",
                    "page_fetched": result.get("page_fetched", "N/A")
                })
            
            # Format the response
            formatted_results = {
                "search_type": "image_search",
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_metadata": {
                    "safesearch": safesearch
                },
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(formatted_results, indent=2)
            
        except requests.RequestException as e:
            return f"Error performing image search: {str(e)}"
        except Exception as e:
            return f"Error processing image search results: {str(e)}"


class BraveVideoSearchTool(BaseTool):
    """Tool for video search using Brave Search API"""
    
    name: str = "brave_video_search"
    description: str = """Search for videos using Brave Search API.
    
    Parameters:
    - query: Video search query (e.g., 'Python tutorial', 'how to cook pasta')
    - count: Number of videos to return (default: 10, max: 20)
    - country: Country code (default: US)
    - search_lang: Language code (default: en)
    
    Returns video search results with titles, URLs, descriptions, duration, views, and creators.
    Perfect for finding educational content, tutorials, and entertainment videos."""
    
    args_schema: Type[BaseModel] = VideoSearchInput
    
    def _run(self, query: str, count: int = 10, country: str = "US", search_lang: str = "en") -> str:
        try:
            api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not api_key:
                return "Error: BRAVE_SEARCH_API_KEY environment variable not set"
            
            # Validate count
            count = max(1, min(count, 20))
            
            url = "https://api.search.brave.com/res/v1/videos/search"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "country": country,
                "search_lang": search_lang,
                "spellcheck": 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract video results
            results = []
            video_results = data.get("results", [])
            
            for result in video_results:
                video_info = result.get("video", {})
                results.append({
                    "title": result.get("title", "N/A"),
                    "url": result.get("url", "N/A"),
                    "description": result.get("description", "N/A"),
                    "age": result.get("age", "N/A"),
                    "duration": video_info.get("duration", "N/A"),
                    "views": video_info.get("views", "N/A"),
                    "creator": video_info.get("creator", "N/A"),
                    "publisher": video_info.get("publisher", "N/A"),
                    "author": video_info.get("author", {}).get("name", "N/A") if video_info.get("author") else "N/A"
                })
            
            # Format the response
            formatted_results = {
                "search_type": "video_search",
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_metadata": {
                    "country": country,
                    "language": search_lang
                },
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(formatted_results, indent=2)
            
        except requests.RequestException as e:
            return f"Error performing video search: {str(e)}"
        except Exception as e:
            return f"Error processing video search results: {str(e)}"


class BraveAISummarizerTool(BaseTool):
    """Tool for AI-powered search summarization using Brave Search API"""
    
    name: str = "brave_ai_summarizer"
    description: str = """Get an AI-powered summary of search results using Brave Search API.
    
    Parameters:
    - query: Search query to summarize (e.g., 'renewable energy trends 2024', 'AI developments')
    - count: Number of sources to use for summary (default: 10, max: 20)
    - country: Country code (default: US)
    - search_lang: Language code (default: en)
    
    Returns an AI-generated summary based on multiple search results.
    Perfect for getting quick overviews of complex topics with multiple sources."""
    
    args_schema: Type[BaseModel] = SummarizerInput
    
    def _run(self, query: str, count: int = 10, country: str = "US", search_lang: str = "en") -> str:
        try:
            api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not api_key:
                return "Error: BRAVE_SEARCH_API_KEY environment variable not set"
            
            # Validate count
            count = max(1, min(count, 20))
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            
            # First, perform a search with summary enabled
            search_url = "https://api.search.brave.com/res/v1/web/search"
            search_params = {
                "q": query,
                "count": count,
                "country": country,
                "search_lang": search_lang,
                "summary": 1,  # Enable summarizer
                "spellcheck": 1
            }
            
            search_response = requests.get(search_url, headers=headers, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # Check if summarizer key was returned
            summarizer_info = search_data.get("summarizer", {})
            if not summarizer_info.get("key"):
                return "Error: AI summarizer not available for this query"
            
            # Get the summary using the key
            summary_url = "https://api.search.brave.com/res/v1/summarizer/summary"
            summary_params = {
                "key": summarizer_info["key"]
            }
            
            summary_response = requests.get(summary_url, headers=headers, params=summary_params)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            # Extract summary text
            summary_tokens = summary_data.get("summary", [])
            summary_text = "".join([token.get("data", "") for token in summary_tokens if token.get("type") == "token"])
            
            # Format the response
            formatted_results = {
                "search_type": "ai_summary",
                "query": query,
                "summary_title": summary_data.get("title", "Summary"),
                "summary_text": summary_text,
                "status": summary_data.get("status", "unknown"),
                "sources_used": len(search_data.get("web", {}).get("results", [])),
                "search_metadata": {
                    "country": country,
                    "language": search_lang
                },
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(formatted_results, indent=2)
            
        except requests.RequestException as e:
            return f"Error performing AI summarization: {str(e)}"
        except Exception as e:
            return f"Error processing AI summary: {str(e)}"


def get_brave_search_tools():
    """Return a list of all Brave Search tools"""
    return [
        BraveWebSearchTool(),
        BraveNewsSearchTool(),
        BraveImageSearchTool(),
        BraveVideoSearchTool(),
        BraveAISummarizerTool()
    ]


if __name__ == "__main__":
    # Test the tools
    tools = get_brave_search_tools()

    logger.info("Testing Brave Search Tools")
    logger.info("=" * 50)

    # Test web search tool
    logger.info("\n1. Testing Web Search Tool:")
    web_tool = BraveWebSearchTool()
    result = web_tool._run("Python programming tutorial", count=3)
    logger.info(result[:500] + "..." if len(result) > 500 else result)

    # Test news search tool
    logger.info("\n2. Testing News Search Tool:")
    news_tool = BraveNewsSearchTool()
    result = news_tool._run("artificial intelligence", count=3)
    logger.info(result[:500] + "..." if len(result) > 500 else result)

    # Test AI summarizer tool
    logger.info("\n3. Testing AI Summarizer Tool:")
    summarizer_tool = BraveAISummarizerTool()
    result = summarizer_tool._run("renewable energy trends 2024", count=5)
    logger.info(result[:500] + "..." if len(result) > 500 else result)