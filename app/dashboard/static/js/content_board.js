// Content platform: calendar (America/Jamaica), episodes, ideas. Vanilla DOM only; server text is never parsed as HTML.
(function () {
  const { el, add, text, pill, card } = Z;
  const C = Z.content;
  const link = (cls, href) => { const a = el("a", cls); a.href = href; return a; };

  // One episode row. `move` adds an inline reschedule control (used on the calendar).
  function episodeRow(ep, opts) {
    const o = opts || {};
    const row = el("div", "item");
    const head = el("div", "row");
    const open = link("t", "#content/episode-" + ep.id); open.textContent = ep.code + " · " + ep.title;
    add(head, open, C.epPill(ep.status));
    if (ep.overdue) head.append(pill("Overdue", "bad"));
    row.append(head);
    if (o.move) {
      const date = C.input("date", ep.planned_date || "");
      const r = el("div", "row");
      add(r, date, Z.btn(ep.planned_date ? "Reschedule" : "Schedule", "ghost cbtn", async () => {
        if (!date.value) throw new Error("Pick a date first");
        await C.api("/episodes/" + ep.id, "PATCH", { planned_date: date.value });
        await C.done("Saved");
      }));
      row.append(r);
    }
    return row;
  }

  // ---------------- calendar ----------------
  function dayPanel(day) {
    const box = el("div", "stack");
    if (day.episodes.length) day.episodes.forEach(e => box.append(episodeRow(e, { move: true })));
    else box.append(Z.empty("Nothing planned", "Add an episode for this day below."));
    const add_ = el("details", "guide"); add_.open = !day.episodes.length;
    add_.append(el("summary", null, "Add an episode on " + C.dateLabel(day.date)));
    box.append(add_);
    C.episodeForm({ planned_date: day.date }, async ep => { await C.done("Created " + ep.code); }).then(f => add_.append(f));
    return box;
  }

  C.views.calendar = async (root, p) => {
    const cur = await C.api("/calendar/today");
    const mode = p.mode, at = p.at || (mode === "m" ? cur.month : cur.week_start);
    const data = await C.api("/calendar/" + (mode === "m" ? "month/" : "week/") + at);
    const prev = mode === "m" ? C.addMonths(data.month, -1) : C.addDays(data.start, -7);
    const next = mode === "m" ? C.addMonths(data.month, 1) : C.addDays(data.start, 7);
    const go = (m, a) => C.go("calendar-" + m + "-" + a);

    const c = card(mode === "m" ? C.monthLabel(data.month) : "Week of " + C.dateLabel(data.start),
      "Today is " + C.dateLabel(data.today) + " (" + data.timezone.replace("_", " ") + " time).");
    const bar = el("div", "row calbar");
    add(bar,
      Z.btn("Previous", "ghost cbtn", async () => go(mode, prev)),
      Z.btn("Today", "ghost cbtn", async () => go(mode, mode === "m" ? cur.month : cur.week_start)),
      Z.btn("Next", "ghost cbtn", async () => go(mode, next)));
    const toggle = el("div", "chips");
    [["m", "Month"], ["w", "Week"]].forEach(([k, label]) => {
      const b = el("button", null, label); b.type = "button"; b.setAttribute("aria-pressed", String(k === mode));
      b.onclick = () => {
        if (k === mode) return;
        if (k === "m") go("m", C.addDays(data.start, 3).slice(0, 7));
        else go("w", (data.days.find(d => d.is_today && d.in_month) || data.days.find(d => d.in_month)).date);
      };
      toggle.append(b);
    });
    bar.append(toggle);
    c.append(bar);

    if (mode === "m") {
      const grid = el("div", "cal");
      ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].forEach(n => grid.append(el("div", "calh", n)));
      data.days.forEach(d => {
        const b = el("button", "calday" + (d.in_month ? "" : " out") + (d.is_today ? " today" : "")); b.type = "button";
        b.setAttribute("aria-label", C.dateLabel(d.date) + ", " + d.episodes.length + " episode" + (d.episodes.length === 1 ? "" : "s"));
        b.append(el("span", "dn", String(+d.date.slice(8))));
        d.episodes.slice(0, 2).forEach(e => b.append(el("span", "calchip" + (e.overdue ? " late" : ""), e.code)));
        if (d.episodes.length > 2) b.append(el("span", "calmore", "+" + (d.episodes.length - 2) + " more"));
        b.onclick = () => Z.openDrawer(C.dateLabel(d.date), dayPanel(d));
        grid.append(b);
      });
      c.append(grid);
    } else {
      data.days.forEach(d => {
        const sec = el("div", "item");
        const h = el("div", "row"); add(h, el("span", "t", C.dateLabel(d.date)), d.is_today ? pill("Today", "gold") : null);
        sec.append(h);
        d.episodes.forEach(e => sec.append(episodeRow(e)));
        sec.append(Z.btn("Add or reschedule on this day", "ghost cbtn", async () => Z.openDrawer(C.dateLabel(d.date), dayPanel(d))));
        c.append(sec);
      });
    }
    root.append(c);

    const un = card("Not scheduled", data.unscheduled.length ? "Pick a date to put an episode on the calendar." : "Every open episode has a date.");
    const list = el("div", "list");
    data.unscheduled.forEach(e => list.append(episodeRow(e, { move: true })));
    if (data.unscheduled.length) un.append(list);
    root.append(un);
  };

  // ---------------- episodes ----------------
  C.views.episodes = async root => {
    const [eps, series] = await Promise.all([C.api("/episodes"), C.series()]);
    const today = (await C.api("/calendar/today")).today;
    const mk = card("New episode", "An episode starts as an IDEA. It cannot reach READY_TO_RECORD without a READY_TO_RECORD script.");
    const holder = el("details", "guide"); holder.append(el("summary", null, "Create an episode"));
    holder.append(await C.episodeForm({}, async ep => { C.go("episode-" + ep.id); }));
    mk.append(holder);
    root.append(mk);

    const all = card("Episodes", eps.length + " in total. Overdue means planned before today (" + C.dateLabel(today) + ") and not yet published or archived.");
    let filter = "ALL";
    const chips = el("div", "chips"), list = el("div", "list");
    const statuses = ["ALL", ...new Set(eps.map(e => e.status))];
    const paint = () => {
      chips.replaceChildren(); list.replaceChildren();
      statuses.forEach(s => {
        const n = s === "ALL" ? eps.length : eps.filter(e => e.status === s).length;
        const b = el("button", null, (s === "ALL" ? "All" : Z.nice(s)) + " " + n); b.type = "button"; b.setAttribute("aria-pressed", String(s === filter));
        b.onclick = () => { filter = s; paint(); }; chips.append(b);
      });
      const shown = eps.filter(e => filter === "ALL" || e.status === filter);
      if (!shown.length) list.append(Z.empty("No episodes here", "Create one above, or promote an idea."));
      shown.forEach(e => {
        const a = link("item click", "#content/episode-" + e.id);
        const h = el("div", "row"); add(h, el("span", "t", e.code + " · " + e.title), C.epPill(e.status));
        if (e.planned_date && e.planned_date < today && !["PUBLISHED", "ARCHIVED"].includes(e.status)) h.append(pill("Overdue", "bad"));
        a.append(h, el("div", "sub", C.seriesName(series, e.series_id) + " · " + C.dateLabel(e.planned_date) + (e.target_duration_s ? " · target " + C.fmtLen(e.target_duration_s) : "")));
        list.append(a);
      });
    };
    paint(); all.append(chips, list); root.append(all);
  };

  C.views.episode = async (root, id) => {
    const [ep, scripts, series] = await Promise.all([C.api("/episodes/" + id), C.api("/episodes/" + id + "/scripts"), C.series()]);
    const back = link("btn ghost cbtn", "#content/episodes"); back.textContent = "Back to episodes"; root.append(back);

    const head = card(ep.code + " · " + ep.title, C.seriesName(series, ep.series_id));
    const chips = el("div", "row"); chips.append(C.epPill(ep.status));
    if (ep.planned_date) chips.append(pill(C.dateLabel(ep.planned_date), ""));
    head.append(chips);
    const stat = el("div", "stack");
    stat.append(el("div", "label", "Move to"));
    const moves = el("div", "row");
    ep.allowed_next.forEach(to => moves.append(Z.btn(Z.nice(to), to === "ARCHIVED" ? "ghost cbtn" : "gold cbtn", async () => {
      await C.api("/episodes/" + id + "/status", "POST", { to }); await C.done("Now " + Z.nice(to));
    })));
    stat.append(moves);
    if (ep.allowed_next.includes("READY_TO_RECORD")) stat.append(el("div", "sub", "READY_TO_RECORD needs a script in READY_TO_RECORD status. The database refuses it otherwise."));
    head.append(stat);
    root.append(head);

    const ed = card("Details");
    const f = el("form", "sform"); f.noValidate = true; f.onsubmit = e => e.preventDefault();
    const title = C.input("text", ep.title), date = C.input("date", ep.planned_date || ""), len = C.input("text", C.fmtLen(ep.target_duration_s), "e.g. 9:00");
    const path = C.input("text", ep.production_path || "", "production/episode-003");
    title.maxLength = 200;
    add(f, C.field("Title", title, true), C.field("Planned date", date), C.field("Target length (m:ss)", len), C.field("Production folder", path, true));
    f.append(Z.btn("Save details", "gold cbtn", async () => {
      await C.api("/episodes/" + id, "PATCH", { title: title.value.trim(), planned_date: date.value || null, target_duration_s: C.parseLen(len.value), production_path: path.value.trim() || null });
      await C.done("Saved");
    }));
    ed.append(f); root.append(ed);

    const sc = card("Scripts", scripts.length ? scripts.length + " version" + (scripts.length === 1 ? "" : "s") + ". Newest first." : "No script yet.");
    const list = el("div", "list");
    scripts.forEach(s => {
      const a = link("item click", "#content/script-" + s.id);
      const h = el("div", "row"); add(h, el("span", "t", "Version " + s.version), pill(Z.nice(s.status), C.SC_KIND[s.status] || ""), el("span", "sub", s.lines + " line" + (s.lines === 1 ? "" : "s")));
      a.append(h); list.append(a);
    });
    if (scripts.length) sc.append(list);
    const acts = el("div", "row");
    acts.append(Z.btn("New blank script", "gold cbtn", async () => { const s = await C.api("/episodes/" + id + "/scripts", "POST", {}); C.go("script-" + s.id); }));
    if (scripts.length) acts.append(Z.btn("New version from latest", "ghost cbtn", async () => {
      const s = await C.api("/episodes/" + id + "/scripts", "POST", { copy_from: scripts[0].id }); C.go("script-" + s.id);
    }));
    sc.append(acts); root.append(sc);

    if (["IDEA", "ARCHIVED"].includes(ep.status)) {
      const dz = card("Delete", "Only IDEA or ARCHIVED episodes can be deleted. This is recorded in the audit log.");
      dz.append(Z.btn("Delete episode", "red cbtn", async () => C.confirm("Delete " + ep.code + "?", "This cannot be undone. An idea that became this episode goes back to the backlog.", "Delete episode", async () => {
        await C.api("/episodes/" + id, "DELETE"); Z.$("drawer").close(); C.go("episodes"); Z.toast("Deleted", "ok");
      })));
      root.append(dz);
    }
  };

  // ---------------- ideas ----------------
  C.views.ideas = async root => {
    const [ideas, series] = await Promise.all([C.api("/ideas"), C.series()]);
    const opts = [["", "No series yet"], ...series.map(s => [s.id, s.title])];

    const mk = card("New idea", "Capture it now, decide later. Nothing here is published or scheduled until you promote it.");
    const f = el("form", "sform"); f.noValidate = true; f.onsubmit = e => e.preventDefault();
    const title = C.input("text", "", "What is the idea?"), notes = C.textarea("", 3), sel = C.select(opts, "");
    title.maxLength = 200;
    add(f, C.field("Title", title, true), C.field("Notes", notes, true), C.field("Series", sel));
    f.append(Z.btn("Add to backlog", "gold cbtn", async () => {
      const b = { title: title.value.trim(), notes: notes.value }; if (sel.value) b.series_id = +sel.value;
      await C.api("/ideas", "POST", b); await C.done("Added");
    }));
    mk.append(f); root.append(mk);

    const group = (name, sub, rows, render) => {
      const c = card(name, sub);
      if (!rows.length) c.append(Z.empty("Nothing here"));
      else { const l = el("div", "list"); rows.forEach(r => l.append(render(r))); c.append(l); }
      root.append(c);
    };
    const base = i => {
      const it = el("div", "item"), h = el("div", "row");
      add(h, el("span", "t", i.title), pill(C.seriesName(series, i.series_id), ""));
      it.append(h);
      if (i.notes) it.append(el("div", "sub pre", i.notes));
      return it;
    };
    const promoteForm = i => {
      const pf = el("form", "sform"); pf.noValidate = true; pf.onsubmit = e => e.preventDefault();
      const ps = C.select(series.map(s => [s.id, s.title]), i.series_id || series[0].id), code = C.input("text", "", "e.g. EP-004"), date = C.input("date", ""), len = C.input("text", "", "e.g. 9:00");
      code.maxLength = 40;
      add(pf, C.field("Series", ps), C.field("Code (unique in the series)", code), C.field("Planned date", date), C.field("Target length (m:ss)", len));
      pf.append(Z.btn("Create episode from this idea", "gold cbtn", async () => {
        const b = { series_id: +ps.value, code: code.value.trim() }; if (date.value) b.planned_date = date.value;
        const l = C.parseLen(len.value); if (l) b.target_duration_s = l;
        const out = await C.api("/ideas/" + i.id + "/promote", "POST", b);
        Z.$("drawer").close(); C.go("episode-" + out.episode.id); Z.toast("Episode created", "ok");
      }));
      return pf;
    };
    const editForm = i => {
      const ef = el("form", "sform"); ef.noValidate = true; ef.onsubmit = e => e.preventDefault();
      const t = C.input("text", i.title), n = C.textarea(i.notes, 4), s = C.select(opts, i.series_id == null ? "" : i.series_id);
      add(ef, C.field("Title", t, true), C.field("Notes", n, true), C.field("Series", s));
      ef.append(Z.btn("Save", "gold cbtn", async () => {
        await C.api("/ideas/" + i.id, "PATCH", { title: t.value.trim(), notes: n.value, series_id: s.value ? +s.value : null }); await C.done("Saved");
      }));
      return ef;
    };
    const del = i => Z.btn("Delete", "ghost cbtn", async () => C.confirm("Delete this idea?", "“" + i.title + "” will be removed. This is recorded in the audit log.", "Delete idea", async () => {
      await C.api("/ideas/" + i.id, "DELETE"); await C.done("Deleted");
    }));
    const status = (label, to, cls) => i => Z.btn(label, cls || "ghost cbtn", async () => { await C.api("/ideas/" + i.id + "/status", "POST", { to }); await C.done(); });

    group("Backlog", ideas.filter(i => i.status === "BACKLOG").length + " waiting", ideas.filter(i => i.status === "BACKLOG"), i => {
      const it = base(i), r = el("div", "row");
      add(r, Z.btn("Promote to episode", "gold cbtn", async () => Z.openDrawer("Promote: " + i.title, promoteForm(i))),
        Z.btn("Edit", "ghost cbtn", async () => Z.openDrawer("Edit idea", editForm(i))), status("Drop", "DROPPED")(i), del(i));
      it.append(r); return it;
    });
    group("Became episodes", "Manage these from the episode.", ideas.filter(i => i.status === "SCHEDULED"), i => {
      const it = base(i), a = link("btn ghost cbtn", "#content/episode-" + i.episode_id); a.textContent = "Open episode"; it.append(a); return it;
    });
    group("Dropped", "Kept for reference. Restore or delete.", ideas.filter(i => i.status === "DROPPED"), i => {
      const it = base(i), r = el("div", "row"); add(r, status("Restore to backlog", "BACKLOG")(i), del(i)); it.append(r); return it;
    });
  };
})();
