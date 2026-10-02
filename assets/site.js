(() => {
  "use strict";
  const root = document.documentElement;
  const status = document.querySelector("#site-status");
  const t = (zh, en) => root.dataset.lang === "zh" ? zh : en;
  function setLanguage(lang) {
    if (!["zh", "en"].includes(lang)) return;
    root.dataset.lang = lang;
    root.lang = lang === "zh" ? "zh-CN" : "en";
    document.querySelectorAll("[data-language]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.language === lang)));
    try { localStorage.setItem("sb-lang", lang); } catch (_) {}
    document.dispatchEvent(new Event("languagechange"));
  }
  document.querySelectorAll("[data-language]").forEach(button => button.addEventListener("click", () => setLanguage(button.dataset.language)));
  let saved;
  try { saved = localStorage.getItem("sb-lang"); } catch (_) {}
  setLanguage(["zh", "en"].includes(saved) ? saved : (navigator.language.startsWith("zh") ? "zh" : "en"));
  document.querySelectorAll("[data-copy]").forEach(button => {
    button.addEventListener("click", async () => {
      const node = document.querySelector(button.dataset.copy);
      const original = button.innerHTML;
      try {
        await navigator.clipboard.writeText(node.textContent);
        button.textContent = t("已复制", "Copied");
        status.textContent = t("已复制到剪贴板。", "Copied to clipboard.");
      } catch (_) {
        const range = document.createRange();
        range.selectNodeContents(node);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = t("已选中，请复制", "Selected — copy now");
        status.textContent = t("文本已选中，请按 Ctrl+C 或 Command+C 复制。", "Text selected. Press Ctrl+C or Command+C to copy.");
      }
      window.setTimeout(() => { button.innerHTML = original; }, 2400);
    });
  });
  const dialog = document.querySelector("#figure-dialog");
  const image = document.querySelector("#dialog-image");
  let previousFocus;
  document.querySelectorAll("[data-figure]").forEach(button => button.addEventListener("click", () => {
    previousFocus = button;
    const title = t(button.dataset.titleZh, button.dataset.titleEn);
    image.src = button.dataset.figure;
    image.alt = title;
    document.querySelector("#dialog-title").textContent = title;
    dialog.showModal();
  }));
  document.querySelector("#close-figure").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => { if (event.target === dialog) {
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  }});
  dialog.addEventListener("close", () => previousFocus?.focus());
})();
