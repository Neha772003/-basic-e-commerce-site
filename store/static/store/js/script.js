/**
 * NovaCart – Modern E-Commerce Store
 * Pure Vanilla JavaScript Client-side interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initQuantitySteppers();
  initPasswordToggles();
  initToastAlerts();
  initRemoveConfirmations();
});

/**
 * 1. Mobile Menu Drawer Navigation
 */
function initMobileMenu() {
  const toggleBtn = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener('click', () => {
      navMenu.classList.toggle('is-active');
      const expanded = navMenu.classList.contains('is-active');
      toggleBtn.setAttribute('aria-expanded', expanded);
      toggleBtn.innerHTML = expanded ? '✕' : '☰';
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!toggleBtn.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('is-active');
        toggleBtn.setAttribute('aria-expanded', 'false');
        toggleBtn.innerHTML = '☰';
      }
    });
  }
}

/**
 * 2. Quantity Selector Steppers (+ / - buttons)
 */
function initQuantitySteppers() {
  const steppers = document.querySelectorAll('.qty-stepper');

  steppers.forEach((stepper) => {
    const input = stepper.querySelector('.qty-input');
    const minusBtn = stepper.querySelector('.qty-btn-minus');
    const plusBtn = stepper.querySelector('.qty-btn-plus');
    const form = stepper.closest('form');

    if (!input) return;

    const min = parseInt(input.getAttribute('min') || '1', 10);
    const max = parseInt(input.getAttribute('max') || '9999', 10);

    if (minusBtn) {
      minusBtn.addEventListener('click', (e) => {
        e.preventDefault();
        let val = parseInt(input.value, 10) || min;
        if (val > min) {
          input.value = val - 1;
          if (form && form.dataset.autoSubmit === 'true') {
            form.submit();
          }
        }
      });
    }

    if (plusBtn) {
      plusBtn.addEventListener('click', (e) => {
        e.preventDefault();
        let val = parseInt(input.value, 10) || min;
        if (val < max) {
          input.value = val + 1;
          if (form && form.dataset.autoSubmit === 'true') {
            form.submit();
          }
        } else {
          showClientToast(`Maximum available stock is ${max}`, 'warning');
        }
      });
    }

    // Direct input validation
    input.addEventListener('change', () => {
      let val = parseInt(input.value, 10);
      if (isNaN(val) || val < min) {
        input.value = min;
      } else if (val > max) {
        input.value = max;
        showClientToast(`Maximum available stock is ${max}`, 'warning');
      }
      if (form && form.dataset.autoSubmit === 'true') {
        form.submit();
      }
    });
  });
}

/**
 * 3. Password Visibility Toggle
 */
function initPasswordToggles() {
  const toggleButtons = document.querySelectorAll('.password-toggle-btn');

  toggleButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          btn.textContent = 'Hide';
        } else {
          input.type = 'password';
          btn.textContent = 'Show';
        }
      }
    });
  });
}

/**
 * 4. Toast Notifications Auto-Dismiss & Manual Close
 */
function initToastAlerts() {
  const toasts = document.querySelectorAll('.toast');

  toasts.forEach((toast) => {
    // Manual close button
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        dismissToast(toast);
      });
    }

    // Auto dismiss after 5s
    setTimeout(() => {
      dismissToast(toast);
    }, 5000);
  });
}

function dismissToast(toast) {
  if (!toast) return;
  toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
  toast.style.opacity = '0';
  toast.style.transform = 'translateX(100%)';
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  }, 400);
}

/**
 * Helper to show dynamic client-side toasts
 */
function showClientToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button type="button" class="toast-close" aria-label="Close">✕</button>
  `;

  const closeBtn = toast.querySelector('.toast-close');
  closeBtn.addEventListener('click', () => dismissToast(toast));

  container.appendChild(toast);

  setTimeout(() => {
    dismissToast(toast);
  }, 4500);
}

/**
 * 5. Cart Item Removal Confirmation
 */
function initRemoveConfirmations() {
  const removeForms = document.querySelectorAll('.form-remove-item');

  removeForms.forEach((form) => {
    form.addEventListener('submit', (e) => {
      const productName = form.dataset.productName || 'this item';
      const confirmed = confirm(`Are you sure you want to remove "${productName}" from your cart?`);
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });
}
