// Aurum Visitenkarten — kleines Script für Scroll-Reveal & PWA-Feinschliff
(function () {
  document.documentElement.classList.remove('no-js');

  // Scroll-Reveal mit IntersectionObserver
  const targets = document.querySelectorAll('.tile, [data-reveal]');
  if (!targets.length) return;

  if (!('IntersectionObserver' in window)) {
    // Fallback: alles direkt sichtbar
    targets.forEach((el) => el.classList.add('is-revealed'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          // Stagger pro Element für Premium-Feel
          const delay = entry.target.dataset.revealDelay || (i * 90);
          setTimeout(() => entry.target.classList.add('is-revealed'), delay);
          observer.unobserve(entry.target);
        }
      });
    },
    {
      rootMargin: '0px 0px -10% 0px',
      threshold: 0.12,
    }
  );

  targets.forEach((el) => observer.observe(el));
})();
