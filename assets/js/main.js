/* RankerToolAI — main.js
   Minimal, dependency-free. No jQuery. No framework. Fast. */

/* ── Google Analytics 4 ──────────────────────────────────────────
   Thay GA_ID bằng Measurement ID thật từ analytics.google.com
   Định dạng: G-XXXXXXXXXX
   ─────────────────────────────────────────────────────────────── */
(function () {
  var GA_ID = 'G-XXXXXXXXXX'; /* <<< THAY CHỖ NÀY */
  if (GA_ID !== 'G-XXXXXXXXXX') {
    var s = document.createElement('script');
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    s.async = true;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { anonymize_ip: true });
  }
})();

(function () {
  'use strict';

  /* ── Mobile Navigation ─────────────────────────────────── */
  const navToggle = document.getElementById('nav-toggle');
  const navMenu   = document.getElementById('nav-menu');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      const open = navMenu.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', open);
      navToggle.innerHTML = open ? '✕' : '☰';
    });
    document.addEventListener('click', function (e) {
      if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.innerHTML = '☰';
      }
    });
  }

  /* ── TOC Scroll Spy ────────────────────────────────────── */
  const tocLinks = document.querySelectorAll('.toc a[href^="#"]');
  if (tocLinks.length) {
    const headings = Array.from(tocLinks).map(function (a) {
      return document.querySelector(a.getAttribute('href'));
    }).filter(Boolean);

    function onScroll() {
      const scrollY = window.scrollY + 120;
      let active = null;
      headings.forEach(function (h) {
        if (h.offsetTop <= scrollY) active = h;
      });
      tocLinks.forEach(function (a) {
        a.classList.toggle(
          'toc-active',
          active && a.getAttribute('href') === '#' + active.id
        );
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Smooth Scroll ─────────────────────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.pushState(null, null, this.getAttribute('href'));
      }
    });
  });

  /* ── Back to Top ───────────────────────────────────────── */
  const btt = document.getElementById('back-to-top');
  if (btt) {
    window.addEventListener('scroll', function () {
      btt.style.display = window.scrollY > 600 ? 'flex' : 'none';
    }, { passive: true });
    btt.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ── Affiliate Click Tracker ───────────────────────────── */
  document.querySelectorAll('a[href*="/go/"]').forEach(function (a) {
    a.addEventListener('click', function () {
      const slug = this.href.match(/\/go\/([^/]+)/);
      if (slug && typeof gtag !== 'undefined') {
        gtag('event', 'affiliate_click', {
          event_category: 'Affiliate',
          event_label: slug[1],
          transport_type: 'beacon'
        });
      }
    });
  });

  /* ── Lazy Images ───────────────────────────────────────── */
  if ('IntersectionObserver' in window) {
    const imgObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          imgObserver.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });
    document.querySelectorAll('img[data-src]').forEach(function (img) {
      imgObserver.observe(img);
    });
  }

})();
