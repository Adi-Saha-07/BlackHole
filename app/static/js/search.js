/* ============================================================
   BlackHole Search — search.js
   Handles: progress bar, loading state, tab switching with live data
============================================================ */

document.addEventListener('DOMContentLoaded', () => {

    /* ── Progress bar on form submit ── */
    const forms = document.querySelectorAll('form[method="GET"]');
    const progressBar = document.getElementById('progress-bar');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            if (progressBar) progressBar.classList.add('active');
        });
    });

    /* ── Clear button visibility for hero search ── */
    const heroInput = document.getElementById('hero-search-input');
    if (heroInput) heroInput.focus();

    /* ── Result hover micro-animation ── */
    document.querySelectorAll('.bh-result').forEach((r, i) => {
        r.style.animationDelay = `${i * 0.04}s`;
    });

    /* ── Tab switching with real data ── */
    const tabs       = document.querySelectorAll('.bh-tab');
    const mainArea   = document.querySelector('.bh-results-main');
    const pageData   = document.getElementById('bh-page-data');
    const query      = pageData ? pageData.getAttribute('data-query') : '';

    // Cache the original "All" HTML so we can restore it
    let allResultsHTML = mainArea ? mainArea.innerHTML : '';

    tabs.forEach(tab => {
        tab.addEventListener('click', async () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const label = tab.textContent.trim().toLowerCase();

            if (label === 'all') {
                if (mainArea) mainArea.innerHTML = allResultsHTML;
                return;
            }

            if (!query) return;

            if (label === 'images') {
                await loadImages(query, mainArea);
            } else if (label === 'videos') {
                await loadVideos(query, mainArea);
            } else if (label === 'news') {
                await loadNews(query, mainArea);
            }
        });
    });

    /* ──────────────────────────────────────────
       IMAGE SEARCH
    ────────────────────────────────────────── */
    async function loadImages(q, container) {
        container.innerHTML = renderLoader('Searching images…');
        try {
            const res  = await fetch(`/api/images?q=${encodeURIComponent(q)}&num=20`);
            const data = await res.json();
            const items = data.items || [];

            if (!items.length) {
                container.innerHTML = renderEmpty('No images found for this query.');
                return;
            }

            container.innerHTML = `
                <div class="bh-img-grid">
                    ${items.map(img => `
                        <a class="bh-img-card" href="${escHtml(img.url)}" target="_blank" rel="noopener">
                            <div class="bh-img-thumb-wrap">
                                <img
                                    src="${escHtml(img.thumbnail || img.image)}"
                                    alt="${escHtml(img.title)}"
                                    loading="lazy"
                                    onerror="this.parentElement.parentElement.style.display='none'"
                                />
                            </div>
                            <p class="bh-img-caption">${escHtml(img.title)}</p>
                        </a>
                    `).join('')}
                </div>`;
        } catch (e) {
            container.innerHTML = renderEmpty('Failed to load images. Please try again.');
        }
    }

    /* ──────────────────────────────────────────
       VIDEO SEARCH
    ────────────────────────────────────────── */
    async function loadVideos(q, container) {
        container.innerHTML = renderLoader('Searching videos…');
        try {
            const res  = await fetch(`/api/videos?q=${encodeURIComponent(q)}&num=12`);
            const data = await res.json();
            const items = data.items || [];

            if (!items.length) {
                container.innerHTML = renderEmpty('No videos found for this query.');
                return;
            }

            container.innerHTML = `
                <div class="bh-video-grid">
                    ${items.map(v => `
                        <a class="bh-video-card" href="${escHtml(v.embed_url || '#')}" target="_blank" rel="noopener">
                            <div class="bh-video-thumb-wrap">
                                ${v.thumbnail
                                    ? `<img src="${escHtml(v.thumbnail)}" alt="${escHtml(v.title)}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=bh-video-thumb-placeholder></div>'" />`
                                    : `<div class="bh-video-thumb-placeholder"></div>`
                                }
                                <div class="bh-video-play-icon">
                                    <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                                </div>
                                ${v.duration ? `<span class="bh-video-duration">${escHtml(v.duration)}</span>` : ''}
                            </div>
                            <div class="bh-video-info">
                                <p class="bh-video-title">${escHtml(v.title)}</p>
                                ${v.publisher ? `<span class="bh-video-pub">${escHtml(v.publisher)}</span>` : ''}
                                ${v.description ? `<p class="bh-video-desc">${escHtml(v.description.slice(0, 120))}…</p>` : ''}
                            </div>
                        </a>
                    `).join('')}
                </div>`;
        } catch (e) {
            container.innerHTML = renderEmpty('Failed to load videos. Please try again.');
        }
    }

    /* ──────────────────────────────────────────
       NEWS — reuse web search with "news" appended
    ────────────────────────────────────────── */
    async function loadNews(q, container) {
        container.innerHTML = renderLoader('Fetching latest news…');
        try {
            const res  = await fetch(`/search?q=${encodeURIComponent(q + ' news')}&format=json`);
            const data = await res.json();
            const items = data.items || [];

            if (!items.length) {
                container.innerHTML = renderEmpty('No news found for this query.');
                return;
            }

            container.innerHTML = `<div class="bh-results-list">
                ${items.map((item, i) => `
                    <article class="bh-result" style="animation-delay:${i * 0.04}s">
                        <div class="bh-result-body">
                            <div class="bh-result-url">
                                ${item.thumbnail ? `<img src="${escHtml(item.thumbnail)}" class="bh-favicon" alt="">` : ''}
                                <span>${escHtml(item.displayLink)}</span>
                            </div>
                            <h3 class="bh-result-title"><a href="${escHtml(item.link)}" target="_blank" rel="noopener">${escHtml(item.title)}</a></h3>
                            <p class="bh-result-snippet">${escHtml(item.snippet)}</p>
                        </div>
                    </article>
                `).join('')}
            </div>`;
        } catch (e) {
            container.innerHTML = renderEmpty('Failed to load news. Please try again.');
        }
    }

    /* ──────────────────────────────────────────
       HELPERS
    ────────────────────────────────────────── */
    function escHtml(str) {
        return String(str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function renderLoader(msg) {
        return `<div class="bh-tab-loader">
            <div class="bh-typing"><span></span><span></span><span></span></div>
            <p>${msg}</p>
        </div>`;
    }

    function renderEmpty(msg) {
        return `<div class="bh-tab-empty">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.5" opacity="0.5">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <p>${msg}</p>
        </div>`;
    }

});
