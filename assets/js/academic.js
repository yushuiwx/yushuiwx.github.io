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

const topConferenceAbbreviations = new Set(["ACL", "ACM MM", "EMNLP", "ICCV", "ICLR", "IROS", "KDD", "NeurIPS"]);

document.querySelectorAll(".publications .row").forEach((publication) => {
  const abbreviation = publication.querySelector(".abbr abbr")?.textContent.trim();
  const periodical = publication.querySelector(".periodical");
  const year = periodical?.textContent.match(/\b(?:19|20)\d{2}\b/)?.[0];

  if (!abbreviation || !year || !periodical || !topConferenceAbbreviations.has(abbreviation)) return;

  const label = document.createElement("span");
  label.className = "venue-label";
  label.textContent = `${abbreviation} ${year}`;
  periodical.append(label);
});
