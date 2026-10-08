document.getElementById('themeToggle').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('theme', next);
});

document.querySelectorAll('form[data-confirm]').forEach(f =>
  f.addEventListener('submit', e => { if (!confirm(f.dataset.confirm)) e.preventDefault(); })
);

setTimeout(() => document.querySelectorAll('.toast').forEach(t => t.remove()), 3600);
