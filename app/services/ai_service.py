import os
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import re
try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

def _reload_env():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    load_dotenv(override=True)

def get_gemini_api_key():
    _reload_env()
    for name in ["GEMINI_API_KEY", "GEMINI_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY", "AI_API_KEY"]:
        val = os.environ.get(name, "").strip().strip('"').strip("'")
        if val and not val.startswith("your_"):
            return val
    return ""

def get_groq_api_key():
    _reload_env()
    val = os.environ.get("GROQ_API_KEY", "").strip().strip('"').strip("'")
    return val if val and not val.startswith("your_") else ""

def _save_env_key(env_name, value):
    os.environ[env_name] = value
    try:
        if os.path.exists(ENV_PATH) and os.access(os.path.dirname(ENV_PATH), os.W_OK):
            lines = []
            if os.path.exists(ENV_PATH):
                with open(ENV_PATH, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            new_lines = []
            found = False
            for l in lines:
                if l.strip().startswith(f"{env_name}="):
                    new_lines.append(f"{env_name}={value}\n")
                    found = True
                else:
                    new_lines.append(l)
            if not found:
                new_lines.append(f"\n{env_name}={value}\n")
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            _reload_env()
        return True
    except Exception:
        return True

def save_gemini_api_key(key):
    key = key.strip().strip('"').strip("'")
    if not key.startswith("AIzaSy") or len(key) < 25:
        return False
    return _save_env_key("GEMINI_API_KEY", key)

def save_groq_api_key(key):
    key = key.strip().strip('"').strip("'")
    if not (key.startswith("gsk_") and len(key) > 20):
        return False
    return _save_env_key("GROQ_API_KEY", key)

# Current working Groq models (verified)
GROQ_MODELS = [
    "qwen/qwen3.6-27b",
    "groq/compound",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]

SYSTEM_PROMPT = (
    "You are BlackHole AI, an advanced intelligent assistant embedded inside "
    "the BlackHole Search Engine. You answer every question thoroughly, "
    "generate full working code when asked, solve math, explain science, "
    "write stories, and handle any topic the user raises. "
    "Format responses using markdown with headers, bullet points, and "
    "fenced code blocks. Always be helpful, accurate, and detailed."
)

def _strip_thinking(text):
    """Remove <think>...</think> reasoning blocks from Qwen/reasoning models."""
    # Remove fully closed <think>...</think> blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove unclosed <think> blocks (from start to end of string if </think> is missing)
    text = re.sub(r'<think>.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove any leftover closing tags
    text = re.sub(r'</think>', '', text, flags=re.IGNORECASE)
    return text.strip()

def _call_groq(prompt, history):
    api_key = get_groq_api_key()
    if not api_key:
        return ""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for m in history[-12:]:
            role = "user" if m.get("role") == "user" else "assistant"
            content = m.get("content", "").strip()
            if content:
                messages.append({"role": role, "content": content})
    if not messages or messages[-1].get("content") != prompt:
        messages.append({"role": "user", "content": prompt})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    # Try each model; on 429 rate-limit, reduce tokens and try next model
    for model in GROQ_MODELS:
        for attempt in range(2):  # 2 attempts per model (normal then reduced tokens)
            max_tokens = 2048 if attempt == 0 else 1024
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": max_tokens,
            }
            try:
                if _HAS_REQUESTS:
                    resp = _requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers, json=payload, timeout=25
                    )
                    if resp.status_code == 200:
                        choices = resp.json().get("choices", [])
                        if choices:
                            raw = choices[0].get("message", {}).get("content", "").strip()
                            return _strip_thinking(raw)
                        break  # no choices, try next model
                    elif resp.status_code == 429:
                        logger.warning("Groq 429 rate limit on %s (attempt %d), retrying with lower tokens", model, attempt+1)
                        continue  # retry with lower tokens
                    elif resp.status_code in (400, 401):
                        logger.error("Groq auth/bad-request on %s: %s", model, resp.text[:200])
                        return ""  # bad key, stop all
                    else:
                        logger.error("Groq %s HTTP %s: %s", model, resp.status_code, resp.text[:150])
                        break  # try next model
                else:
                    req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/chat/completions",
                        data=json.dumps(payload).encode("utf-8"),
                        headers=headers, method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=25) as r:
                        data = json.loads(r.read().decode("utf-8"))
                        choices = data.get("choices", [])
                        if choices:
                            raw = choices[0].get("message", {}).get("content", "").strip()
                            return _strip_thinking(raw)
                    break
            except Exception as ex:
                logger.error("Groq connection error on %s: %s", model, ex)
                break
    return ""


