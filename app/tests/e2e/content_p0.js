// Tablet browser check for the content platform foundation page (P0), against a LOCAL server with a throwaway database.
// Usage: BASE=http://127.0.0.1:8099 PASSWORD=... TOTP_SECRET=<base32> OUT=<dir> node tests/e2e/content_p0.js
// Signs in through the real login form (password + TOTP), then checks the Content page at both tablet orientations.
const { chromium } = require("playwright");
const crypto = require("crypto"), fs = require("fs"), path = require("path");
const BASE = process.env.BASE || "http://127.0.0.1:8099", PASSWORD = process.env.PASSWORD, SECRET = process.env.TOTP_SECRET, OUT = process.env.OUT || "/tmp/e2e-content";
fs.mkdirSync(OUT, { recursive: true });
const results = [];

function b32(s) { const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"; let bits = ""; for (const c of s.replace(/=+$/, "")) bits += A.indexOf(c).toString(2).padStart(5, "0"); const out = []; for (let i = 0; i + 8 <= bits.length; i += 8) out.push(parseInt(bits.slice(i, i + 8), 2)); return Buffer.from(out); }
function totp(step) { const b = Buffer.alloc(8); b.writeBigUInt64BE(BigInt(step)); const h = crypto.createHmac("sha1", b32(SECRET)).update(b).digest(); const o = h[h.length - 1] & 15; return String((h.readUInt32BE(o) & 0x7fffffff) % 1e6).padStart(6, "0"); }

(async () => {
  const browser = await chromium.launch();
  const VIEWPORTS = [["landscape", { width: 1280, height: 800 }], ["portrait", { width: 800, height: 1280 }]];
  let token = null;
  const consoleErrors = [], bad = [];

  for (const [orient, vp] of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: vp, hasTouch: true, isMobile: false, deviceScaleFactor: 1 });
    if (token) await ctx.addInitScript(t => { try { localStorage.setItem("od_token", t); } catch (e) {} }, token);
    const page = await ctx.newPage();
    // G1/G2 deliberately make unauthenticated calls; Chrome logs those 401s as resource errors. Anything else is a real error.
    page.on("console", m => { if (m.type() === "error" && !/status of 401/.test(m.text())) consoleErrors.push(`[${orient}] ${m.text()}`); });
    page.on("pageerror", e => consoleErrors.push(`[${orient}] pageerror: ${e.message}`));
    page.on("response", r => { if (r.status() >= 500) bad.push(`[${orient}] ${r.status()} ${r.url()}`); });
    const step = async (id, name, fn) => {
      try { await fn(); results.push({ orient, id, name, status: "passed" }); console.log("PASS", orient, id, name); }
      catch (e) { results.push({ orient, id, name, status: "failed", error: String(e.message).split("\n")[0] }); console.log("FAIL", orient, id, name, "-", String(e.message).split("\n")[0]); await page.screenshot({ path: path.join(OUT, `FAIL_${orient}_${id}.png`) }).catch(() => {}); }
    };
    await page.goto(BASE + "/");

    if (!token) {
      await step("A1", "Real sign-in with password + authenticator code opens the shell", async () => {
        await page.locator("#login").waitFor({ state: "visible", timeout: 8000 });
        await page.fill("#l_pw", PASSWORD);
        await page.fill("#l_code", totp(Math.floor(Date.now() / 30000)));  // current step; setup used step-1, so this is strictly newer
        await page.click("#l_go");
        await page.locator("#shell").waitFor({ state: "visible", timeout: 8000 });
        token = await page.evaluate(() => localStorage.getItem("od_token"));
        if (!token) throw new Error("no session token stored");
      });
    }
    await step("A2", "Shell is visible", async () => { await page.locator("#shell").waitFor({ state: "visible", timeout: 8000 }); });

    await step("B1", orient === "landscape" ? "Landscape: side navigation visible, tab bar hidden" : "Portrait: tab bar visible, side navigation hidden", async () => {
      const side = await page.locator(".side").isVisible(), tabs = await page.locator("#nav-tabs").isVisible();
      if (orient === "landscape" && !(side && !tabs)) throw new Error(`side=${side} tabs=${tabs}`);
      if (orient === "portrait" && !(tabs && !side)) throw new Error(`side=${side} tabs=${tabs}`);
    });
    const nav = orient === "landscape" ? "#nav-side" : "#nav-tabs";
    await step("B2", "Content is in the navigation and opens the page", async () => {
      await page.locator(`${nav} a[data-page=content]`).click();
      await page.locator("#page-title").filter({ hasText: "Content" }).waitFor({ timeout: 6000 });
      await page.getByText("Foundation only").first().waitFor({ timeout: 6000 });
    });
    await step("C1", "Page shows live database state (RLS on, queried as content_app)", async () => {
      await page.getByText("Row-level security on").first().waitFor({ timeout: 4000 });
      await page.getByText("Queries run as content_app").first().waitFor({ timeout: 4000 });
      await page.getByText("Database ready").first().waitFor({ timeout: 4000 });
    });
    await step("C2", "Table tiles show the real row counts (4 series, 1 course plan, 3 sample claims)", async () => {
      const count = async name => Number(await page.locator(".tile", { has: page.locator(".label", { hasText: new RegExp(`^${name}$`) }) }).locator(".stat").innerText());
      const got = { series: await count("series"), course_plan: await count("course_plan"), claims: await count("claims"), episodes: await count("episodes"), hide_list: await count("hide_list") };
      const want = { series: 4, course_plan: 1, claims: 3, episodes: 1, hide_list: 1 };
      if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`got ${JSON.stringify(got)} want ${JSON.stringify(want)}`);
    });
    await step("C3", "Every table tile says RLS forced; none says missing", async () => {
      const forced = await page.getByText("RLS forced", { exact: true }).count(), missing = await page.getByText("RLS missing").count();
      if (forced !== 19 || missing !== 0) throw new Error(`forced=${forced} missing=${missing}`);
    });
    await step("C4", "Planned work is labelled NOT BUILT (nothing presented as finished)", async () => {
      await page.getByText("Not built yet").first().waitFor({ timeout: 4000 });
      for (const p of ["P1", "P2", "P5", "P9", "P10"]) await page.locator(".pill", { hasText: new RegExp(`^${p}$`) }).first().waitFor({ timeout: 2000 });
    });
    await step("C5", "Hide-list term is never shown on screen", async () => {
      const body = await page.locator("body").innerText();
      if (body.includes("SAMPLE-HIDDEN-TERM")) throw new Error("hide-list term leaked into the page");
    });
    await step("D1", "No horizontal scrolling at this width", async () => {
      const o = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
      if (o.sw > o.cw + 1) throw new Error(`page scrolls horizontally: ${o.sw} > ${o.cw}`);
    });
    await step("D2", "Tab bar fits all 5 tabs without scrolling (portrait only)", async () => {
      if (orient !== "portrait") return;
      const o = await page.evaluate(() => { const t = document.getElementById("nav-tabs"); return { sw: t.scrollWidth, cw: t.clientWidth, n: t.querySelectorAll("a").length }; });
      if (o.n !== 5 || o.sw > o.cw + 1) throw new Error(JSON.stringify(o));
    });
    await step("D3", "Touch targets are at least 48px: navigation and the Refresh button", async () => {
      const boxes = await page.evaluate(nav => [...document.querySelectorAll(`${nav} a`), ...document.querySelectorAll("#view button")].filter(e => e.offsetParent).map(e => { const r = e.getBoundingClientRect(); return { t: (e.textContent || "").trim(), w: Math.round(r.width), h: Math.round(r.height) }; }), nav);
      const small = boxes.filter(b => b.h < 48 || b.w < 48);
      if (!boxes.length || small.length) throw new Error("too small: " + JSON.stringify(small));
    });
    await step("D4", "Refresh button works by touch (tap)", async () => {
      await page.getByRole("button", { name: "Refresh" }).tap();
      await page.getByText("Foundation only").first().waitFor({ timeout: 4000 });
    });
    await page.screenshot({ path: path.join(OUT, `content_${orient}_light.png`), fullPage: true });
    await step("E1", "Dark theme renders the page", async () => {
      await page.evaluate(() => document.documentElement.setAttribute("data-theme", "dark"));
      await page.screenshot({ path: path.join(OUT, `content_${orient}_dark.png`), fullPage: false });
      await page.evaluate(() => document.documentElement.removeAttribute("data-theme"));
    });
    await step("F1", "Existing pages still load (regression): Today, Pipeline, Playbooks, Insights", async () => {
      for (const [h, title] of [["today", "Today"], ["pipeline", "Pipeline"], ["playbooks", "Playbooks"], ["insights", "Insights"]]) {
        await page.evaluate(x => { location.hash = x; }, h);
        await page.locator("#page-title").filter({ hasText: title }).waitFor({ timeout: 6000 });
        await page.waitForTimeout(400);
        if (await page.getByText("Could not load this page").count()) throw new Error(title + " failed to load");
      }
    });
    if (orient === "portrait") {
      await step("G1", "Unauthenticated API call from the browser is 401", async () => {
        const s = await page.evaluate(async () => (await fetch("/api/content/health")).status);
        if (s !== 401) throw new Error("status " + s);
      });
      await step("G2", "Sign out revokes the session: content API is 401 afterwards and the login screen returns", async () => {
        await page.evaluate(() => { location.hash = "today"; });
        await page.locator("#signoutall").evaluate(b => b.click()).catch(() => {});
        await page.locator("#login").waitFor({ state: "visible", timeout: 6000 });
        const s = await page.evaluate(async t => (await fetch("/api/content/health", { headers: { Authorization: "Bearer " + t } })).status, token);
        if (s !== 401) throw new Error("old token still works: " + s);
      });
    }
    await ctx.close();
  }
  await browser.close();
  const failed = results.filter(r => r.status === "failed");
  fs.writeFileSync(path.join(OUT, "results.json"), JSON.stringify({ results, consoleErrors, bad }, null, 2));
  console.log(`\n${results.length - failed.length}/${results.length} passed; console errors: ${consoleErrors.length}; 5xx responses: ${bad.length}`);
  if (consoleErrors.length) console.log(consoleErrors.join("\n"));
  process.exit(failed.length || consoleErrors.length || bad.length ? 1 : 0);
})();
