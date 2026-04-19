/**
 * LogicBoost - Authentication & Form Utilities
 * Common functions for form validation, AJAX, and UI feedback
 */

/* ═════════════════════════════════════════════════════════════
   Email Validation
   ═════════════════════════════════════════════════════════════ */

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email format
 */
function isEmailValid(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/* ═════════════════════════════════════════════════════════════
   Username Validation
   ═════════════════════════════════════════════════════════════ */

/**
 * Validate username format
 * @param {string} username - Username to validate
 * @returns {boolean} True if username is 3-20 chars, alphanumeric + underscore
 */
function isUsernameValid(username) {
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    return usernameRegex.test(username);
}

/* ═════════════════════════════════════════════════════════════
   Password Strength
   ═════════════════════════════════════════════════════════════ */

/**
 * Calculate password strength level
 * @param {string} password - Password to evaluate
 * @returns {string} Strength level: 'weak', 'fair', 'good', or 'strong'
 */
function calculatePasswordStrength(password) {
    if (!password) return '';

    let score = 0;

    // Length checks
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (password.length >= 16) score++;

    // Character types
    if (/[a-z]/.test(password)) score++;  // lowercase
    if (/[A-Z]/.test(password)) score++;  // uppercase
    if (/\d/.test(password)) score++;     // numbers
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score++;  // special

    // Return strength level
    if (score <= 2) return 'weak';
    if (score <= 4) return 'fair';
    if (score <= 5) return 'good';
    return 'strong';
}

/* ═════════════════════════════════════════════════════════════
   Password Visibility Toggle
   ═════════════════════════════════════════════════════════════ */

/**
 * Toggle password field visibility
 * @param {HTMLInputElement} inputElement - Password input element
 * @param {HTMLElement} buttonElement - Toggle button element
 */
function togglePasswordVisibility(inputElement, buttonElement) {
    if (!inputElement || !buttonElement) return;

    const type = inputElement.type === 'password' ? 'text' : 'password';
    inputElement.type = type;
    buttonElement.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
    buttonElement.setAttribute('aria-label', type === 'password' ? 'Show password' : 'Hide password');
}

/* ═════════════════════════════════════════════════════════════
   Form Field Error Display
   ═════════════════════════════════════════════════════════════ */

/**
 * Show error message on form field
 * @param {HTMLElement|string} fieldElement - Form field or field ID
 * @param {string} errorMessage - Error message to display
 */
function showFieldError(fieldElement, errorMessage) {
    if (typeof fieldElement === 'string') {
        fieldElement = document.getElementById(fieldElement);
    }

    if (!fieldElement) return;

    const errorEl = fieldElement.parentElement.querySelector('.form-error');
    if (errorEl) {
        errorEl.textContent = errorMessage;
    }

    fieldElement.parentElement.classList.add('has-error');
}

/**
 * Clear error message on form field
 * @param {HTMLElement|string} fieldElement - Form field or field ID
 */
function clearFieldError(fieldElement) {
    if (typeof fieldElement === 'string') {
        fieldElement = document.getElementById(fieldElement);
    }

    if (!fieldElement) return;

    const errorEl = fieldElement.parentElement.querySelector('.form-error');
    if (errorEl) {
        errorEl.textContent = '';
    }

    fieldElement.parentElement.classList.remove('has-error');
}

/**
 * Show success state on form field
 * @param {HTMLElement|string} fieldElement - Form field or field ID
 */
function showFieldSuccess(fieldElement) {
    if (typeof fieldElement === 'string') {
        fieldElement = document.getElementById(fieldElement);
    }

    if (!fieldElement) return;

    fieldElement.parentElement.classList.remove('has-error');
    fieldElement.parentElement.classList.add('has-success');
}

/* ═════════════════════════════════════════════════════════════
   Toast Notifications
   ═════════════════════════════════════════════════════════════ */

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (default 4000)
 */
function showToast(message, type = 'info', duration = 4000) {
    // Create or get container
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    // Add to container
    container.appendChild(toast);

    // Fade out and remove after duration
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/* ═════════════════════════════════════════════════════════════
   Modal Dialogs
   ═════════════════════════════════════════════════════════════ */

/**
 * Show a confirmation modal
 * @param {string} title - Modal title
 * @param {string} message - Modal message
 * @param {Function} onConfirm - Callback when user confirms
 * @param {string} confirmText - Text for confirm button (default: Confirm)
 * @param {string} cancelText - Text for cancel button (default: Cancel)
 */
function showConfirmDialog(title, message, onConfirm, confirmText = 'Confirm', cancelText = 'Cancel') {
    let modal = document.getElementById('confirm-modal');

    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'confirm-modal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2 id="confirm-modal-title"></h2>
                    <button class="modal-close" id="confirm-modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <p id="confirm-modal-message"></p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="confirm-modal-cancel"></button>
                    <button class="btn btn-primary" id="confirm-modal-confirm"></button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Set content
    document.getElementById('confirm-modal-title').textContent = title;
    document.getElementById('confirm-modal-message').textContent = message;
    document.getElementById('confirm-modal-confirm').textContent = confirmText;
    document.getElementById('confirm-modal-cancel').textContent = cancelText;

    // Setup handlers
    const confirmBtn = document.getElementById('confirm-modal-confirm');
    const cancelBtn = document.getElementById('confirm-modal-cancel');
    const closeBtn = document.getElementById('confirm-modal-close');

    const closeModal = () => {
        modal.classList.remove('show');
        confirmBtn.removeEventListener('click', handleConfirm);
        cancelBtn.removeEventListener('click', closeModal);
        closeBtn.removeEventListener('click', closeModal);
    };

    const handleConfirm = () => {
        onConfirm();
        closeModal();
    };

    confirmBtn.addEventListener('click', handleConfirm);
    cancelBtn.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);

    // Show modal
    modal.classList.add('show');
}

/* ═════════════════════════════════════════════════════════════
   AJAX Helpers
   ═════════════════════════════════════════════════════════════ */

/**
 * Fetch with CSRF token
 * @param {string} url - URL to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>}
 */
async function fetchWithCsrf(url, options = {}) {
    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || 
                      document.querySelector('[data-csrf-token]')?.getAttribute('data-csrf-token');

    // Set headers
    options.headers = options.headers || {};
    if (csrfToken) {
        options.headers['X-CSRFToken'] = csrfToken;
    }

    return fetch(url, options);
}

/**
 * Make a POST request with JSON
 * @param {string} url - URL to post to
 * @param {Object} data - Data to send
 * @returns {Promise<Object>}
 */
async function postJSON(url, data) {
    const response = await fetchWithCsrf(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

/**
 * Make a DELETE request
 * @param {string} url - URL to delete
 * @returns {Promise<Response>}
 */
async function deleteRequest(url) {
    return fetchWithCsrf(url, { method: 'DELETE' });
}

/* ═════════════════════════════════════════════════════════════
   Form Utilities
   ═════════════════════════════════════════════════════════════ */

/**
 * Disable form submit button and show spinner
 * @param {HTMLFormElement} form - Form element
 * @param {string} spinnerId - ID of spinner element
 */
function disableFormSubmit(form, spinnerId = 'form-spinner') {
    const submitBtn = form.querySelector('button[type="submit"]');
    const spinner = document.getElementById(spinnerId);

    if (submitBtn) submitBtn.disabled = true;
    if (spinner) spinner.style.display = 'inline-block';
}

/**
 * Enable form submit button and hide spinner
 * @param {HTMLFormElement} form - Form element
 * @param {string} spinnerId - ID of spinner element
 */
function enableFormSubmit(form, spinnerId = 'form-spinner') {
    const submitBtn = form.querySelector('button[type="submit"]');
    const spinner = document.getElementById(spinnerId);

    if (submitBtn) submitBtn.disabled = false;
    if (spinner) spinner.style.display = 'none';
}

/**
 * Get form data as object
 * @param {HTMLFormElement} form - Form element
 * @returns {Object}
 */
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        if (key in data) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }

    return data;
}

/**
 * Detect if form has been modified
 * @param {HTMLFormElement} form - Form element
 * @returns {boolean}
 */
function hasFormChanged(form) {
    const initialState = new FormData(form);
    const currentState = new FormData(form);

    return Array.from(initialState.entries()).some(([key, value]) => 
        currentState.get(key) !== value
    );
}

/* ═════════════════════════════════════════════════════════════
   Table Utilities
   ═════════════════════════════════════════════════════════════ */

/**
 * Filter table rows based on search text
 * @param {HTMLTableElement} table - Table element
 * @param {string} searchText - Text to search for
 * @param {number} columnIndex - Column index to search (default: all columns)
 */
function filterTableRows(table, searchText, columnIndex = -1) {
    const rows = table.querySelectorAll('tbody tr');
    const lowerSearch = searchText.toLowerCase();

    rows.forEach(row => {
        let matches = false;

        if (columnIndex >= 0) {
            // Search specific column
            const cell = row.cells[columnIndex];
            if (cell && cell.textContent.toLowerCase().includes(lowerSearch)) {
                matches = true;
            }
        } else {
            // Search all columns
            for (let cell of row.cells) {
                if (cell.textContent.toLowerCase().includes(lowerSearch)) {
                    matches = true;
                    break;
                }
            }
        }

        row.style.display = matches ? '' : 'none';
    });
}

/**
 * Sort table by column
 * @param {HTMLTableElement} table - Table element
 * @param {number} columnIndex - Column index to sort by
 * @param {boolean} ascending - Sort direction (default: true for ascending)
 */
function sortTable(table, columnIndex, ascending = true) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        // Try to parse as numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }

        // String comparison
        return ascending ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });

    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));
}

/* ═════════════════════════════════════════════════════════════
   Initialization
   ═════════════════════════════════════════════════════════════ */

/**
 * Initialize form validation on document ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-clear errors on input
    document.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('input', function() {
            if (this.parentElement.classList.contains('has-error')) {
                clearFieldError(this);
            }
        });
    });
});
