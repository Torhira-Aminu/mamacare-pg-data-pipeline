/*
 * MamaCare PG — "Resources in your ZIP" card (add-on, no changes to app logic required).
 *
 * Shows resource counts for the user's ZIP from the AWS pipeline's Athena output
 * (window.MAMACARE_ZIP_SUMMARY, loaded from zip_summary.js). The data is SYNTHETIC,
 * and the card says so on screen.
 *
 * Usage in the app:
 *   <script src="zip_summary.js"></script>
 *   <script src="zip-coverage.js"></script>
 *   <div id="zipCoverage"></div>              (where the card should appear)
 *   MamaCareZipCoverage.render(userData.zip); (e.g. at the end of showDashboard)
 */
(function (root) {
  "use strict";

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function normalizeZip(zip) {
    var digits = String(zip == null ? "" : zip).replace(/\D/g, "");
    return digits.length === 5 ? digits : null;
  }

  // Pure function: returns the card's HTML. Kept separate from the DOM so it can be unit-tested.
  function buildCardHtml(summary, rawZip) {
    var badge = '<span class="zc-badge">Synthetic demo data</span>';
    var head = function (title) {
      return '<div class="zc-head"><span class="zc-title">' + title + "</span>" + badge + "</div>";
    };
    var footer = '<p class="zc-note">' + escapeHtml(summary.notice) +
      " Counts come from an AWS S3 → Glue → Athena pipeline.</p>";

    var zip = normalizeZip(rawZip);
    if (!zip) {
      return head("📍 Resources in your ZIP") +
        '<p class="zc-msg">Enter a 5-digit ZIP code to see local resource counts.</p>' + footer;
    }
    var entry = summary.zips[zip];
    if (!entry) {
      return head("📍 Resources near " + escapeHtml(zip)) +
        '<p class="zc-msg">This ZIP isn\'t in our Prince George\'s County dataset. Call 2-1-1 for local referrals.</p>' + footer;
    }
    var rows = Object.keys(summary.type_labels).map(function (t) {
      var n = entry.by_type[t] || 0;
      return '<li class="' + (n ? "zc-has" : "zc-none") + '"><span>' + escapeHtml(summary.type_labels[t]) +
        "</span><strong>" + n + "</strong></li>";
    }).join("");
    return head("📍 Resources in " + escapeHtml(zip) + " · " + escapeHtml(entry.city)) +
      '<p class="zc-total"><strong>' + entry.total + "</strong> listed resources across 8 categories</p>" +
      '<ul class="zc-list">' + rows + "</ul>" + footer;
  }

  var STYLE = [
    ".zc-card{background:#fff;border-radius:16px;padding:16px;margin:16px 0;box-shadow:0 4px 20px rgba(107,63,160,.12);border-left:4px solid var(--purple,#6B3FA0);font-family:inherit}",
    ".zc-head{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}",
    ".zc-title{font-weight:800;font-size:.95rem;color:#1f2937}",
    ".zc-badge{font-size:.7rem;font-weight:700;padding:3px 9px;border-radius:20px;background:#fef3c7;color:#92400e;white-space:nowrap}",
    ".zc-total,.zc-msg{font-size:.85rem;color:#4b5563;margin-top:8px}",
    ".zc-list{list-style:none;padding:0;margin:10px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:6px}",
    ".zc-list li{display:flex;justify-content:space-between;font-size:.82rem;padding:6px 10px;border-radius:8px;background:#f5f3ff;color:#374151}",
    ".zc-list li.zc-none{background:#f9fafb;color:#9ca3af}",
    ".zc-note{font-size:.72rem;color:#6b7280;margin-top:10px;line-height:1.4}",
    "@media(max-width:480px){.zc-list{grid-template-columns:1fr}}"
  ].join("");

  function render(zip, targetId) {
    var doc = root.document;
    var target = doc && doc.getElementById(targetId || "zipCoverage");
    var summary = root.MAMACARE_ZIP_SUMMARY;
    if (!target || !summary) return false; // fail quietly: the rest of the app keeps working
    if (!doc.getElementById("zc-style")) {
      var s = doc.createElement("style");
      s.id = "zc-style";
      s.textContent = STYLE;
      doc.head.appendChild(s);
    }
    target.className = "zc-card";
    target.innerHTML = buildCardHtml(summary, zip);
    return true;
  }

  var api = { render: render, buildCardHtml: buildCardHtml, normalizeZip: normalizeZip, escapeHtml: escapeHtml };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.MamaCareZipCoverage = api;
})(typeof window !== "undefined" ? window : globalThis);
