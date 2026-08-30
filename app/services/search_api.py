import os
import logging
import requests

logger = logging.getLogger(__name__)

def fetch_google_search(query: str, api_key: str = None, cx: str = None, num: int = 10, start: int = 1) -> dict:
    """
    Queries the Google Programmable Search Engine API (Custom Search JSON API)
    and returns a clean structured dictionary of results.
    
    If credentials are not configured, returns mock cosmic results to enable
    immediate offline / local UI testing.
    """
    api_key = api_key or os.environ.get("GOOGLE_SEARCH_API_KEY", "")
    cx = cx or os.environ.get("GOOGLE_SEARCH_CX", "")

    # Fallback to rich mock data if credentials are not configured
    if not api_key or not cx:
        logger.warning("Google Custom Search API Key or CX ID not configured. Using cosmic mock data.")
        return get_mock_search_results(query, num=num)

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": min(max(num, 1), 10),
        "start": max(start, 1)
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        search_info = data.get("searchInformation", {})
        raw_items = data.get("items", [])
        
        items = []
        for item in raw_items:
            # Extract thumbnail if present in pagemap metadata
            thumbnail = None
            pagemap = item.get("pagemap", {})
            if "cse_thumbnail" in pagemap and len(pagemap["cse_thumbnail"]) > 0:
                thumbnail = pagemap["cse_thumbnail"][0].get("src")
            elif "cse_image" in pagemap and len(pagemap["cse_image"]) > 0:
                thumbnail = pagemap["cse_image"][0].get("src")
                
            items.append({
                "title": item.get("title", "Untitled"),
                "snippet": item.get("snippet", "No description available."),
                "link": item.get("link", "#"),
                "displayLink": item.get("displayLink", ""),
                "thumbnail": thumbnail
            })
            
        return {
            "query": query,
            "total_results": search_info.get("totalResults", str(len(items))),
            "search_time": search_info.get("searchTime", 0.0),
            "items": items,
            "source": "google_api"
        }
    except requests.RequestException as e:
        logger.warning(f"Google Custom Search API error: {e}. Providing fallback search data.")
        mock_data = get_mock_search_results(query, num=num)
        mock_data["error"] = str(e)
        return mock_data

def get_mock_search_results(query: str, num: int = 10) -> dict:
    """Generates cosmic-themed mock search results for queries when API keys are not supplied."""
    cosmic_data = [
        {
            "title": f"Cosmic Singularity & Exploration: {query}",
            "snippet": f"Detailed astronomical observations, spacetime geometry, and theoretical physics regarding '{query}' at the event horizon of gravitational singularities.",
            "link": f"https://astrophysics.space/voyage/{query.replace(' ', '-').lower()}",
            "displayLink": "astrophysics.space",
            "thumbnail": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=150&auto=format&fit=crop&q=80"
        },
        {
            "title": f"General Relativity & Event Horizons - {query.title()}",
            "snippet": f"Understanding how light, information, and quantum particles interact with relativistic gravitational wells under the '{query}' framework.",
            "link": f"https://relativity.quantum-void.org/phenomena/{query.replace(' ', '_')}",
            "displayLink": "relativity.quantum-void.org",
            "thumbnail": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=150&auto=format&fit=crop&q=80"
        },
        {
            "title": f"Hawking Radiation & Accretion Dynamics: {query}",
            "snippet": f"Quantum fluctuations near the boundary produce steady radiation while matter accelerates to near light-speed in the accretion disk surrounding {query}.",
            "link": f"https://deepspace.science/research/{query.replace(' ', '+')}",
            "displayLink": "deepspace.science",
            "thumbnail": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=150&auto=format&fit=crop&q=80"
        },
        {
            "title": f"Gravitational Lensing Archives - {query.title()}",
            "snippet": f"Space-time curvature acts as a massive natural telescope, warping background starlight around {query} into brilliant Einstein rings.",
            "link": f"https://telescope.observatory.edu/catalog/{query.replace(' ', '')}",
            "displayLink": "telescope.observatory.edu",
            "thumbnail": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=150&auto=format&fit=crop&q=80"
        },
        {
            "title": f"Interstellar Wormholes and Void Pathways: {query}",
            "snippet": f"Investigating theoretical Einstein-Rosen bridges and theoretical topology manipulation relating to {query} across hyper-dimensional manifolds.",
            "link": f"https://interstellar.cosmos/voids/{query.replace(' ', '-').lower()}",
            "displayLink": "interstellar.cosmos",
            "thumbnail": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=150&auto=format&fit=crop&q=80"
        }
    ]
    
    return {
        "query": query,
        "total_results": str(len(cosmic_data)),
        "search_time": 0.042,
        "items": cosmic_data[:num],
        "source": "mock_data"
    }
