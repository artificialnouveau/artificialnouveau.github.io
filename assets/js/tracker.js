/**
 * Site-wide passive tracker for artificialnouveau.com
 * Silently collects browsing data, stores in localStorage.
 * Shows a unified surveillance bar at the bottom.
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
            if (duration > 200) {
                visit.linksHovered.push({ href, text: hoverData[href].text, duration });
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

    // Save to localStorage
    function saveVisit() {
        updateTime();
        try {
            const history = JSON.parse(localStorage.getItem('_an_visits') || '[]');
            const existingIdx = history.findIndex(v => v.page === visit.page && v.timestamp === visit.timestamp);
            if (existingIdx >= 0) history[existingIdx] = visit;
            else history.push(visit);
            while (history.length > 50) history.shift();
            localStorage.setItem('_an_visits', JSON.stringify(history));
        } catch(e) {}
    }
    setInterval(saveVisit, 5000);
    window.addEventListener('beforeunload', saveVisit);
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') saveVisit();
    });

    // --- Unified surveillance bar ---
    function createBar() {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const browserStr = visit.browser;
        const deviceStr = visit.deviceType === 'mobile' ? 'phone' : 'desktop';

        const bar = document.createElement('div');
        bar.id = 'sv-bar';
        bar.innerHTML = `
            <div class="sv-summary">
                <span class="sv-eye">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </span>
                <span class="sv-info">This page knows you're on ${browserStr} (${deviceStr}) at ${timeStr}.</span>
                <a href="/miniprojects/your-history/" class="sv-link">Full report &rarr;</a>
                <button class="sv-toggle" aria-label="Expand details">&#9650;</button>
                <button class="sv-close" aria-label="Dismiss">&times;</button>
            </div>
            <div class="sv-details">
                <div class="sv-details-inner" id="sv-details-inner"></div>
                <div class="sv-local">All data stored locally in your browser. Nothing sent to any server.</div>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            #sv-bar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(10, 0, 20, 0.94);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-top: 1px solid rgba(0, 240, 255, 0.15);
                font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
                font-size: 11px;
                color: rgba(184, 168, 216, 0.7);
                z-index: 10000;
                transform: translateY(100%);
                transition: transform 0.5s ease;
            }
            #sv-bar.visible { transform: translateY(0); }

            .sv-summary {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 14px;
            }
            .sv-eye {
                color: rgba(0, 240, 255, 0.5);
                display: flex;
                align-items: center;
                flex-shrink: 0;
            }
            .sv-info { flex: 1; min-width: 0; }
            .sv-link {
                color: rgba(0, 240, 255, 0.7);
                text-decoration: none;
                white-space: nowrap;
                flex-shrink: 0;
            }
            .sv-link:hover { color: #00f0ff; text-decoration: underline; }
            .sv-toggle, .sv-close {
                background: none;
                border: none;
                color: rgba(184, 168, 216, 0.4);
                font-size: 12px;
                cursor: pointer;
                padding: 2px 4px;
                line-height: 1;
                flex-shrink: 0;
            }
            .sv-toggle:hover, .sv-close:hover { color: rgba(0, 240, 255, 0.8); }
            .sv-toggle.open { transform: rotate(180deg); }

            .sv-details {
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.4s ease, padding 0.4s ease;
                padding: 0 14px;
            }
            .sv-details.open {
                max-height: 400px;
                padding: 0 14px 10px;
                overflow-y: auto;
            }
            .sv-details-inner {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 3px 16px;
                font-size: 10px;
                line-height: 1.7;
            }
            .sv-details .sv-dl { color: rgba(184, 168, 216, 0.45); }
            .sv-details .sv-dv { color: #00f0ff; }
            .sv-details .sv-dw { color: #ffaa00; }
            .sv-details .sv-section {
                grid-column: 1 / -1;
                color: rgba(255, 16, 240, 0.5);
                font-size: 9px;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-top: 6px;
                padding-top: 6px;
                border-top: 1px solid rgba(0, 240, 255, 0.08);
            }
            .sv-details .sv-full { grid-column: 1 / -1; }
            .sv-local {
                font-size: 8px;
                opacity: 0.3;
                text-align: center;
                margin-top: 6px;
            }

            @media (max-width: 600px) {
                #sv-bar { font-size: 10px; }
                .sv-summary { padding: 6px 10px; gap: 6px; }
                .sv-details-inner { grid-template-columns: 1fr; }
                .sv-link { display: none; }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(bar);

        // Show after 5s unless dismissed
        if (!sessionStorage.getItem('_an_bar_dismissed')) {
            setTimeout(() => bar.classList.add('visible'), 5000);
        }

        // Close
        bar.querySelector('.sv-close').addEventListener('click', function() {
            bar.classList.remove('visible');
            sessionStorage.setItem('_an_bar_dismissed', '1');
        });

        // Toggle details
        const toggleBtn = bar.querySelector('.sv-toggle');
        const details = bar.querySelector('.sv-details');
        let expanded = false;

        toggleBtn.addEventListener('click', function() {
            expanded = !expanded;
            if (expanded) {
                updateDetails();
                details.classList.add('open');
                toggleBtn.classList.add('open');
            } else {
                details.classList.remove('open');
                toggleBtn.classList.remove('open');
            }
        });

        // Update details periodically when open
        setInterval(function() {
            if (expanded) updateDetails();
        }, 2000);
    }

    function updateDetails() {
        const inner = document.getElementById('sv-details-inner');
        if (!inner) return;

        const history = JSON.parse(localStorage.getItem('_an_visits') || '[]');
        const totalVisits = history.length;
        const uniquePages = [...new Set(history.map(v => v.page))];
        const totalTime = history.reduce((sum, v) => sum + (v.timeOnPage || 0), 0);

        let html = '';

        // Current page stats
        html += `<span class="sv-dl">Browser</span><span class="sv-dv">${visit.browser}</span>`;
        html += `<span class="sv-dl">Device</span><span class="sv-dv">${visit.deviceType}</span>`;
        html += `<span class="sv-dl">Screen</span><span class="sv-dv">${screen.width}&times;${screen.height}</span>`;
        html += `<span class="sv-dl">Dark mode</span><span class="sv-dv">${visit.darkMode ? 'yes' : 'no'}</span>`;
        html += `<span class="sv-dl">Time on page</span><span class="sv-dv">${visit.timeOnPage}s</span>`;
        html += `<span class="sv-dl">Scroll depth</span><span class="sv-dv">${visit.scrollDepthMax}%</span>`;

        // Link hovers
        if (visit.linksHovered.length > 0) {
            html += '<div class="sv-section">Link hover prediction</div>';
            const sorted = [...visit.linksHovered].sort((a, b) => b.duration - a.duration).slice(0, 3);
            sorted.forEach(h => {
                const text = (h.text || h.href).substring(0, 25);
                html += `<span class="sv-dw">${text}</span><span class="sv-dl">${h.duration}ms</span>`;
            });
            html += '<div class="sv-full" style="font-size:9px; opacity:0.5; margin-top:2px;">Longest hover = most likely click. Chrome would preload it.</div>';
        }

        // Cross-site history
        if (totalVisits > 1) {
            html += '<div class="sv-section">Your history on this site</div>';
            html += `<span class="sv-dl">Total visits</span><span class="sv-dw">${totalVisits}</span>`;
            html += `<span class="sv-dl">Pages seen</span><span class="sv-dw">${uniquePages.length}</span>`;
            html += `<span class="sv-dl">Total time</span><span class="sv-dw">${totalTime}s</span>`;

            const recent = history.filter(v => v.page !== visit.page).slice(-3).reverse();
            if (recent.length > 0) {
                html += '<div class="sv-full" style="margin-top:4px;"><span class="sv-dl">Recent:</span></div>';
                recent.forEach(v => {
                    const time = new Date(v.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    const title = (v.title || v.page).substring(0, 25);
                    html += `<span class="sv-dv">${title}</span><span class="sv-dl">${time}</span>`;
                });
            }
        }

        // Full report link at bottom of details
        html += `<div class="sv-full" style="text-align:center; margin-top:8px; padding-top:6px; border-top:1px solid rgba(0,240,255,0.08);"><a href="/miniprojects/your-history/" style="color:#00f0ff; text-decoration:none; font-size:10px;">See the full report &rarr;</a></div>`;

        inner.innerHTML = html;
    }

    // --- Initialize ---
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createBar);
    } else {
        createBar();
    }
})();
