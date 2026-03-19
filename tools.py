import os
from tavily import TavilyClient

def search(query: str) -> str:
    """
    Executes a search query using the Tavily API and returns the results.
    Handles potential API errors robustly.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not found in environment variables."
        
    try:
        client = TavilyClient(api_key=api_key)
        # We only need the top 3-5 results for the agent to reason over
        response = client.search(query=query, search_depth="basic", max_results=3)
        
        results = response.get("results", [])
        if not results:
            return "No results found for your query. Try rephrasing."
            
        formatted_results = []
        for index, res in enumerate(results, start=1):
            title = res.get("title", "No Title")
            content = res.get("content", "No Content")
            formatted_results.append(f"Result {index}:\nTitle: {title}\nContent: {content}\n")
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Tool Error: The search tool encountered an error: {str(e)}"
