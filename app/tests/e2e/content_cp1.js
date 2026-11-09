// Tablet browser check for CP1: calendar, episodes, ideas, script editor. Runs against a LOCAL server with a THROWAWAY database.
// Usage: BASE=http://127.0.0.1:8099 PASSWORD=... TOTP_SECRET=<base32> OUT=<dir> node tests/e2e/content_cp1.js
// Signs in through the real login form, then drives the UI by touch/click at 1280x800 and 800x1280.
const { chromium } = require("playwright");
const crypto = require("crypto"), fs = require("fs"), path = require("path");
const BASE = process.env.BASE || "http://127.0.0.1:8099", PASSWORD = process.env.PASSWORD, SECRET = process.env.TOTP_SECRET, OUT = process.env.OUT || "/tmp/e2e-cp1";
fs.mkdirSync(OUT, { recursive: true });
const results = [];

function b32(s) { const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"; let bits = ""; for (const c of s.replace(/=+$/, "")) bits += A.indexOf(c).toString(2).padStart(5, "0"); const out = []; for (let i = 0; i + 8 <= bits.length; i += 8) out.push(parseInt(bits.slice(i, i + 8), 2)); return Buffer.from(out); }
function totp(step) { const b = Buffer.alloc(8); b.writeBigUInt64BE(BigInt(step)); const h = crypto.createHmac("sha1", b32(SECRET)).update(b).digest(); const o = h[h.length - 1] & 15; return String((h.readUInt32BE(o) & 0x7fffffff) % 1e6).padStart(6, "0"); }

(async () => {
  const browser = await chromium.launch();
  const VIEWPORTS = [["landscape", { width: 1280, height: 800 }], ["portrait", { width: 800, height: 1280 }]];
  let token = null, ids = {};
  const consoleErrors = [], bad = [];

  for (const [orient, vp] of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: vp, hasTouch: true, isMobile: false, deviceScaleFactor: 1 });
    if (token) await ctx.addInitScript(t => { try { localStorage.setItem("od_token", t); } catch (e) {} }, token);
    const page = await ctx.newPage();
    // 401 (G-checks) and 409 (the claim gate refusing a FACT line on purpose, step D2) are expected resource errors; anything else is real.
    page.on("console", m => { if (m.type() === "error" && !/status of (401|409)/.test(m.text())) consoleErrors.push(`[${orient}] ${m.text()}`); });
    page.on("pageerror", e => consoleErrors.push(`[${orient}] pageerror: ${e.message}`));
    page.on("response", r => { if (r.status() >= 500) bad.push(`[${orient}] ${r.status()} ${r.url()}`); });
    const step = async (id, name, fn) => {
      try { await fn(); results.push({ orient, id, name, status: "passed" }); console.log("PASS", orient, id, name); }
      catch (e) { results.push({ orient, id, name, status: "failed", error: String(e.message).split("\n")[0] }); console.log("FAIL", orient, id, name, "-", String(e.message).split("\n")[0]); await page.screenshot({ path: path.join(OUT, `FAIL_${orient}_${id}.png`) }).catch(() => {}); }
    };
    const api = (p, method, body) => page.evaluate(async ([p, method, body]) => {
      const r = await fetch("/api/content" + p, { method: method || "GET", headers: { Authorization: "Bearer " + localStorage.getItem("od_token"), "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
      return { status: r.status, data: await r.json() };
    }, [p, method, body]);
    const hash = async (h, raw) => { await page.evaluate(x => { location.hash = x; }, (raw ? "" : "content/") + h); await page.waitForTimeout(500); };
    const noOverflow = async () => { const o = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth })); if (o.sw > o.cw + 1) throw new Error(`horizontal scroll ${o.sw} > ${o.cw}`); };
    const bigEnough = async () => {
      const small = await page.evaluate(() => [...document.querySelectorAll("#view button, #view a.btn, #view input:not([type=checkbox]), #view select, #view textarea, #drawer button, #drawer input, #drawer select, #drawer textarea")]
        .filter(e => e.offsetParent && !e.disabled || (e.offsetParent && e.disabled)).map(e => { const r = e.getBoundingClientRect(); return { t: (e.textContent || e.getAttribute("aria-label") || e.tagName).trim().slice(0, 24), w: Math.round(r.width), h: Math.round(r.height) }; })
        .filter(b => b.h < 48 || b.w < 48));
      if (small.length) throw new Error("controls under 48px: " + JSON.stringify(small.slice(0, 6)));
    };
    await page.goto(BASE + "/");

    if (!token) {
      await step("A1", "Real sign-in with password + authenticator code", async () => {
        await page.locator("#login").waitFor({ state: "visible", timeout: 8000 });
        await page.fill("#l_pw", PASSWORD); await page.fill("#l_code", totp(Math.floor(Date.now() / 30000))); await page.click("#l_go");
        await page.locator("#shell").waitFor({ state: "visible", timeout: 8000 });
        token = await page.evaluate(() => localStorage.getItem("od_token")); if (!token) throw new Error("no token");
      });
    }
    await page.locator("#shell").waitFor({ state: "visible", timeout: 8000 });
    const nav = orient === "landscape" ? "#nav-side" : "#nav-tabs";
    const today = (await api("/calendar/today")).data;

    await step("B1", "Content opens on the Calendar tab, shows the month and today in Jamaica time", async () => {
      await page.locator(`${nav} a[data-page=content]`).click();
      await page.locator(".tabs button[aria-selected=true]").filter({ hasText: "Calendar" }).waitFor({ timeout: 6000 });
      await page.getByText("America/Jamaica".replace("_", " ") + " time").first().waitFor({ timeout: 4000 });
      await page.locator(".calday.today").first().waitFor({ timeout: 4000 });
      const n = await page.locator(".calday").count(); if (![28, 35, 42].includes(n)) throw new Error("grid cells " + n);
    });
    await step("B2", "No horizontal scroll and every control is at least 48px (calendar)", async () => { await noOverflow(); await bigEnough();
      const h = await page.locator(".calday").first().evaluate(e => e.getBoundingClientRect().height); if (h < 48) throw new Error("day cell " + h); });

    if (orient === "landscape") {
      await step("C1", "Create an idea in the UI; it appears in the backlog", async () => {
        await page.locator(".tabs button", { hasText: "Ideas" }).click();
        await page.getByPlaceholder("What is the idea?").fill("SAMPLE idea from e2e");
        await page.locator("textarea").first().fill("SAMPLE notes\nsecond line");
        await page.getByRole("button", { name: "Add to backlog" }).click();
        await page.locator(".item .t", { hasText: "SAMPLE idea from e2e" }).waitFor({ timeout: 5000 });
      });
      await step("C2", "Promote the idea: opens the new episode, idea moves to 'Became episodes'", async () => {
        await page.getByRole("button", { name: "Promote to episode" }).first().click();
        const d = page.locator("#drawer"); await d.waitFor({ state: "visible" });
        await bigEnough();
        await d.getByPlaceholder("e.g. EP-004").fill("E2E-1");
        await d.locator('input[type=date]').fill(today.today);
        await d.getByRole("button", { name: "Create episode from this idea" }).click();
        await page.locator(".card h2", { hasText: "E2E-1" }).waitFor({ timeout: 6000 });
        ids.ep = Number((page.url().match(/episode-(\d+)/) || [])[1]); if (!ids.ep) throw new Error("no episode id in " + page.url());
        await hash("ideas"); await page.getByText("Became episodes").waitFor(); await page.getByRole("link", { name: "Open episode" }).waitFor();
      });
      await step("C3", "The episode shows on today's cell of the calendar; tapping the day opens the day panel", async () => {
        await hash("calendar");
        const cell = page.locator(".calday.today"); await cell.locator(".calchip", { hasText: "E2E-1" }).waitFor({ timeout: 5000 });
        await cell.tap(); await page.locator("#drawer").waitFor({ state: "visible" });
        await page.locator("#drawer .item .t", { hasText: "E2E-1" }).waitFor({ timeout: 3000 });
        await bigEnough();
      });
      await step("C4", "Reschedule from the day panel moves it to another day", async () => {
        const target = await page.evaluate(t => { const [y, m, d] = t.split("-").map(Number); const x = new Date(Date.UTC(y, m - 1, d + 2)); return x.toISOString().slice(0, 10); }, today.today);
        await page.locator("#drawer .item input[type=date]").first().fill(target);
        await page.locator("#drawer").getByRole("button", { name: "Reschedule" }).click();
        await page.waitForTimeout(700);
        const e = (await api("/episodes/" + ids.ep)).data; if (e.planned_date !== target) throw new Error("planned_date " + e.planned_date);
      });
      await step("C5", "Week view lists seven days; Next/Previous/Today navigate", async () => {
        await hash("calendar"); await page.getByRole("button", { name: "Week", exact: true }).click(); await page.waitForTimeout(500);
        const days = await page.locator(".card .item .t", { hasText: /^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) \d/ }).count(); if (days !== 7) throw new Error("day sections " + days);
        const before = await page.locator(".card h2").first().innerText();
        await page.getByRole("button", { name: "Next" }).click(); await page.waitForTimeout(600);
        const after = await page.locator(".card h2").first().innerText(); if (after === before) throw new Error("Next did not change the week");
        await page.getByRole("button", { name: "Today" }).click(); await page.waitForTimeout(600);
        if ((await page.locator(".card h2").first().innerText()) !== before) throw new Error("Today did not return");
        await page.getByRole("button", { name: "Month", exact: true }).click(); await page.waitForTimeout(500);
        await page.locator(".cal").waitFor();
      });
      await step("D1", "Script editor: new script, add lines, retag, reorder", async () => {
        await hash("episode-" + ids.ep);
        await page.getByRole("button", { name: "New blank script" }).click();
        await page.locator(".card h2", { hasText: "script v1" }).waitFor({ timeout: 6000 });
        ids.script = Number((page.url().match(/script-(\d+)/) || [])[1]);
        let n = 0;
        for (const [t, k] of [["SAMPLE factual line", "FACT"], ["SAMPLE my opinion", "OPINION"], ["SAMPLE a question?", "QUESTION"]]) {
          await page.locator(".addline textarea").fill(t); await page.locator(".addline select").selectOption(k);
          await page.getByRole("button", { name: "Add line" }).click(); n++;
          await page.waitForFunction(c => document.querySelectorAll(".line").length === c, n, { timeout: 5000 });
        }
        await page.locator(".line").nth(2).getByRole("button", { name: "Up" }).click(); await page.waitForTimeout(600);
        const order = await page.locator(".line textarea").evaluateAll(a => a.map(x => x.value));
        if (order[1] !== "SAMPLE a question?") throw new Error("order " + order);
        await bigEnough();
      });
      await step("D2", "A FACT line blocks READY_TO_RECORD with a clear message; re-tagging it lets the script through", async () => {
        await page.getByRole("button", { name: "Move to In review" }).click(); await page.waitForTimeout(600);
        await page.getByRole("button", { name: "Move to Ready to record" }).click();
        await page.locator(".toast.bad", { hasText: "claim check" }).waitFor({ timeout: 5000 });
        await page.locator(".line").first().locator("select").selectOption("OPINION"); await page.waitForTimeout(700);
        await page.getByRole("button", { name: "Move to Ready to record" }).click(); await page.waitForTimeout(800);
        await page.locator(".banner", { hasText: "frozen" }).waitFor({ timeout: 5000 });
        if (await page.getByRole("button", { name: "Add line" }).count()) throw new Error("editor still editable while frozen");
      });
      await step("D3", "Episode can now move to Ready to record (database gate satisfied)", async () => {
        await hash("episode-" + ids.ep);
        await page.getByRole("button", { name: "Scripting" }).click(); await page.waitForTimeout(700);
        await page.getByRole("button", { name: "Ready to record" }).click(); await page.waitForTimeout(700);
        await page.locator(".pill", { hasText: "Ready to record" }).first().waitFor({ timeout: 4000 });
      });
    }

    await step("E1", "Every content page renders without errors, overflow or small controls", async () => {
      for (const h of ["calendar", "calendar-w-" + today.week_start, "episodes", "ideas", "foundation", ...(ids.ep ? ["episode-" + ids.ep, "script-" + ids.script] : [])]) {
        await hash(h);
        if (await page.getByText("Could not load this page").count()) throw new Error(h + " failed to load");
        await noOverflow(); await bigEnough();
        await page.screenshot({ path: path.join(OUT, `cp1_${orient}_${h.split("-")[0]}.png`), fullPage: true });
      }
    });
    await step("E2", "Foundation tab still shows the live database status", async () => {
      await hash("foundation"); await page.getByText("Foundation status").first().waitFor({ timeout: 5000 }); await page.getByText("Row-level security on").first().waitFor({ timeout: 4000 });
    });
    await step("E3", "Dark theme renders the calendar", async () => {
      await hash("calendar"); await page.evaluate(() => document.documentElement.setAttribute("data-theme", "dark"));
      await page.screenshot({ path: path.join(OUT, `cp1_${orient}_calendar_dark.png`) }); await page.evaluate(() => document.documentElement.removeAttribute("data-theme"));
    });
    await step("F1", "Existing Outreach Desk pages still load", async () => {
      for (const [h, title] of [["today", "Today"], ["pipeline", "Pipeline"], ["playbooks", "Playbooks"], ["insights", "Insights"]]) {
        await hash(h, true); await page.locator("#page-title").filter({ hasText: title }).waitFor({ timeout: 6000 });
        if (await page.getByText("Could not load this page").count()) throw new Error(title + " failed to load");
      }
    });
    await ctx.close();
  }
  await browser.close();
  const failed = results.filter(r => r.status === "failed");
  fs.writeFileSync(path.join(OUT, "results.json"), JSON.stringify({ results, consoleErrors, bad }, null, 2));
  console.log(`\n${results.length - failed.length}/${results.length} passed; console errors: ${consoleErrors.length}; 5xx responses: ${bad.length}`);
  if (consoleErrors.length) console.log(consoleErrors.join("\n"));
  process.exit(failed.length || consoleErrors.length || bad.length ? 1 : 0);
})();
