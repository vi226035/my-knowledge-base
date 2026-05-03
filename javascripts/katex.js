(function() {
  function renderAll() {
    if (typeof katex === 'undefined') return;
    var elements = document.querySelectorAll('.arithmatex:not([data-rendered])');
    elements.forEach(function(el) {
      var tex = el.textContent || el.innerText;
      var display = el.tagName === 'DIV';
      tex = tex.replace(/^\\\[/, '').replace(/\\\]$/, '');
      tex = tex.replace(/^\\\(/, '').replace(/\\\)$/, '');
      try {
        katex.render(tex, el, {
          displayMode: display,
          throwOnError: false
        });
        el.setAttribute('data-rendered', 'true');
      } catch(e) {}
    });
  }

  // Initial render — katex is already loaded (imported before this script)
  renderAll();

  // Re-render on SPA navigation
  document$.subscribe(function() {
    renderAll();
  });
})();
