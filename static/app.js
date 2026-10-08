(function () {
  const root = document.documentElement;

  document.getElementById('themeToggle').addEventListener('click', () => {
    const next = root.dataset.theme === 'dusk' ? 'day' : 'dusk';
    root.dataset.theme = next;
    localStorage.setItem('theme', next);
  });

  const box = document.getElementById('bubbles');
  for (let i = 0; i < 14; i++) {
    const b = document.createElement('span');
    const size = 18 + Math.random() * 70;
    b.className = 'bubble';
    b.style.cssText = 'width:' + size + 'px;height:' + size + 'px;left:' + Math.random() * 100 +
      '%;animation-duration:' + (14 + Math.random() * 18) + 's;animation-delay:-' + Math.random() * 20 + 's';
    box.appendChild(b);
  }

  const clock = document.getElementById('clock');
  function tick() {
    const d = new Date();
    clock.innerHTML = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) +
      '<br>' + d.toLocaleDateString();
  }
  tick();
  setInterval(tick, 30000);

  document.querySelectorAll('form[data-confirm]').forEach(f =>
    f.addEventListener('submit', e => { if (!confirm(f.dataset.confirm)) e.preventDefault(); })
  );

  setTimeout(() => document.querySelectorAll('.toast').forEach(t => t.remove()), 3800);
})();
