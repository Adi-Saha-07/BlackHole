/* ============================================================
   BlackHole Search — search.js
   Handles: progress bar, loading state, clear button
   (AI chat logic lives in base.html for template access)
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
    if (heroInput) {
        heroInput.focus();
    }

    /* ── Tab switching (visual only for now) ── */
    const tabs = document.querySelectorAll('.bh-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });

    /* ── Result hover micro-interaction ── */
    const results = document.querySelectorAll('.bh-result');
    results.forEach((r, i) => {
        r.style.animationDelay = `${i * 0.04}s`;
    });
});
