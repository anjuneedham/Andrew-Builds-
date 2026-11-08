(function () {
  const { $, el, add, text, icon } = Z;
  const NAV = [["today", "Today"], ["pipeline", "Pipeline"], ["playbooks", "Playbooks"], ["insights", "Insights"], ["content", "Content"]];
  const AUTH = ["msgbox", "setup1", "setup2", "setup3", "login"];
  let timer = null, seq = 0, current = "today";

  const KO = ["Opening your desk", "Checking follow-ups", "Reading the pipeline"];
  let ki = 0; const kt = setInterval(() => { ki = (ki + 1) % KO.length; text($("ko-msg"), KO[ki]); }, 700); const t0 = Date.now();
  function kickoffDone() { setTimeout(() => { clearInterval(kt); $("kickoff").classList.add("out"); setTimeout(() => { $("kickoff").hidden = true; }, 500); }, Math.max(0, 900 - (Date.now() - t0))); }
  Z.goal = msg => {
    text($("ko-msg"), "Goal! " + msg); $("kickoff").hidden = false; $("kickoff").classList.remove("out");
    setTimeout(() => { $("kickoff").classList.add("out"); setTimeout(() => { $("kickoff").hidden = true; }, 500); }, 1700);
  };

  // theme (per device)
  const applyTheme = t => { if (t) document.documentElement.setAttribute("data-theme", t); else document.documentElement.removeAttribute("data-theme"); };
  applyTheme(Z.store.get("od_theme"));
  $("theme").onclick = () => {
    const dark = document.documentElement.getAttribute("data-theme") === "dark" || (!document.documentElement.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    const next = dark ? "light" : "dark"; Z.store.set("od_theme", next); applyTheme(next);
  };

  // navigation
  function buildNav() {
    ["nav-side", "nav-tabs"].forEach(id => {
      const box = $(id); box.replaceChildren();
      NAV.forEach(([k, label]) => { const a = el("a"); a.href = "#" + k; a.dataset.page = k; add(a, icon(Z.pages[k].icon), el("span", null, label)); if (id === "nav-side" && k === "operator") { const bd = el("span", "badge"); bd.hidden = true; a.append(bd); } box.append(a); });
    });
  }
  function markNav() {
    document.querySelectorAll("[data-page]").forEach(a => { if (a.dataset.page === current) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
  }
  Z.paintStatus = () => {};
  async function render() {
    const my = ++seq; const [route, arg] = location.hash.slice(1).split("/"); const name = Z.pages[route] ? route : NAV[0][0]; const page = Z.pages[name]; current = page.navKey || name; markNav(); text($("page-title"), page.title); text($("page-sub"), page.sub); document.title = page.title + " · Outreach Desk";
    const view = $("view"); const y = scrollY; const box = el("div"); const first = !view.firstChild || view.dataset.page !== name + "/" + (arg || "");
    if (first) view.replaceChildren(Z.skeleton(4));
    try { await page.render(box, arg ? decodeURIComponent(arg) : undefined); } catch (e) {
      if (my !== seq || e.message === "Signed out") return;
      const c = Z.card("Could not load this page", e.message); c.append(Z.btn("Try again", "gold", () => render())); box.replaceChildren(c);
    }
    if (my !== seq) return; view.replaceChildren(...box.childNodes);
    view.dataset.page = name + "/" + (arg || ""); if (!first) scrollTo(0, y);
  }
  Z.rerender = render;
  window.addEventListener("hashchange", () => { render(); scrollTo(0, 0); $("view").focus({ preventScroll: true }); });

  // auth
  function showAuth(id) { $("shell").hidden = true; $("auth").hidden = false; AUTH.forEach(a => { $(a).hidden = a !== id; }); document.querySelectorAll("[data-err]").forEach(e => { e.textContent = ""; }); }
  function showShell() { $("auth").hidden = true; $("shell").hidden = false; }
  Z.onSignedOut = m => { Z.store.del("od_token"); clearInterval(timer); showAuth("login"); document.querySelector("#login [data-err]").textContent = m || ""; };
  const authAct = (btn, section, fn) => { btn.onclick = Z.busy(btn, async () => { try { await fn(); } catch (e) { section.querySelector("[data-err]").textContent = e.message; throw e; } }); };
  authAct($("s_begin"), $("setup1"), async () => { const d = await Z.api("/api/auth/setup/begin", "POST", { setup_token: $("s_token").value, password: $("s_pw").value }, false); text($("s_secret"), d.secret); $("s_pw").value = ""; showAuth("setup2"); });
  authAct($("s_confirm"), $("setup2"), async () => {
    const d = await Z.api("/api/auth/setup/confirm", "POST", { setup_token: $("s_token").value, code: $("s_code").value.trim() }, false);
    $("s_codes").replaceChildren(); d.recovery_codes.forEach(c => $("s_codes").append(el("code", "key", c))); $("s_token").value = ""; showAuth("setup3");
  });
  $("s_done").onclick = () => { $("s_codes").replaceChildren(); text($("s_secret"), ""); showAuth("login"); };
  authAct($("l_go"), $("login"), async () => {
    const d = await Z.api("/api/auth/login", "POST", { password: $("l_pw").value, code: $("l_code").value.trim() }, false);
    $("l_pw").value = ""; $("l_code").value = ""; Z.setToken(d.token); await start();
  });
  $("signout").onclick = Z.busy($("signout"), async () => { await Z.api("/api/auth/logout", "POST"); Z.onSignedOut(""); });
  $("signoutall").onclick = Z.busy($("signoutall"), async () => { await Z.api("/api/auth/logout-all", "POST"); Z.onSignedOut(""); });
  $("drawer-close").onclick = () => $("drawer").close();
  $("drawer").addEventListener("click", e => { if (e.target === $("drawer")) $("drawer").close(); });

  window.addEventListener("beforeinstallprompt", e => { e.preventDefault(); Z.installEvent = e; $("install").hidden = false; });
  $("install").onclick = async () => { if (Z.installEvent) { Z.installEvent.prompt(); await Z.installEvent.userChoice; $("install").hidden = true; } };

  async function start() {
    showShell(); buildNav(); await render();
  }

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
  (async () => {
    try {
      const st = await Z.api("/api/auth/state", "GET", null, false);
      Z.state.mode = st.mode; const chip = $("modechip"); text(chip, st.mode === "LIVE" ? "LIVE" : "LOCAL"); chip.className = "modechip" + (st.mode === "LIVE" ? " live" : "");
      if (!st.setup_complete) {
        if (!st.setup_enabled) { showAuth("msgbox"); text($("msg"), "Setup is not enabled. Set OWNER_SETUP_TOKEN (20+ characters), then redeploy or restart."); return; }
        showAuth("setup1"); return;
      }
      if (Z.token()) { try { await start(); return; } catch (e) {} }
      showAuth("login");
    } catch (e) { showAuth("msgbox"); text($("msg"), "Service unavailable: " + e.message); } finally { kickoffDone(); }
  })();
})();
