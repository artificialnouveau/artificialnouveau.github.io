/*
 * The Grant Desk embed widget
 * https://www.artificialnouveau.com/smalltools/grants/
 *
 * Drop-in, dependency-free. Renders the latest open grants, fellowships and
 * residencies from The Grant Desk, with a link back to the source.
 *
 * Usage:
 *   <div id="grant-desk-embed"></div>
 *   <script src="https://www.artificialnouveau.com/smalltools/grants/embed.js"
 *           data-count="6" data-category="ai" data-region="eu" async></script>
 *
 * Optional data-* attributes (all optional):
 *   data-target    id of the container element (default: "grant-desk-embed")
 *   data-count     how many grants to show, 1 to 25 (default: 6)
 *   data-category  filter to one category slug (ai, tech, research, writers,
 *                  film, arts, game, design, curator, audio, cross)
 *   data-region    filter to one region slug (eu, us, uk, nl, asia, africa,
 *                  canada, australia, latam, remote, worldwide)
 *   data-theme     "light" or "dark" (default: "light")
 *
 * Terms: free to embed as-is. The "The Grant Desk" credit link must remain.
 * See https://www.artificialnouveau.com/smalltools/grants/data/ for full terms.
 */
(function () {
  "use strict";

  var BASE = "https://www.artificialnouveau.com/smalltools/grants/";
  var DATA_URL = BASE + "embed.json";
  var HOME_URL = BASE + "?utm_source=grantdeskembed&utm_medium=referral";

  // Find the invoking <script> so we can read its data-* attributes.
  var thisScript =
    document.currentScript ||
    (function () {
      var s = document.getElementsByTagName("script");
      return s[s.length - 1];
    })();

  function attr(name, fallback) {
    var v = thisScript && thisScript.getAttribute("data-" + name);
    return v == null || v === "" ? fallback : v;
  }

  var targetId = attr("target", "grant-desk-embed");
  var count = Math.max(1, Math.min(25, parseInt(attr("count", "6"), 10) || 6));
  var category = (attr("category", "") || "").toLowerCase();
  var region = (attr("region", "") || "").toLowerCase();
  var theme = (attr("theme", "light") || "light").toLowerCase();

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function fmtDeadline(iso) {
    if (!iso) return "Rolling / no fixed deadline";
    var d = new Date(iso + "T00:00:00");
    if (isNaN(d.getTime())) return esc(iso);
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  }

  function injectStyles() {
    if (document.getElementById("grant-desk-embed-styles")) return;
    var dark = theme === "dark";
    var css =
      ".gde{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" +
      "font-size:15px;line-height:1.45;max-width:640px;" +
      "color:" + (dark ? "#e9e4d8" : "#1F1B16") + ";" +
      "background:" + (dark ? "#211d18" : "#F4ECDC") + ";" +
      "border:1px solid " + (dark ? "#3a332a" : "#2A241D") + ";" +
      "border-radius:10px;padding:16px 18px;box-sizing:border-box}" +
      ".gde *{box-sizing:border-box}" +
      ".gde-head{display:flex;align-items:baseline;justify-content:space-between;" +
      "gap:8px;margin:0 0 12px;padding-bottom:10px;border-bottom:1px solid " +
      (dark ? "#3a332a" : "#cbb98f") + "}" +
      ".gde-title{font-weight:700;font-size:15px;letter-spacing:.02em;text-transform:uppercase}" +
      ".gde-title a{color:inherit;text-decoration:none}" +
      ".gde-title a:hover{text-decoration:underline}" +
      ".gde-list{list-style:none;margin:0;padding:0}" +
      ".gde-item{padding:10px 0;border-bottom:1px dotted " +
      (dark ? "#3a332a" : "#cbb98f") + "}" +
      ".gde-item:last-child{border-bottom:0}" +
      ".gde-name{font-weight:600;font-size:15px;margin:0 0 3px}" +
      ".gde-name a{color:inherit;text-decoration:none}" +
      ".gde-name a:hover{text-decoration:underline}" +
      ".gde-meta{font-size:12.5px;opacity:.8;margin:0}" +
      ".gde-dl{font-weight:600}" +
      ".gde-foot{margin:12px 0 0;font-size:12px;opacity:.85;text-align:right}" +
      ".gde-foot a{color:inherit;font-weight:600}" +
      ".gde-empty{opacity:.75;font-size:14px;padding:6px 0}";
    var style = document.createElement("style");
    style.id = "grant-desk-embed-styles";
    style.textContent = css;
    document.head.appendChild(style);
  }

  function render(container, grants) {
    injectStyles();
    var wrap = document.createElement("div");
    wrap.className = "gde";

    var scopeBits = [];
    if (category) scopeBits.push(category);
    if (region) scopeBits.push(region.toUpperCase());
    var scopeLabel = scopeBits.length ? " (" + esc(scopeBits.join(" / ")) + ")" : "";

    var html =
      '<div class="gde-head">' +
      '<span class="gde-title"><a href="' + HOME_URL + '" target="_blank" rel="noopener">The Grant Desk</a></span>' +
      '<span class="gde-title" style="font-weight:500;opacity:.7;text-transform:none">Open calls' + scopeLabel + "</span>" +
      "</div>";

    if (!grants.length) {
      html +=
        '<p class="gde-empty">No open calls match right now. ' +
        '<a href="' + HOME_URL + '" target="_blank" rel="noopener">Browse all on The Grant Desk</a>.</p>';
    } else {
      html += '<ul class="gde-list">';
      grants.forEach(function (g) {
        var link = g.applyUrl || g.grantDeskUrl || HOME_URL;
        var metaBits = [];
        if (g.organization) metaBits.push(esc(g.organization));
        if (g.region) metaBits.push(esc(g.region));
        html +=
          '<li class="gde-item">' +
          '<p class="gde-name"><a href="' + esc(link) + '" target="_blank" rel="noopener">' +
          esc(g.title) + "</a></p>" +
          '<p class="gde-meta">' +
          (metaBits.length ? metaBits.join(" &middot; ") + " &middot; " : "") +
          '<span class="gde-dl">Deadline: ' + fmtDeadline(g.deadline) + "</span></p>" +
          "</li>";
      });
      html += "</ul>";
    }

    html +=
      '<p class="gde-foot">Curated by ' +
      '<a href="' + HOME_URL + '" target="_blank" rel="noopener">The Grant Desk</a></p>';

    wrap.innerHTML = html;
    container.innerHTML = "";
    container.appendChild(wrap);
  }

  function matches(g) {
    if (category && String(g.category || "").toLowerCase() !== category) {
      var extra = (g.categories || []).map(function (c) {
        return String(c).toLowerCase();
      });
      if (extra.indexOf(category) === -1) return false;
    }
    if (region) {
      var r = String(g.region || "").toLowerCase();
      var multi = (g.regions || []).map(function (x) {
        return String(x).toLowerCase();
      });
      if (r !== region && multi.indexOf(region) === -1) return false;
    }
    return true;
  }

  function start() {
    var container = document.getElementById(targetId);
    if (!container) return;

    fetch(DATA_URL, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        var grants = (data && data.grants ? data.grants : []).filter(matches).slice(0, count);
        render(container, grants);
      })
      .catch(function () {
        injectStyles();
        container.innerHTML =
          '<div class="gde"><p class="gde-empty">Grants are on ' +
          '<a href="' + HOME_URL + '" target="_blank" rel="noopener">The Grant Desk</a>.</p></div>';
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
