document.addEventListener('click', (event) => {
  const target = event.target.closest('[data-query]');
  if (!target) {
    return;
  }

  const textarea = document.getElementById('sql_query');
  if (!textarea) {
    return;
  }

  textarea.value = target.getAttribute('data-query');
  textarea.focus();
});