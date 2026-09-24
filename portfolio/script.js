// Theme toggle and footer year. Everything is optional; the page works without JS.
(function () {
  var root = document.documentElement;
  var btn = document.getElementById('themeBtn');
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  function current() {
    var set = root.getAttribute('data-theme');
    if (set) return set;
    try {
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    } catch (e) { return 'dark'; }
  }
  function label() {
    if (btn) btn.textContent = current() === 'dark' ? 'light mode' : 'dark mode';
  }
  if (btn) {
    btn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      label();
    });
    label();
  }
})();
