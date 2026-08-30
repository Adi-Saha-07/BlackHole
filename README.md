# BlackHole — Fast Search Engine with Intelligent AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=flat-square&logo=flask)
![AI](https://img.shields.io/badge/AI-Groq%20%7C%20Gemini%20%7C%20Llama-gold?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**BlackHole** is a fast, modern web search and multi-modal AI engine built with **Python + Flask**, **Groq Llama/Qwen & Google Gemini AI**, **Redis caching**, and **SQLite analytics**. It features a sleek cosmic dark UI with real-time AI assistance, voice search, live query metrics, and one-click code copy.

---

## ✨ Features

- 🔍 **Web Search**: Integration with Google Custom Search API with cosmic mock fallbacks and live caching.
- 🤖 **BlackHole AI Assistant**: Slide-out neural chat drawer powered by **Groq (Llama / Qwen)** and **Google Gemini**, with local Wikipedia & DuckDuckGo knowledge fallback.
- 📋 **1-Click Copy**: Copy entire AI responses or individual syntax-highlighted code blocks with animated visual feedback.
- ⚡ **Multi-Tier Caching**: Redis query caching with configurable TTL and zero-setup in-memory fallback.
- 🎙️ **Voice Search**: Hands-free voice typing in both the main search bar and AI chat via Web Speech API.
- 📱 **Mobile Optimized**: Push-layout responsive design with mobile-adapted icon search bar.
- 📊 **Search History & Trending**: SQLite-backed query tracking and trending analytics API.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask 3.x, Flask-SQLAlchemy |
| **AI Models** | Groq API (Qwen, Llama), Google Gemini 1.5/2.0 API, Wikipedia REST API |
| **Caching** | Redis (with in-memory fallback) |
| **Database** | SQLite |
| **Frontend** | Jinja2 Templates, Vanilla JavaScript (ES6+), Vanilla CSS |
| **Fonts** | Inter, Outfit, JetBrains Mono, Roboto |

---

## 📂 Project Structure

```text
BlackHole/
├── app/
│   ├── __init__.py           # Flask factory & database initialization
│   ├── config.py             # Application configuration
│   ├── routes.py             # Web routes (/search, /api/ai-chat, /api/trending)
│   ├── models/
│   │   ├── __init__.py
│   │   └── history.py        # QueryLog model & trending algorithms
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py     # Groq, Gemini & Universal Knowledge AI engine
│   │   ├── cache.py          # Redis & in-memory caching layer
│   │   └── search_api.py     # Google Custom Search API client
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Dark mode, responsive design, animations
│   │   └── js/
│   │       ├── index.js      # Page interactions & AI overview renderer
│   │       └── search.js     # Form & tab interactions
│   └── templates/
│       ├── base.html         # Layout, AI chat drawer, voice recognition & copy engine
│       └── index.html        # Homepage & search results template
├── tests/
│   ├── __init__.py
│   └── test_search.py        # Automated test suite
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules for clean commits
├── pyproject.toml            # Project packaging & Vercel deployment config
├── requirements.txt          # Python dependencies
├── run.py                    # Server entry point
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Adi-Saha-07/BlackHole.git
cd BlackHole
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Add your API keys to `.env`:
- **Groq AI (Free)**: Get a free key at [console.groq.com](https://console.groq.com) and set `GROQ_API_KEY=gsk_...`
- **Google Gemini (Optional)**: Get an API key at [Google AI Studio](https://aistudio.google.com/app/apikey) and set `GEMINI_API_KEY=AIzaSy...`
- **Google Search (Optional)**: Set `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX` for live web results.

### 5. Run the Server

```bash
python run.py
```

Open your browser at **`http://127.0.0.1:5000`** 🎉

---

## 🧪 Running Tests

Run the automated test suite:

```bash
python -m unittest discover tests
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
