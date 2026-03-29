/**
 * Site-wide passive tracker for artificialnouveau.com
 * Silently collects browsing data, stores in localStorage.
 * Shows a subtle surveillance footer + Easter egg panel.
 * Data is surfaced on /miniprojects/your-history/
 */
(function() {
    'use strict';

    // Don't run on the tracking page itself
    if (window.location.pathname.includes('/your-history')) return;

    // --- Data collection ---
    const visit = {
        page: window.location.pathname,
        title: document.title,
        referrer: document.referrer || null,
        timestamp: Date.now(),
        hour: new Date().getHours(),
        scrollDepthMax: 0,
        timeOnPage: 0,
        linksHovered: [],
        linksClicked: [],
        deviceType: ('ontouchstart' in window) ? 'mobile' : 'desktop',
        screenW: screen.width,
        darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches
    };

    // Quick browser detect
    const ua = navigator.userAgent;
    if (ua.includes('Firefox/')) visit.browser = 'Firefox';
    else if (ua.includes('Edg/')) visit.browser = 'Edge';
    else if (ua.includes('Chrome/') && ua.includes('Safari/')) visit.browser = 'Chrome';
    else if (ua.includes('Safari/') && !ua.includes('Chrome')) visit.browser = 'Safari';
    else visit.browser = 'Other';

    // Scroll depth tracking
    let maxScroll = 0;
    document.addEventListener('scroll', function() {
        const docH = document.documentElement.scrollHeight - window.innerHeight;
        if (docH > 0) {
            const pct = Math.round((window.scrollY / docH) * 100);
            if (pct > maxScroll) maxScroll = pct;
            visit.scrollDepthMax = maxScroll;
        }
    });

    // Link hover prediction
    const hoverData = {};
    document.addEventListener('mouseover', function(e) {
        const link = e.target.closest('a');
        if (!link || !link.href) return;
        const href = link.getAttribute('href') || link.href;
        hoverData[href] = { start: performance.now(), text: (link.textContent || '').trim().substring(0, 50) };
    });

    document.addEventListener('mouseout', function(e) {
        const link = e.target.closest('a');
        if (!link || !link.href) return;
        const href = link.getAttribute('href') || link.href;
        if (hoverData[href]) {
            const duration = Math.round(performance.now() - hoverData[href].start);
            if (duration > 200) { // only log meaningful hovers
                visit.linksHovered.push({
                    href: href,
                    text: hoverData[href].text,
                    duration: duration
                });
                // Cap at 20
                if (visit.linksHovered.length > 20) visit.linksHovered.shift();
            }
            delete hoverData[href];
        }
    });

    // Link click tracking
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (!link || !link.href) return;
        visit.linksClicked.push({
            href: link.getAttribute('href') || link.href,
            text: (link.textContent || '').trim().substring(0, 50),
            timestamp: Date.now()
        });
        if (visit.linksClicked.length > 20) visit.linksClicked.shift();
    });

    // Time on page
    const pageStart = Date.now();
    function updateTime() { visit.timeOnPage = Math.round((Date.now() - pageStart) / 1000); }
    setInterval(updateTime, 1000);

    // Save to localStorage on unload + periodically
    function saveVisit() {
        updateTime();
        try {
            const history = JSON.parse(localStorage.getItem('_an_visits') || '[]');
            // Update existing entry for this page or add new
            const existingIdx = history.findIndex(v => v.page === visit.page && v.timestamp === visit.timestamp);
            if (existingIdx >= 0) {
                history[existingIdx] = visit;
            } else {
                history.push(visit);
            }
            // Keep last 50 visits
            while (history.length > 50) history.shift();
            localStorage.setItem('_an_visits', JSON.stringify(history));
        } catch(e) {}
    }

    setInterval(saveVisit, 5000);
    window.addEventListener('beforeunload', saveVisit);
    // Also save on visibility change (mobile backgrounding)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') saveVisit();
    });

    // --- Surveillance footer ---
    function createFooter() {
        const footer = document.createElement('div');
        footer.id = 'surveillance-footer';

        // Gather one-liner info
        const city = ''; // We won't fetch geolocation on every page — too slow
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const browserStr = visit.browser;
        const deviceStr = visit.deviceType === 'mobile' ? 'phone' : 'desktop';

        footer.innerHTML = `
            <span class="sf-text">
                This page knows you're on ${browserStr} (${deviceStr}) at ${timeStr}.
                <a href="/miniprojects/your-history/" class="sf-link">See everything we know &rarr;</a>
                <span class="sf-local">All data stays in your browser. Nothing is sent to us.</span>
            </span>
            <button class="sf-close" aria-label="Dismiss">&times;</button>
        `;

        // Styles
        const style = document.createElement('style');
        style.textContent = `
            #surveillance-footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(10, 0, 20, 0.92);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                border-top: 1px solid rgba(0, 240, 255, 0.15);
                padding: 10px 16px;
                font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
                font-size: 11px;
                color: rgba(184, 168, 216, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                z-index: 10000;
                transform: translateY(100%);
                transition: transform 0.5s ease;
            }
            #surveillance-footer.visible {
                transform: translateY(0);
            }
            #surveillance-footer .sf-link {
                color: rgba(0, 240, 255, 0.8);
                text-decoration: none;
                margin-left: 6px;
            }
            #surveillance-footer .sf-link:hover {
                color: #00f0ff;
                text-decoration: underline;
            }
            #surveillance-footer .sf-close {
                background: none;
                border: none;
                color: rgba(184, 168, 216, 0.4);
                font-size: 16px;
                cursor: pointer;
                padding: 0 4px;
                line-height: 1;
            }
            #surveillance-footer .sf-local {
                display: block;
                font-size: 9px;
                opacity: 0.4;
                margin-top: 2px;
            }
            #surveillance-footer .sf-close:hover {
                color: rgba(255, 16, 240, 0.8);
            }

            /* Easter egg eye icon */
            #surveillance-eye {
                position: fixed;
                bottom: 50px;
                right: 16px;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: rgba(10, 0, 20, 0.85);
                border: 1px solid rgba(0, 240, 255, 0.2);
                cursor: pointer;
                z-index: 10001;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                transition: all 0.3s ease;
                opacity: 0;
                transform: scale(0.8);
            }
            #surveillance-eye.visible {
                opacity: 1;
                transform: scale(1);
            }
            #surveillance-eye:hover {
                border-color: rgba(0, 240, 255, 0.6);
                background: rgba(10, 0, 20, 0.95);
                transform: scale(1.1);
            }

            /* Easter egg panel */
            #surveillance-panel {
                position: fixed;
                bottom: 90px;
                right: 16px;
                width: 280px;
                max-height: 400px;
                overflow-y: auto;
                background: rgba(10, 0, 20, 0.95);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(0, 240, 255, 0.2);
                border-radius: 4px;
                padding: 14px;
                font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
                font-size: 10px;
                color: rgba(184, 168, 216, 0.8);
                z-index: 10001;
                display: none;
                line-height: 1.6;
            }
            #surveillance-panel.open {
                display: block;
            }
            #surveillance-panel .sp-title {
                color: #ff10f0;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 10px;
            }
            #surveillance-panel .sp-line {
                margin-bottom: 4px;
            }
            #surveillance-panel .sp-label {
                color: rgba(184, 168, 216, 0.5);
            }
            #surveillance-panel .sp-value {
                color: #00f0ff;
            }
            #surveillance-panel .sp-warn {
                color: #ffaa00;
            }
            #surveillance-panel .sp-section {
                color: rgba(255, 16, 240, 0.6);
                font-size: 9px;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-top: 10px;
                margin-bottom: 4px;
                border-top: 1px solid rgba(0, 240, 255, 0.1);
                padding-top: 8px;
            }
            #surveillance-panel .sp-footer {
                margin-top: 10px;
                padding-top: 8px;
                border-top: 1px solid rgba(0, 240, 255, 0.1);
                text-align: center;
            }
            #surveillance-panel .sp-footer a {
                color: #00f0ff;
                text-decoration: none;
                font-size: 10px;
            }
            #surveillance-panel .sp-footer a:hover {
                text-decoration: underline;
            }
            @media (max-width: 600px) {
                #surveillance-panel { width: calc(100vw - 32px); right: 16px; }
                #surveillance-footer { font-size: 10px; padding: 8px 12px; }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(footer);

        // Show footer after 5 seconds, unless dismissed before
        const dismissed = sessionStorage.getItem('_an_footer_dismissed');
        if (!dismissed) {
            setTimeout(() => footer.classList.add('visible'), 5000);
        }

        footer.querySelector('.sf-close').addEventListener('click', function() {
            footer.classList.remove('visible');
            sessionStorage.setItem('_an_footer_dismissed', '1');
        });
    }

    // --- Easter egg eye + panel ---
    function createEasterEgg() {
        // Eye icon
        const eye = document.createElement('div');
        eye.id = 'surveillance-eye';
        eye.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(0,240,255,0.6)" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
        document.body.appendChild(eye);

        // Panel
        const panel = document.createElement('div');
        panel.id = 'surveillance-panel';
        document.body.appendChild(panel);

        // Show eye after 8 seconds
        setTimeout(() => eye.classList.add('visible'), 8000);

        let panelOpen = false;
        eye.addEventListener('click', function() {
            panelOpen = !panelOpen;
            if (panelOpen) {
                updatePanel();
                panel.classList.add('open');
                eye.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,16,240,0.8)" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';
            } else {
                panel.classList.remove('open');
                eye.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(0,240,255,0.6)" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
            }
        });
    }

    function updatePanel() {
        const panel = document.getElementById('surveillance-panel');
        if (!panel) return;

        const history = JSON.parse(localStorage.getItem('_an_visits') || '[]');
        const totalVisits = history.length;
        const uniquePages = [...new Set(history.map(v => v.page))];
        const totalTime = history.reduce((sum, v) => sum + (v.timeOnPage || 0), 0);

        let html = '<div class="sp-title">What this page knows</div>';

        // Current session
        html += '<div class="sp-line"><span class="sp-label">Browser:</span> <span class="sp-value">' + visit.browser + '</span></div>';
        html += '<div class="sp-line"><span class="sp-label">Device:</span> <span class="sp-value">' + visit.deviceType + '</span></div>';
        html += '<div class="sp-line"><span class="sp-label">Screen:</span> <span class="sp-value">' + screen.width + '×' + screen.height + '</span></div>';
        html += '<div class="sp-line"><span class="sp-label">Dark mode:</span> <span class="sp-value">' + (visit.darkMode ? 'yes' : 'no') + '</span></div>';
        html += '<div class="sp-line"><span class="sp-label">Time on page:</span> <span class="sp-value">' + visit.timeOnPage + 's</span></div>';
        html += '<div class="sp-line"><span class="sp-label">Scroll depth:</span> <span class="sp-value">' + visit.scrollDepthMax + '%</span></div>';

        // Link hovers
        if (visit.linksHovered.length > 0) {
            html += '<div class="sp-section">Link hover prediction</div>';
            const sorted = [...visit.linksHovered].sort((a, b) => b.duration - a.duration).slice(0, 5);
            sorted.forEach(h => {
                const text = h.text || h.href;
                html += '<div class="sp-line"><span class="sp-warn">' + text.substring(0, 30) + '</span> <span class="sp-label">' + h.duration + 'ms</span></div>';
            });
            html += '<div class="sp-line" style="margin-top:4px;"><span class="sp-label">Longest hover = most likely click. Chrome would have already preloaded it.</span></div>';
        }

        // Cross-site history
        if (totalVisits > 1) {
            html += '<div class="sp-section">Your history on this site</div>';
            html += '<div class="sp-line"><span class="sp-label">Total visits:</span> <span class="sp-warn">' + totalVisits + '</span></div>';
            html += '<div class="sp-line"><span class="sp-label">Pages seen:</span> <span class="sp-warn">' + uniquePages.length + '</span></div>';
            html += '<div class="sp-line"><span class="sp-label">Total time:</span> <span class="sp-warn">' + totalTime + 's</span></div>';

            // Last 3 pages visited
            const recent = history.filter(v => v.page !== visit.page).slice(-3).reverse();
            if (recent.length > 0) {
                html += '<div class="sp-line" style="margin-top:4px;"><span class="sp-label">Recent pages:</span></div>';
                recent.forEach(v => {
                    const time = new Date(v.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    const title = (v.title || v.page).substring(0, 30);
                    html += '<div class="sp-line"><span class="sp-value">' + title + '</span> <span class="sp-label">' + time + '</span></div>';
                });
            }
        }

        html += '<div class="sp-footer"><a href="/miniprojects/your-history/">See the full report &rarr;</a><div style="margin-top:6px; font-size:8px; opacity:0.35;">All data stored locally in your browser. Nothing sent to any server.</div></div>';

        panel.innerHTML = html;
    }

    // Periodically update panel if open
    setInterval(function() {
        const panel = document.getElementById('surveillance-panel');
        if (panel && panel.classList.contains('open')) updatePanel();
    }, 2000);

    // --- Initialize ---
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { createFooter(); createEasterEgg(); });
    } else {
        createFooter();
        createEasterEgg();
    }
})();
