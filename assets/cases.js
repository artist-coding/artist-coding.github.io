(() => {
  "use strict";
  const root = document.documentElement;
  const grid = document.querySelector("#case-grid");
  const search = document.querySelector("#case-search");
  const filters = document.querySelectorAll("[data-family]");
  const previous = document.querySelector("#previous-page");
  const next = document.querySelector("#next-page");
  const t = (zh, en) => root.dataset.lang === "zh" ? zh : en;
  const allowed = ["all", "F1", "F2", "F3", "T2", "T3-S", "T3-C", "T3-A", "T3"];
  let selected = allowed.includes(location.hash.slice(1)) ? location.hash.slice(1) : "all";
  let page = 1;
  let cases = [];
  const pageSize = 12;
  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function render() {
    const query = search.value.trim().toLowerCase();
    const filtered = cases.filter(item => (selected === "all" || item.family === selected || (selected === "T3" && item.family.startsWith("T3-"))) && [item.id,item.title,item.entry,item.carrier,item.boundary,item.trigger,item.violation].join(" ").toLowerCase().includes(query));
    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pageCount);
    grid.replaceChildren();
    const first = (page - 1) * pageSize;
    for (const item of filtered.slice(first, first + pageSize)) {
      const card = el("article", undefined, "case-card");
      card.append(el("span", item.family, "case-tag"), el("h2", item.title), el("p", item.id, "case-id"));
      const list = el("dl");
      [["Entry", "入口",item.entry],["Carrier","载体",item.carrier],["Boundary","边界",item.boundary],["Trigger","触发",item.trigger],["Violation","违规",item.violation]].forEach(([en,zh,value]) => {
        list.append(el("dt",t(zh,en)),el("dd", value.replaceAll("_"," ")));
      });
      card.append(list);
      if (item.safe_behavior) {
        const details = el("details");
        details.append(el("summary",t("预期安全行为","Expected safe behavior")),el("p",item.safe_behavior,"case-prompt"));
        card.append(details);
      }
      const link = el("a",t("在 GitHub 查看完整案例 ↗","View full case on GitHub ↗"));
      link.href = "https://github.com/artist-coding/harnesssafe/tree/main/runs/" + item.path.split("/").map(encodeURIComponent).join("/");
      card.append(link);
      grid.append(card);
    }
    if (!filtered.length) grid.append(el("p",t("没有匹配的案例。试试其他关键词，或清除筛选。","No matching cases. Try another keyword or clear the filters."),"empty-state"));
    document.querySelector("#case-count").textContent = t("匹配 "+filtered.length+" / 328 个案例","Showing "+filtered.length+" of 328 cases") + (filtered.length ? t(" · 当前 "+(first+1)+"–"+Math.min(first+pageSize,filtered.length)," · "+(first+1)+"–"+Math.min(first+pageSize,filtered.length)) : "");
    document.querySelector("#page-info").textContent = page+" / "+pageCount;
    previous.disabled = page <= 1;
    next.disabled = page >= pageCount;
    filters.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.family === selected)));
    search.placeholder = t("检索案例标识、载体、触发条件…","Search case ID, carrier, trigger…");
  }
  filters.forEach(button => button.addEventListener("click", () => {
    selected = button.dataset.family;
    page = 1;
    history.replaceState(null,"",selected === "all" ? location.pathname : "#"+selected);
    render();
  }));
  search.addEventListener("input", () => { page = 1; render(); });
  document.querySelector("#clear-search").addEventListener("click", () => {
    search.value = ""; selected = "all"; page = 1;
    history.replaceState(null,"",location.pathname);
    render(); search.focus();
  });
  window.addEventListener("hashchange", () => {
    selected = allowed.includes(location.hash.slice(1)) ? location.hash.slice(1) : "all";
    page = 1; render();
  });
  document.addEventListener("languagechange", () => { if (cases.length) render(); });
  previous.addEventListener("click", () => { page--; render(); grid.scrollIntoView({block:"start"}); });
  next.addEventListener("click", () => { page++; render(); grid.scrollIntoView({block:"start"}); });
  fetch("assets/cases.json").then(response => { if (!response.ok) throw new Error("HTTP "+response.status); return response.json(); }).then(data => {
    if (!Array.isArray(data.cases) || data.cases.length !== 328) throw new Error("Invalid case inventory");
    cases = data.cases; render();
  }).catch(() => {
    document.querySelector("#case-count").textContent = t("案例列表加载失败，请刷新或查看 GitHub 清单。","Could not load cases. Refresh or view the manifest on GitHub.");
    grid.append(el("p",t("请使用上方“查看冻结清单”链接浏览原始案例。","Use the frozen manifest link above to browse the source cases."),"empty-state"));
    previous.disabled = true; next.disabled = true;
  });
})();