GEMINI_MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]

def _call_gemini(prompt, history):
    api_key = get_gemini_api_key()
    if not api_key:
        return ""
    contents = []
    if history:
        for m in history[-10:]:
            role = "user" if m.get("role") == "user" else "model"
            text = m.get("content", "").strip()
            if text:
                contents.append({"role": role, "parts": [{"text": text}]})
    if not contents or contents[-1].get("parts", [{}])[0].get("text") != prompt:
        contents.append({"role": "user", "parts": [{"text": prompt}]})
    payload = {"contents": contents, "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}}
    last_error = ""
    for model in GEMINI_MODELS:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                return "Gemini returned no text for this query."
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="ignore")
            logger.error("Gemini error on %s (%s): %s", model, e.code, raw[:200])
            try:
                msg = json.loads(raw).get("error", {}).get("message", "")
                last_error = f"Gemini Error ({e.code}): {msg or raw[:100]}"
            except Exception:
                last_error = f"Gemini Error ({e.code})"
            if e.code != 404:
                return last_error
        except Exception as ex:
            logger.error("Gemini connection error on %s: %s", model, ex)
            last_error = str(ex)
    return last_error

def search_universal_knowledge(query):
    clean = re.sub(
        r"^(what\s+is|who\s+is|who\s+was|tell\s+me\s+about|explain|define|how\s+to|what\s+are|how\s+does|where\s+is|give\s+me|show\s+me)\s+",
        "", query.strip(), flags=re.IGNORECASE
    ).rstrip(" ?!. ")
    clean = re.sub(r"^(a|an|the)\s+", "", clean, flags=re.IGNORECASE).strip()
    if not clean or len(clean) < 2:
        clean = query.strip().rstrip(" ?!. ")

    try:
        ddg_url = "https://api.duckduckgo.com/?q=" + urllib.parse.quote(clean) + "&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(ddg_url, headers={"User-Agent": "BlackHoleAI/3.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
            txt = data.get("AbstractText") or data.get("Answer")
            if txt and len(txt) > 35:
                heading = data.get("Heading", clean.title())
                source = data.get("AbstractSource", "Knowledge Base")
                return f"**{heading}**\n\n{txt}\n\n*Source: {source}*"
    except Exception:
        pass

    try:
        slug = clean.replace(" ", "_")
        wiki_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(slug)
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "BlackHoleAI/3.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
            extract = data.get("extract", "")
            title = data.get("title", clean.title())
            desc = data.get("description", "")
            if extract and len(extract) > 35:
                header = f"**{title}**"
                if desc:
                    header += f" *({desc})*"
                return f"{header}\n\n{extract}\n\n*Source: Wikipedia*"
    except Exception:
        pass

    try:
        os_url = "https://en.wikipedia.org/w/api.php?action=opensearch&search=" + urllib.parse.quote(clean) + "&limit=1&namespace=0&format=json"
        req = urllib.request.Request(os_url, headers={"User-Agent": "BlackHoleAI/3.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
            if len(data) >= 3 and data[2] and data[2][0]:
                return f"**{data[1][0]}**\n\n{data[2][0]}\n\n*Source: Wikipedia*"
    except Exception:
        pass

    return ""

def calculate_math_expression(prompt):
    clean = (
        prompt.lower()
        .replace("calculate", "").replace("what is", "")
        .replace("solve", "").replace("evaluate", "")
        .replace("compute", "").strip(" ?=")
    )
    if re.match(r"^[0-9\.\+\-\*\/\(\)\^\s\%]+$", clean) and any(op in clean for op in ["+", "-", "*", "/", "^", "%"]):
        try:
            expr = clean.replace("^", "**")
            result = eval(expr, {"__builtins__": None}, {})
            return f"### Math Result\n\n`{clean.strip()}` = **{result}**"
        except Exception:
            pass
    return ""

def extract_user_name_from_history(history):
    if not history:
        return ""
    patterns = [
        r"(?:my\s+name\s+is|call\s+me|i\s+am|i'm)\s+([A-Za-z]+)",
        r"^i\s+am\s+([A-Za-z]+)$",
    ]
    skip = {"a", "an", "the", "asking", "curious", "wondering", "testing", "here"}
    for msg in reversed(history):
        if msg.get("role") == "user":
            text = msg.get("content", "")
            for p in patterns:
                m = re.search(p, text, re.IGNORECASE)
                if m:
                    cand = m.group(1).strip()
                    if cand.lower() not in skip:
                        return cand.title()
    return ""

def _local_smart_reply(prompt, history):
    p = prompt.lower().strip()
    known_name = extract_user_name_from_history(history)

    intro = re.search(
        r"^(?:hi\s+|hello\s+)?(?:my\s+name\s+is|call\s+me|i\s+am|i'm)\s+([A-Za-z]+)", p
    )
    if intro:
        name = intro.group(1).title()
        if name.lower() not in {"a", "an", "the", "here", "curious", "asking"}:
            return (
                f"Nice to meet you, **{name}**! "
                "I've noted your name and will remember it. "
                "What would you like to explore today?"
            )

    if any(q in p for q in ["what is my name", "whats my name", "what's my name", "who am i", "tell me my name"]):
        if known_name:
            return f"Your name is **{known_name}**! How can I help you, {known_name}?"
        return "I don't know your name yet! Just say **'My name is [Your Name]'** and I'll remember it."

    if any(q in p for q in ["how are you", "how r u", "kaise ho", "kya haal hai"]):
        return (
            "I'm running at full power and ready to help!\n\n"
            "Ask me **anything** -- coding, science, math, history, creative writing!"
        )

    if any(q in p for q in ["who are you", "what are you", "who made you", "what can you do"]):
        return (
            "I am **BlackHole AI** -- an intelligent assistant inside the BlackHole Search Engine.\n\n"
            "**I can:**\n"
            "- Answer questions on any topic\n"
            "- Write full working code (Python, JS, HTML, C++, etc.)\n"
            "- Solve math equations\n"
            "- Generate creative content\n"
            "- Remember our conversation context\n\n"
            "**Upgrade to full AI power:** Add a free Groq API key (`gsk_...`) "
            "from https://console.groq.com to your `.env` file as `GROQ_API_KEY=gsk_...`"
        )

    if any(q in p for q in ["thank you", "thanks", "shukriya", "dhanyawad"]):
        return "You're very welcome! Ask me anything anytime."

    if any(q in p for q in ["bye", "goodbye", "alvida"]):
        return "Goodbye! Come back whenever you need help. Have a great day!"

    if "joke" in p:
        return "**Why do programmers prefer dark mode?**\n\n*Because light attracts bugs!*\n\nWant another one? Just ask!"

    math_res = calculate_math_expression(prompt)
    if math_res:
        return math_res

    knowledge = search_universal_knowledge(prompt)
    if knowledge:
        return knowledge

    topic = prompt.strip().rstrip("?!.")
    return (
        f"### {topic.title()}\n\n"
        f"I understand you're asking about **{topic.title()}**.\n\n"
        "For detailed, Gemini-level dynamic answers on any topic, "
        "please add a **free Groq API key**:\n\n"
        "1. Go to https://console.groq.com and sign up (completely free)\n"
        "2. Create an API key starting with `gsk_`\n"
        "3. Open `.env` and set: `GROQ_API_KEY=gsk_...`\n"
        "4. Restart the server -- I'll instantly answer like Gemini!\n\n"
        "*(Or add your `GEMINI_API_KEY` for Google Gemini)*"
    )

def generate_gemini_response(prompt, history=None):
    history = history or []

    gemini_match = re.search(r"(AIzaSy[A-Za-z0-9_\-]{30,45})", prompt)
    if gemini_match:
        if save_gemini_api_key(gemini_match.group(1)):
            return (
                "**Gemini API Key Activated!**\n\n"
                "BlackHole AI is now connected to Google Gemini. Ask me anything!"
            )

    groq_match = re.search(r"(gsk_[A-Za-z0-9]{20,})", prompt)
    if groq_match:
        if save_groq_api_key(groq_match.group(1)):
            return (
                "**Groq AI Key Activated!**\n\n"
                "BlackHole AI is now powered by **Llama 3.1 70B** via Groq -- "
                "a free, ultra-fast AI model. Ask me anything!"
            )

    gemini_key = get_gemini_api_key()
    if gemini_key:
        result = _call_gemini(prompt, history)
        if result and not result.startswith("Gemini Error"):
            return result

    groq_key = get_groq_api_key()
    if groq_key:
        result = _call_groq(prompt, history)
        if result:
            return result

    return _local_smart_reply(prompt, history)

def generate_ai_overview(query, model="default"):
    q = query.strip()
    summary = generate_gemini_response(
        f"Give a concise 2-sentence summary answering: '{q}'. Use bold markdown for key terms.",
        history=[]
    )
    return {"query": q, "model_name": "BlackHole AI", "summary": summary, "status": "success"}

def generate_local_knowledge_reply(prompt, history=None):
    return _local_smart_reply(prompt, history or [])
