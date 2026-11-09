// Run with: node --test app-integration/zip-coverage.test.js
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "zip_summary.js"), "utf8"), sandbox);
const summary = sandbox.window.MAMACARE_ZIP_SUMMARY;
const w = require("./zip-coverage.js");

test("summary is marked synthetic and covers 27 ZIPs", () => {
  assert.strictEqual(summary.synthetic, true);
  assert.strictEqual(Object.keys(summary.zips).length, 27);
});

test("known ZIP shows city, total and all 8 categories", () => {
  const html = w.buildCardHtml(summary, "20743");
  assert.match(html, /20743 · Capitol Heights/);
  assert.match(html, /<strong>10<\/strong> listed resources/);
  assert.strictEqual((html.match(/<li /g) || []).length, 8);
});

test("every card is labeled synthetic", () => {
  for (const z of ["20743", "99999", "", "abc"]) {
    assert.match(w.buildCardHtml(summary, z), /Synthetic demo data/);
  }
});

test("ZIP outside dataset gets a 2-1-1 referral, not an error", () => {
  assert.match(w.buildCardHtml(summary, "21201"), /isn't in our Prince George's County dataset/);
});

test("invalid ZIP asks for 5 digits", () => {
  assert.match(w.buildCardHtml(summary, "207"), /Enter a 5-digit ZIP/);
  assert.strictEqual(w.normalizeZip(" 20743 "), "20743");
});

test("user input is escaped (no HTML injection)", () => {
  const html = w.buildCardHtml(summary, "<img src=x onerror=alert(1)>12345");
  assert.doesNotMatch(html, /<img/);
});

test("card totals equal the per-type counts for every ZIP", () => {
  for (const [z, e] of Object.entries(summary.zips)) {
    assert.strictEqual(Object.values(e.by_type).reduce((a, b) => a + b, 0), e.total, z);
  }
});
