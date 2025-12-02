import os
from typing import List, Dict, Any
from utils.http_client import HTTPClient


class SerperClient:
    """Client for Serper API (Google search integration)."""
    
    BASE_URL = "https://google.serper.dev/search"
    
    def __init__(self, api_key: str = None):
        """
        Initialize Serper client.
        
        Args:
            api_key: Serper API key. If None, reads from SERPER_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment or arguments")
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a web search using Serper API.
        
        Args:
            query: Search query string
            num_results: Number of results to return (default: 10)
            
        Returns:
            List of search results with 'title', 'link', 'snippet'
        """
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        
        payload = {
            "q": query,
            "num": num_results,
        }
        
        try:
            response = HTTPClient.post(self.BASE_URL, payload, headers)
            results = response.get("organic", [])
            
            # Extract relevant fields
            cleaned_results = [
                {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                }
                for result in results
            ]
            
            return cleaned_results
        except Exception as e:
            print(f"Serper search failed: {e}")
            return []
    
    def get_top_urls(self, query: str, count: int = 4) -> List[str]:
        """
        Get top URLs from search results.
        
        Args:
            query: Search query string
            count: Number of top URLs to return
            
        Returns:
            List of URLs (max 'count' items)
        """
        results = self.search(query, num_results=count)
        return [result["link"] for result in results if result.get("link")]
