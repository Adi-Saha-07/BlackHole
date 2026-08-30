/**
 * BlackHole Search — index.js
 * Page-level logic for homepage and results page.
 * Server data is read from the #bh-page-data JSON island injected by the template.
 */

(function () {
    'use strict';

    /* ── Read server-side data from the hidden div's data-* attributes ── */
    var el       = document.getElementById('bh-page-data');
    var query    = el ? (el.dataset.query || '') : '';
    var cached   = el ? (el.dataset.cached === 'true') : false;

    /* Trending topics (static list — matches what the template renders) */
    var trending = ['AI tools 2025', 'SpaceX Starship', 'Quantum computing', 'Open source LLMs'];

    /* ════════════════════════════════════════
       HOMEPAGE
    ════════════════════════════════════════ */

    /* Trending chips */
    var chipsWrap = document.getElementById('trending-chips');
    if (chipsWrap && trending.length) {
        trending.forEach(function (t) {
            var btn = document.createElement('button');
            btn.className = 'bh-chip';
            btn.innerHTML =
                '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor"' +
                ' stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">' +
                '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>' +
                '<polyline points="17 6 23 6 23 12"/></svg> ' + t;
            btn.addEventListener('click', function () {
                var inp  = document.getElementById('hero-search-input');
                var form = document.getElementById('hero-form');
                if (inp && form) { inp.value = t; form.submit(); }
            });
            chipsWrap.appendChild(btn);
        });
    }

    /* ════════════════════════════════════════
       RESULTS PAGE
    ════════════════════════════════════════ */

    /* Clear button */
    var headerInput = document.getElementById('header-search-input');
    var clearBtn    = document.getElementById('clear-btn');

    if (headerInput && clearBtn) {
        function updateClear() {
            clearBtn.style.display = headerInput.value ? 'flex' : 'none';
        }
        updateClear();
        headerInput.addEventListener('input', updateClear);
        clearBtn.addEventListener('click', function () {
            headerInput.value = '';
            updateClear();
            headerInput.focus();
        });
    }

    /* Staggered result entry animations */
    document.querySelectorAll('.bh-result').forEach(function (el) {
        var idx = parseInt(el.getAttribute('data-index'), 10) || 0;
        el.style.animationDelay = (idx * 0.04) + 's';
    });

    /* Tab switching */
    document.querySelectorAll('.bh-tab').forEach(function (tab) {
        tab.addEventListener('click', function () {
            document.querySelectorAll('.bh-tab').forEach(function (t) {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
        });
    });

    /* Sidebar "Ask AI" button */
    var sidebarBtn  = document.getElementById('sidebar-ask-btn');
    var sidebarText = document.getElementById('sidebar-ask-text');

    if (sidebarBtn && query) {
        if (sidebarText) {
            sidebarText.textContent = 'Get an instant AI overview for "' + query + '"';
        }
        sidebarBtn.addEventListener('click', function () {
            if (typeof openAiPanel === 'function') { openAiPanel(); }
            var input = document.getElementById('ai-chat-input');
            if (input && !input.value) {
                input.value = 'Tell me more about: ' + query;
                input.dispatchEvent(new Event('input'));
            }
        });
    }

    /* AI overview card — async fetch on results page */
    if (query && document.getElementById('ai-overview-card')) {
        (async function loadAiOverview() {
            try {
                var res = await fetch('/api/ai-summary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                if (!res.ok) return;
                var data = await res.json();
                if (data.summary) {
                    var card = document.getElementById('ai-overview-card');
                    var body = document.getElementById('ai-overview-body');
                    card.setAttribute('data-raw-text', data.summary);
                    if (typeof renderAiMarkdown === 'function') {
                        body.innerHTML = renderAiMarkdown(data.summary);
                    } else {
                        body.innerHTML = data.summary.replace(/\n/g, '<br>');
                    }
                    card.style.display = 'block';
                    card.style.animation = 'bhSlideIn 0.3s ease both';
                }
            } catch (e) { /* silent — AI overview is non-critical */ }
        })();
    }

})();
