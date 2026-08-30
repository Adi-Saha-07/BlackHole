from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.search_api import fetch_google_search
from app.services.cache import cache_service
from app.models.history import QueryLog
from app.services.ai_service import generate_ai_overview, generate_gemini_response
import os

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Renders the main search page. If ?q= is present, runs search and passes results."""
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("index.html", query=None, results=None, cached=False, error=None)

    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    api_key = current_app.config.get("GOOGLE_SEARCH_API_KEY")
    cx = current_app.config.get("GOOGLE_SEARCH_CX")
    ttl = current_app.config.get("CACHE_DEFAULT_TTL", 600)

    # Check cache
    cached_data = cache_service.get(query)
    if cached_data is not None:
        items = cached_data.get("items", [])
        search_time = cached_data.get("search_time", 0.0)
        QueryLog.log(query=query, result_count=len(items), search_time=search_time, cached=True, client_ip=client_ip)
        return render_template("index.html", query=query, results=items, cached=True, error=None)

    # Fetch live results
    try:
        results_data = fetch_google_search(query=query, api_key=api_key, cx=cx)
        items = results_data.get("items", [])
        search_time = results_data.get("search_time", 0.0)
        if items:
            cache_service.set(query, results_data, ttl=ttl)
        QueryLog.log(query=query, result_count=len(items), search_time=search_time, cached=False, client_ip=client_ip)
        return render_template("index.html", query=query, results=items, cached=False, error=None)
    except Exception as e:
        return render_template("index.html", query=query, results=[], cached=False, error=str(e))

@main_bp.route("/api/ai-summary", methods=["GET", "POST"])
def api_ai_summary():
    """Returns synthesized AI overview for a query and selected model."""
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        query = data.get("query", "").strip()
        model = data.get("model", "blackhole-ai").strip()
    else:
        query = request.args.get("q", "").strip()
        model = request.args.get("model", "blackhole-ai").strip()

    if not query:
        return jsonify({"status": "error", "message": "Query is required."}), 400

    summary_data = generate_ai_overview(query=query, model=model)
    return jsonify(summary_data)



@main_bp.route("/api/ai-chat", methods=["POST"])
def api_ai_chat():
    """BlackHole AI chat endpoint — proxies to Google Gemini API."""
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Message is required."}), 400

    reply = generate_gemini_response(prompt=message, history=history)
    return jsonify({"reply": reply})

@main_bp.route("/api/trending", methods=["GET"])
def api_trending():
    """Returns trending search queries in JSON."""
    trending = QueryLog.get_trending(limit=10, days=7)
    return jsonify({
        "status": "success",
        "trending": trending
    })

@main_bp.route("/search", methods=["GET"])
def search():
    """
    Search route. Takes query parameter 'q'.
    Checks Redis cache first; if not found, queries search API,
    caches result for configured TTL, logs search in SQLite,
    and returns structured JSON.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({
            "status": "error",
            "message": "Query parameter 'q' is required.",
            "items": []
        }), 400

    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # 1. Check Redis / Memory cache
    cached_data = cache_service.get(query)
    if cached_data is not None:
        items = cached_data.get("items", [])
        search_time = cached_data.get("search_time", 0.0)
        # Log cache hit
        QueryLog.log(
            query=query, 
            result_count=len(items), 
            search_time=search_time, 
            cached=True, 
            client_ip=client_ip
        )
        return jsonify({
            "status": "success",
            "query": query,
            "total_results": cached_data.get("total_results", "0"),
            "search_time": search_time,
            "items": items,
            "source": cached_data.get("source", "google_api"),
            "cached": True
        })

    # 2. Fetch from Google Custom Search API
    api_key = current_app.config.get("GOOGLE_SEARCH_API_KEY")
    cx = current_app.config.get("GOOGLE_SEARCH_CX")
    ttl = current_app.config.get("CACHE_DEFAULT_TTL", 600)

    results = fetch_google_search(query=query, api_key=api_key, cx=cx)
    items = results.get("items", [])
    search_time = results.get("search_time", 0.0)

    # 3. Store in cache if successful
    if items:
        cache_service.set(query, results, ttl=ttl)

    # 4. Log search query in SQLite database
    QueryLog.log(
        query=query, 
        result_count=len(items), 
        search_time=search_time, 
        cached=False, 
        client_ip=client_ip
    )

    return jsonify({
        "status": "success",
        "query": query,
        "total_results": results.get("total_results", "0"),
        "search_time": search_time,
        "items": items,
        "source": results.get("source", "google_api"),
        "cached": False
    })
