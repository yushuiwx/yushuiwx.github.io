document.addEventListener("click", (event) => {
  const trigger = event.target.closest(".publications .links .bibtex");
  if (!trigger) return;

  event.preventDefault();
  const entry = trigger.closest("[id]");
  const bibliography = entry?.querySelector("div.bibtex");
  if (!bibliography) return;

  const isOpening = bibliography.classList.contains("hidden");
  bibliography.classList.toggle("hidden");
  trigger.setAttribute("aria-expanded", String(isOpening));
});
