"""
jaxOS/net/browser.py

The Neural Browser
------------------
A text-based web browser that uses the LLM to "read" the web for you.
It fetches raw HTML, strips tags, and asks the Cortex to summarize 
the content into a retro-futurist display format.
"""

import urllib.request
import urllib.parse
import re
import json
from typing import Dict

def fetch_and_summarize(url: str, llm_func) -> str:
    """
    Fetches a URL and uses the LLM to summarize it.
    
    Args:
        url (str): The URL to visit.
        llm_func (callable): The kernel's _llm_inference method.
        
    Returns:
        str: A summary of the page.
    """
    try:
        # 1. Smart URL Handling
        url = url.strip()
        if " " in url or "." not in url:
            # Treat as search query
            query = urllib.parse.quote(url)
            url = f"https://html.duckduckgo.com/html/?q={query}"
        elif not url.startswith("http"):
            url = "https://" + url
            
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (jaxOS/1.0; NeuralKernel)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        # 2. Strip HTML (Simple Regex)
        text = re.sub('<[^<]+?>', ' ', html)
        text = re.sub('\s+', ' ', text).strip()
        
        # Truncate to fit context window (approx 4000 chars)
        text = text[:4000]
        
        # 3. Ask Cortex to Summarize
        prompt = f"""
        You are the browser engine for jaxOS.
        Read the following website content and summarize it for a text-only retro display.
        Focus on the main headlines or content. Format as a bulleted list.
        
        Website Content:
        {text}
        """
        
        # We need to bypass the JSON enforcement for this specific call 
        # or parse the JSON result if the kernel enforces it.
        # Since the kernel enforces JSON, we should ask for JSON output.
        
        json_prompt = f"""
        You are the browser engine for jaxOS.
        Read the following website content and summarize it.
        Output JSON: {{ "response": "YOUR_SUMMARY_HERE" }}
        
        Website Content:
        {text}
        """
        
        response_json = llm_func(json_prompt)
        try:
            data = json.loads(response_json)
            return data.get("response", "Could not render page.")
        except:
            return "Error: Cortex failed to render page."
            
    except Exception as e:
        return f"Connection Error: {e}"
