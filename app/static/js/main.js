/* ==========================================================
   KISS Vocational Training Management System (VTMS)
   Client-Side Interactive Scripts
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Navigation Toggle
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }

  // Auto-dismissible or closeable alert banners
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    // Add close button if not present
    if (!alert.querySelector('.alert-close')) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'alert-close';
      closeBtn.innerHTML = '&times;';
      closeBtn.style.background = 'none';
      closeBtn.style.border = 'none';
      closeBtn.style.fontSize = '1.25rem';
      closeBtn.style.cursor = 'pointer';
      closeBtn.style.marginLeft = '1rem';
      closeBtn.style.color = 'inherit';
      closeBtn.style.opacity = '0.7';
      closeBtn.setAttribute('aria-label', 'Dismiss alert');
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 200);
      });
      alert.appendChild(closeBtn);
    }
  });

  // Action confirmations
  const confirmForms = document.querySelectorAll('form[data-confirm]');
  confirmForms.forEach(form => {
    form.addEventListener('submit', (e) => {
      const message = form.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
      if (!window.confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // Client-side quick filter for tables
  const filterInputs = document.querySelectorAll('[data-table-filter]');
  filterInputs.forEach(input => {
    const tableSelector = input.getAttribute('data-table-filter');
    const table = document.querySelector(tableSelector);
    if (!table) return;

    input.addEventListener('input', () => {
      const term = input.value.toLowerCase();
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
      });
    });
  });
});
