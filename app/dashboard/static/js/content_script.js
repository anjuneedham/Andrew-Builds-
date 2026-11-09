// Content platform: script editor (P2a). One sentence per line, each tagged with a kind. Vanilla DOM only.
// Claims arrive in the next checkpoint (P2b): until then a FACT line cannot let a script become READY_TO_RECORD.
(function () {
  const { el, add, text, pill, card } = Z;
  const C = Z.content;

  const KIND_HELP = {
    FACT: "A statement of fact. Needs a CONFIRMED claim before the script can be READY_TO_RECORD.",
    OPINION: "Your view. Never treated as a fact.", REFLECTION: "Looking back. Never treated as a fact.",
    QUESTION: "A question to the viewer.", HYPOTHESIS: "A guess or a test. Never treated as a fact.",
    DIRECTION: "A note for you while recording (not spoken).", CTA: "A call to action.", DISCLAIMER: "Required wording, e.g. not financial advice.",
  };

  C.views.script = async (root, id) => {
    const [s, meta] = await Promise.all([C.api("/scripts/" + id), Z.api("/api/content/meta")]);
    const kinds = meta.enums["script_lines.kind"];
    const ep = await C.api("/episodes/" + s.episode_id);
    const kindOpts = kinds.map(k => [k, k === "FACT" ? "FACT (needs a claim)" : Z.nice(k)]);

    const back = Z.el("a", "btn ghost cbtn"); back.href = "#content/episode-" + ep.id; back.textContent = "Back to " + ep.code; root.append(back);

    const head = card(ep.code + " · " + ep.title + " · script v" + s.version);
    const chips = el("div", "row"); chips.append(pill(Z.nice(s.status), C.SC_KIND[s.status] || ""));
    Object.entries(s.counts).forEach(([k, n]) => chips.append(pill(n + " " + k.toLowerCase(), k === "FACT" ? "warn" : "")));
    head.append(chips);
    const mv = el("div", "row");
    s.allowed_next.forEach(to => mv.append(Z.btn("Move to " + Z.nice(to), to === "DRAFT" ? "ghost cbtn" : "gold cbtn", async () => {
      await C.api("/scripts/" + id + "/status", "POST", { to }); await C.done("Now " + Z.nice(to));
    })));
    if (mv.childNodes.length) head.append(el("div", "label", "Next step"), mv);
    else head.append(el("div", "sub", "LOCKED is final. Start a new version from the episode page to change anything."));
    if (!s.editable) head.append(el("div", "banner", s.status === "LOCKED" ? "This script is locked and cannot change."
      : "This script is frozen. Move it back to DRAFT to edit lines, kinds or notes."));
    else head.append(el("div", "sub", "Claims and the claim checker arrive in the next checkpoint. Until then a FACT line blocks READY_TO_RECORD; tag opinions, questions and directions as such."));
    root.append(head);

    // --- lines ---
    const lines = card("Lines", s.lines.length ? "One sentence per line. Tag each with what it is." : "No lines yet. Add the first one below.");
    const list = el("div", "list");
    s.lines.forEach(l => {
      const row = el("div", "item line" + (l.kind === "FACT" ? " fact" : ""));
      const top = el("div", "row");
      add(top, el("span", "pos", String(l.position)), pill(l.kind, l.kind === "FACT" ? "warn" : ""));
      l.claims.forEach(c => top.append(pill(c.code + " " + Z.nice(c.status), c.status === "CONFIRMED" ? "ok" : "bad")));
      row.append(top);
      const t = C.textarea(l.text, 2); t.maxLength = 2000; t.disabled = !s.editable; t.setAttribute("aria-label", "Line " + l.position + " text");
      row.append(t);
      if (s.editable) {
        const kind = C.select(kindOpts, l.kind); kind.setAttribute("aria-label", "Line " + l.position + " kind");
        kind.onchange = C.act(async () => { await C.api("/lines/" + l.id, "PATCH", { kind: kind.value }); await Z.rerender(); });
        const save = Z.btn("Save text", "gold cbtn", async () => { await C.api("/lines/" + l.id, "PATCH", { text: t.value }); await C.done("Saved"); });
        save.disabled = true; t.oninput = () => { save.disabled = t.value.trim() === l.text; };
        const ctl = el("div", "row");
        add(ctl, kind, save,
          Z.btn("Up", "ghost cbtn", async () => { await C.api("/lines/" + l.id + "/move", "POST", { to: l.position - 1 }); await Z.rerender(); }),
          Z.btn("Down", "ghost cbtn", async () => { await C.api("/lines/" + l.id + "/move", "POST", { to: l.position + 1 }); await Z.rerender(); }),
          Z.btn("Delete", "ghost cbtn", async () => { await C.api("/lines/" + l.id, "DELETE"); await Z.rerender(); }));
        ctl.querySelectorAll("button").forEach(b => { if (b.textContent === "Up") b.disabled = l.position === 1; if (b.textContent === "Down") b.disabled = l.position === s.lines.length; });
        row.append(ctl, el("div", "sub", KIND_HELP[l.kind]));
      }
      list.append(row);
    });
    if (s.lines.length) lines.append(list);

    if (s.editable) {
      const f = el("form", "sform addline"); f.noValidate = true; f.onsubmit = e => e.preventDefault();
      const t = C.textarea("", 2), k = C.select(kindOpts, "FACT"); t.maxLength = 2000;
      const help = el("div", "sub", KIND_HELP.FACT); k.onchange = () => text(help, KIND_HELP[k.value]);
      add(f, C.field("New line", t, true), C.field("Kind", k), help);
      f.append(Z.btn("Add line", "gold cbtn", async () => {
        await C.api("/scripts/" + id + "/lines", "POST", { text: t.value.trim(), kind: k.value }); await Z.rerender();
      }));
      lines.append(f);
    }
    root.append(lines);

    // --- notes ---
    const nb = card("Notes", "Free text for this version (not spoken). Frozen with the script.");
    const body = C.textarea(s.body, 5); body.maxLength = 20000; body.disabled = !s.editable;
    nb.append(body);
    if (s.editable) nb.append(Z.btn("Save notes", "gold cbtn", async () => { await C.api("/scripts/" + id, "PATCH", { body: body.value }); await C.done("Saved"); }));
    root.append(nb);

    if (s.editable) {
      const dz = card("Delete this script", "Only DRAFT or IN_REVIEW scripts. The lines go with it. Recorded in the audit log.");
      dz.append(Z.btn("Delete script", "red cbtn", async () => C.confirm("Delete script v" + s.version + "?", "Its " + s.lines.length + " line(s) will be removed.", "Delete script", async () => {
        await C.api("/scripts/" + id, "DELETE"); Z.$("drawer").close(); C.go("episode-" + ep.id); Z.toast("Deleted", "ok");
      })));
      root.append(dz);
    }
  };
})();
