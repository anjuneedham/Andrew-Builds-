// Content platform. content.js = shell, tabs, shared helpers and the Foundation view.
// content_board.js = calendar, episodes, ideas. content_script.js = script editor.
// All DOM is built with createElement/textContent; server data is never parsed as HTML.
(function () {
  const { el, add, text, pill, card } = Z;
  const C = (Z.content = { views: {} });

  const phaseNote = items => {
    const ul = el("ul", "plain");
    items.forEach(i => ul.append(el("li", null, i)));
    return ul;
  };

  // ---- shared helpers ----
  C.EP_KIND = { SCRIPTING: "royal", READY_TO_RECORD: "gold", RECORDED: "gold", EDITING: "warn", QA: "warn", READY_TO_PUBLISH: "ok", PUBLISHED: "ok" };
  C.epPill = s => pill(Z.nice(s), C.EP_KIND[s] || "");
  C.SC_KIND = { DRAFT: "", IN_REVIEW: "warn", READY_TO_RECORD: "ok", LOCKED: "royal" };
  C.api = (path, method, body) => Z.api("/api/content" + path, method, body);
  C.go = arg => { location.hash = "content" + (arg ? "/" + arg : ""); };
  C.field = (label, input, wide) => { const l = el("label", "f" + (wide ? " wide" : "")); l.append(el("span", null, label), input); return l; };
  C.input = (type, value, ph) => { const i = el("input"); i.type = type; if (value != null) i.value = value; if (ph) i.placeholder = ph; return i; };
  C.textarea = (value, rows) => { const t = el("textarea"); t.rows = rows || 3; t.value = value || ""; return t; };
  C.select = (opts, value) => {
    const s = el("select");
    opts.forEach(([v, l]) => { const o = el("option", null, l); o.value = v; s.append(o); });
    if (value != null) s.value = String(value);
    return s;
  };
  // handler for change events (not buttons): toast errors instead of leaving an unhandled rejection
  C.act = fn => async () => { try { await fn(); } catch (e) { if (e.message !== "Signed out") Z.toast(e.message, "bad"); } };
  C.done = (msg) => { if (msg) Z.toast(msg, "ok"); const d = Z.$("drawer"); if (d.open) d.close(); return Z.rerender(); };
  C.confirm = (title, message, label, fn) => {
    const box = el("div", "stack");
    add(box, el("p", null, message), add(el("div", "row"),
      Z.btn(label, "red cbtn", async () => { await fn(); }), Z.btn("Cancel", "ghost cbtn", async () => { Z.$("drawer").close(); })));
    Z.openDrawer(title, box);
  };
  let seriesCache = null;
  C.series = async () => seriesCache || (seriesCache = await C.api("/series"));
  C.seriesName = (list, id) => { const s = list.find(x => x.id === id); return s ? s.title : "No series"; };

  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const parts = iso => iso.split("-").map(Number);
  C.dateLabel = iso => { if (!iso) return "No date"; const [y, m, d] = parts(iso); return DOW[new Date(Date.UTC(y, m - 1, d)).getUTCDay()] + " " + d + " " + MON[m - 1] + " " + y; };
  C.monthLabel = ym => { const [y, m] = parts(ym); return ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][m - 1] + " " + y; };
  C.addDays = (iso, n) => { const [y, m, d] = parts(iso); return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10); };
  C.addMonths = (ym, n) => { const [y, m] = parts(ym); const t = y * 12 + (m - 1) + n; return Math.floor(t / 12) + "-" + String((t % 12) + 1).padStart(2, "0"); };
  C.fmtLen = s => (s == null ? "" : Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"));
  // "9:30" -> 570, "9" -> 540 (minutes), "" -> null
  C.parseLen = v => {
    v = v.trim(); if (!v) return null;
    let m = /^(\d{1,4}):([0-5]\d)$/.exec(v); if (m) return +m[1] * 60 + +m[2];
    m = /^(\d{1,4})$/.exec(v); if (m) return +m[1] * 60;
    throw new Error("Length must look like 9:30 (minutes:seconds) or just minutes");
  };

  // New-episode form. prefill = {planned_date, series_id, code, title}. onDone runs after a successful save.
  C.episodeForm = async (prefill, onDone) => {
    const series = await C.series(), p = prefill || {};
    const f = el("form", "sform"); f.noValidate = true;
    const sel = C.select(series.map(s => [s.id, s.title]), p.series_id || series[0].id);
    const code = C.input("text", p.code || "", "e.g. EP-003"), title = C.input("text", p.title || "", "Working title");
    const date = C.input("date", p.planned_date || ""), len = C.input("text", "", "e.g. 9:00");
    code.maxLength = 40; title.maxLength = 200;
    add(f, C.field("Series", sel), C.field("Code (unique in the series)", code), C.field("Title", title, true), C.field("Planned date", date), C.field("Target length (m:ss)", len));
    const go = Z.btn("Create episode", "gold cbtn", async () => {
      const body = { series_id: +sel.value, code: code.value.trim(), title: title.value.trim() };
      if (date.value) body.planned_date = date.value;
      const l = C.parseLen(len.value); if (l) body.target_duration_s = l;
      const ep = await C.api("/episodes", "POST", body);
      await onDone(ep);
    });
    f.append(go); f.onsubmit = e => e.preventDefault();
    return f;
  };

  const TABS = [["calendar", "Calendar"], ["episodes", "Episodes"], ["ideas", "Ideas"], ["foundation", "Foundation"]];
  const parse = arg => {
    const a = arg || "calendar"; let m;
    if ((m = /^calendar(?:-([mw])-([\d-]{7,10}))?$/.exec(a))) return ["calendar", { mode: m[1] || "m", at: m[2] }, "calendar"];
    if ((m = /^episode-(\d{1,18})$/.exec(a))) return ["episode", +m[1], "episodes"];
    if ((m = /^script-(\d{1,18})$/.exec(a))) return ["script", +m[1], "episodes"];
    if (a === "episodes" || a === "ideas" || a === "foundation") return [a, null, a];
    return ["calendar", { mode: "m" }, "calendar"];
  };

  Z.pages.content = {
    title: "Content", sub: "Andrew Builds content platform", icon: "content",
    async render(root, arg) {
      const [view, param, tab] = parse(arg);
      const bar = el("div", "tabs"); bar.setAttribute("role", "tablist");
      TABS.forEach(([k, label]) => {
        const b = el("button", null, label); b.type = "button"; b.setAttribute("role", "tab"); b.setAttribute("aria-selected", String(k === tab));
        b.onclick = () => C.go(k); bar.append(b);
      });
      const body = el("div", "stack");
      root.append(bar, body);
      await C.views[view](body, param);
    },
  };

  C.views.foundation = async root => {
    const [m, h] = await Promise.all([Z.api("/api/content/meta"), Z.api("/api/content/health")]);
    const g = el("div", "grid");

    // 1. Honest status banner
    const hero = card("Foundation status", "Database, rules and security are in place. Calendar, episodes, ideas and the script editor work; everything under \"Not built yet\" does not.");
    hero.classList.add("s12", "hero");
    const chips = el("div", "row");
    add(chips,
      pill(h.content_migrated ? "Database ready" : "Not migrated", h.content_migrated ? "ok" : "bad"),
      pill(h.rls_ok ? "Row-level security on" : "RLS problem", h.rls_ok ? "ok" : "bad"),
      pill("Queries run as " + h.queried_as, h.queried_as === h.role ? "ok" : "warn"),
      pill("Nothing is published or sent from here", "gold"));
    hero.append(chips);
    g.append(hero);

    // 2. Table counts (real rows, read as content_app)
    const total = h.tables.reduce((n, t) => n + t.rows, 0);
    const tc = card("Tables", total + " rows in total across the content tables (read as the content_app role).");
    tc.classList.add("s12");
    const tiles = el("div", "tiles");
    h.tables.forEach(t => {
      const tile = el("div", "tile");
      add(tile, el("div", "label", t.name), el("div", "stat", t.rows));
      tile.append(pill(t.rls_enabled && t.rls_forced ? "RLS forced" : "RLS missing", t.rls_enabled && t.rls_forced ? "ok" : "bad"));
      tiles.append(tile);
    });
    tc.append(tiles);
    g.append(tc);

    // 3. Rules the database enforces
    const rc = card("Rules the database enforces", "These hold even if the app has a bug. Each one gets its screen in the phase shown.");
    rc.classList.add("s6");
    const list = el("div", "list");
    m.rules.forEach(r => {
      const it = el("div", "item");
      add(it, add(el("div", "row"), el("span", "t", r.title), pill(r.phase, r.phase === "P0" ? "ok" : "")), el("div", "sub", r.detail), el("div", "label", r.where));
      list.append(it);
    });
    rc.append(list);
    g.append(rc);

    // 4. What is NOT built (never present planned work as done)
    const nb = card("Not built yet", "Planned, not working. Do not rely on any of this.");
    nb.classList.add("s6");
    const nl = el("div", "list");
    m.not_built.forEach(n => {
      const it = el("div", "item");
      add(it, add(el("div", "row"), pill(n.phase, "warn"), el("span", null, n.what)));
      nl.append(it);
    });
    nb.append(nl);
    const kinds = el("div", "item");
    add(kinds, el("div", "label", "How script lines will be marked"),
      el("div", "sub", "Factual lines need a CONFIRMED claim. These are never treated as facts: " + m.non_factual_kinds.join(", ").toLowerCase() + "."));
    nb.append(kinds);
    g.append(nb);

    const foot = card("Migrations applied");
    foot.classList.add("s12");
    foot.append(phaseNote(h.migrations));
    foot.append(Z.btn("Refresh", "ghost cbtn", async () => { await Z.rerender(); }));
    g.append(foot);
    root.append(g);
  };
})();
