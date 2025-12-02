import requests
from typing import Dict, Any, Optional


class HTTPClient:
    """Generic HTTP client with automatic retry on failure."""

    @staticmethod
    def get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Dict[str, Any]:
        """
        GET request with 1 automatic retry on failure.
        
        Args:
            url: Target URL
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            HTTPError if both attempts fail
        """
        headers = headers or {}
        
        for attempt in range(2):  # Try twice: initial + 1 retry
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == 1:  # Last attempt failed
                    raise HTTPError(f"GET {url} failed after retry: {str(e)}")
                # First attempt failed, will retry
                continue
    
    @staticmethod
    def post(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Dict[str, Any]:
        """
        POST request with 1 automatic retry on failure.
        
        Args:
            url: Target URL
            data: Request body as dictionary
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            HTTPError if both attempts fail
        """
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        
        for attempt in range(2):  # Try twice: initial + 1 retry
            try:
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == 1:  # Last attempt failed
                    raise HTTPError(f"POST {url} failed after retry: {str(e)}")
                # First attempt failed, will retry
                continue
    
    @staticmethod
    def fetch_html(url: str, timeout: int = 10) -> str:
        """
        Fetch raw HTML with 1 automatic retry on failure.
        
        Args:
            url: Target URL
            timeout: Request timeout in seconds
            
        Returns:
            HTML content as string
            
        Raises:
            HTTPError if both attempts fail
        """
        for attempt in range(2):  # Try twice: initial + 1 retry
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == 1:  # Last attempt failed
                    raise HTTPError(f"Fetch HTML {url} failed after retry: {str(e)}")
                # First attempt failed, will retry
                continue


class HTTPError(Exception):
    """Custom HTTP error."""
    pass
