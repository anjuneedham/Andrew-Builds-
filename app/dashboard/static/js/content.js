// Content platform: foundation page (P0). Shows what the database is enforcing and what does NOT exist yet.
// All DOM is built with createElement/textContent; server data is never parsed as HTML.
(function () {
  const { el, add, text, pill, card } = Z;

  const phaseNote = items => {
    const ul = el("ul", "plain");
    items.forEach(i => ul.append(el("li", null, i)));
    return ul;
  };

  Z.pages.content = {
    title: "Content", sub: "Andrew Builds content platform · foundation", icon: "content",
    async render(root) {
      const [m, h] = await Promise.all([Z.api("/api/content/meta"), Z.api("/api/content/health")]);
      const g = el("div", "grid");

      // 1. Honest status banner
      const hero = card("Foundation only", "The database, rules and security exist. The screens you will work in are built phase by phase.");
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
      const tc = card("Tables", total + " rows in total. Starter rows: 4 series and 1 course plan.");
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
    },
  };
})();
