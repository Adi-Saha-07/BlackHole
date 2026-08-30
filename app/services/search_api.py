import os
import logging
import requests

logger = logging.getLogger(__name__)


def fetch_google_search(query: str, api_key: str = None, cx: str = None, num: int = 10, start: int = 1) -> dict:
    """
    Primary search via DuckDuckGo (free, no API key needed).
    Falls back to Google Custom Search API if configured.
    Falls back to cosmic mock data if all else fails.
    """
    # Try DuckDuckGo first (always free, no key needed)
    try:
        return _fetch_duckduckgo(query, num=num)
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}. Trying Google fallback.")

    # Try Google Custom Search as fallback
    api_key = api_key or os.environ.get("GOOGLE_SEARCH_API_KEY", "")
    cx = cx or os.environ.get("GOOGLE_SEARCH_CX", "")
    if api_key and cx:
        try:
            return _fetch_google(query, api_key, cx, num=num, start=start)
        except Exception as e:
            logger.warning(f"Google Custom Search API error: {e}. Using mock data.")

    # Final fallback — cosmic mock data
    logger.warning("All search backends failed. Using cosmic mock data.")
    return get_mock_search_results(query, num=num)


def _fetch_duckduckgo(query: str, num: int = 10) -> dict:
    """Fetch real results from DuckDuckGo via ddgs library."""
    from ddgs import DDGS

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=num):
            results.append({
                "title": r.get("title", "Untitled"),
                "snippet": r.get("body", "No description available."),
                "link": r.get("href", "#"),
                "displayLink": r.get("href", "").split("/")[2] if r.get("href") else "",
                "thumbnail": None
            })

    if not results:
        raise ValueError("DuckDuckGo returned no results.")

    return {
        "query": query,
        "total_results": str(len(results)),
        "search_time": 0.5,
        "items": results,
        "source": "duckduckgo"
    }


def _fetch_google(query: str, api_key: str, cx: str, num: int = 10, start: int = 1) -> dict:
    """Fetch results from Google Custom Search JSON API."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": min(max(num, 1), 10),
        "start": max(start, 1)
    }

    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()
    data = response.json()

    search_info = data.get("searchInformation", {})
    raw_items = data.get("items", [])

    items = []
    for item in raw_items:
        thumbnail = None
        pagemap = item.get("pagemap", {})
        if "cse_thumbnail" in pagemap and pagemap["cse_thumbnail"]:
            thumbnail = pagemap["cse_thumbnail"][0].get("src")
        elif "cse_image" in pagemap and pagemap["cse_image"]:
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


def get_mock_search_results(query: str, num: int = 10) -> dict:
    """Generates cosmic-themed mock search results when all backends fail."""
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


def fetch_image_search(query: str, num: int = 20) -> dict:
    """
    Fetch image results from DuckDuckGo.
    Returns list of {title, image, thumbnail, url, source}.
    """
    try:
        from ddgs import DDGS
        items = []
        with DDGS() as ddgs:
            for r in ddgs.images(query, max_results=num):
                items.append({
                    "title": r.get("title", ""),
                    "image": r.get("image", ""),
                    "thumbnail": r.get("thumbnail", r.get("image", "")),
                    "url": r.get("url", "#"),
                    "source": r.get("source", "")
                })
        return {"query": query, "items": items, "source": "duckduckgo_images"}
    except Exception as e:
        logger.warning(f"DuckDuckGo image search failed: {e}")
        return {"query": query, "items": [], "source": "error", "error": str(e)}


def fetch_video_search(query: str, num: int = 12) -> dict:
    """
    Fetch video results from DuckDuckGo.
    Returns list of {title, description, embed_url, thumbnail, duration, publisher}.
    """
    try:
        from ddgs import DDGS
        items = []
        with DDGS() as ddgs:
            for r in ddgs.videos(query, max_results=num):
                # Build watchable link — prefer embed_html or content
                embed_url = r.get("embed_url", "") or r.get("content", "")
                items.append({
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "embed_url": embed_url,
                    "thumbnail": r.get("images", {}).get("large", "") or r.get("images", {}).get("small", ""),
                    "duration": r.get("duration", ""),
                    "publisher": r.get("publisher", ""),
                    "published": r.get("published", "")
                })
        return {"query": query, "items": items, "source": "duckduckgo_videos"}
    except Exception as e:
        logger.warning(f"DuckDuckGo video search failed: {e}")
        return {"query": query, "items": [], "source": "error", "error": str(e)}
