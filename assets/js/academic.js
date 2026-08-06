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

const appendGeneratedTocLink = (container, targetId, label) => {
  if (!targetId || container.querySelector(`a[href="#${targetId}"]`)) return;

  const link = document.createElement("a");
  link.href = `#${targetId}`;
  link.textContent = label;
  container.append(link);
};

document.querySelectorAll("[data-page-toc]").forEach((toc) => {
  const linksContainer = toc.querySelector(".page-toc-links");
  const toggle = toc.querySelector(".page-toc-toggle");
  const source = toc.dataset.tocSource;
  if (!linksContainer || !toggle) return;

  if (source === "publication-years") {
    document.querySelectorAll(".publications h2.bibliography").forEach((heading) => {
      const year = heading.textContent.trim();
      if (!year) return;

      heading.id = heading.id || `year-${year.replace(/[^0-9a-z-]/gi, "-").toLowerCase()}`;
      appendGeneratedTocLink(linksContainer, heading.id, year);
    });
  }

  if (source === "blog-years") {
    const years = new Set();
    document.querySelectorAll(".blog-item").forEach((item) => {
      const year = item.querySelector("time")?.getAttribute("datetime")?.slice(0, 4);
      if (!year || years.has(year)) return;

      years.add(year);
      item.id = item.id || `posts-${year}`;
      appendGeneratedTocLink(linksContainer, item.id, year);
    });
  }

  toggle.addEventListener("click", () => {
    const isOpen = toc.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  linksContainer.addEventListener("click", (event) => {
    if (!event.target.closest("a")) return;
    toc.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
  });

  const links = [...linksContainer.querySelectorAll('a[href^="#"]')];
  const targets = links.map((link) => document.getElementById(link.hash.slice(1)));

  const updateActiveLink = () => {
    const threshold = window.scrollY + 110;
    let activeIndex = 0;

    targets.forEach((target, index) => {
      if (target && target.getBoundingClientRect().top + window.scrollY <= threshold) activeIndex = index;
    });

    links.forEach((link, index) => {
      const isActive = index === activeIndex;
      link.classList.toggle("is-active", isActive);
      if (isActive) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  };

  updateActiveLink();
  window.addEventListener("scroll", updateActiveLink, { passive: true });
});
