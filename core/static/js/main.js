function toggleTheme() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', newTheme);
  fetch('/set-theme/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ theme: newTheme })
  });
  localStorage.setItem('theme', newTheme);
}

window.addEventListener('load', () => {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  if (!navigator.onLine) {
    document.getElementById('offline-notice').classList.remove('hidden');
  }
});

window.addEventListener('online', () => {
  document.getElementById('offline-notice').classList.add('hidden');
});

window.addEventListener('offline', () => {
  document.getElementById('offline-notice').classList.remove('hidden');
});