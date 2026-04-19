/**
 * Admin Panel - Question Form & Import Excel
 * Handles form validation, image preview, and conditional field visibility
 */

/* ═════════════════════════════════════════════════════════════
   Question Form Functions
   ═════════════════════════════════════════════════════════════ */

/**
 * Toggle sub-category field visibility
 * Only show for "real_world" mode
 */
function toggleSubCategory() {
    const mode = document.getElementById('mode');
    const subCategoryGroup = document.getElementById('subcategory-group');

    if (!mode || !subCategoryGroup) {
        console.warn('Mode or sub-category group element not found');
        return;
    }

    if (mode.value === 'real_world') {
        subCategoryGroup.style.display = 'block';
    } else {
        subCategoryGroup.style.display = 'none';
    }
}

/**
 * Preview image file before upload
 * Shows image in preview container
 * @param {HTMLInputElement} input - File input element
 * @param {string} previewElementId - ID of preview container div
 */
function previewImage(input, previewElementId) {
    if (!input.files || !input.files[0]) {
        return;
    }

    const previewDiv = document.getElementById(previewElementId);
    if (!previewDiv) {
        console.warn(`Preview element with ID '${previewElementId}' not found`);
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        previewDiv.innerHTML = '<img src="' + e.target.result +
            '" style="max-width: 200px; max-height: 150px; border: 1px solid #ddd; padding: 5px; border-radius: 4px;">';
    };
    reader.readAsDataURL(input.files[0]);
}

/**
 * Validate question form before submission
 * Check required fields: title, question, answer, explanation, mode
 * @returns {boolean} - True if form is valid
 */
function validateQuestionForm() {
    const title = document.getElementById('title')?.value.trim();
    const question = document.getElementById('question')?.value.trim();
    const answer = document.getElementById('answer')?.value.trim();
    const explanation = document.getElementById('explanation')?.value.trim();
    const mode = document.getElementById('mode')?.value;

    // Check required fields
    if (!title) {
        alert('Please enter a title');
        return false;
    }

    if (!question) {
        alert('Please enter the question text');
        return false;
    }

    if (!answer) {
        alert('Please enter the correct answer');
        return false;
    }

    if (!explanation) {
        alert('Please enter an explanation');
        return false;
    }

    if (!mode) {
        alert('Please select a mode (Daily Challenge, Mini Game, or Real-world)');
        return false;
    }

    // If mode is real_world, check sub-category
    if (mode === 'real_world') {
        const subCategory = document.getElementById('sub_category')?.value;
        if (!subCategory) {
            alert('Please select a sub-category for Real-world problems');
            return false;
        }
    }

    return true;
}

/**
 * Toggle multiple choice options visibility
 * Show when answer type is "multiple_choice"
 */
function toggleMultipleChoiceOptions() {
    const optionA = document.getElementById('option_a');
    const optionB = document.getElementById('option_b');
    const optionC = document.getElementById('option_c');
    const optionD = document.getElementById('option_d');
    const optionsGroup = document.getElementById('options-group');

    if (!optionsGroup) {
        return;
    }

    // Check if any option has content to determine if this is multiple choice
    const hasOptions = optionA?.value || optionB?.value || optionC?.value || optionD?.value;
    
    if (hasOptions) {
        optionsGroup.style.display = 'block';
    }
}

/* ═════════════════════════════════════════════════════════════
   Initialization
   ═════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize form fields
    toggleSubCategory();
    toggleMultipleChoiceOptions();

    // Add change listeners for dynamic behavior
    const modeSelect = document.getElementById('mode');
    if (modeSelect) {
        modeSelect.addEventListener('change', toggleSubCategory);
    }

    // Add form submission validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (e) {
            if (!validateQuestionForm()) {
                e.preventDefault();
            }
        });
    }

    // Log initialization for debugging
    console.log('Admin form initialized');
});

/* ═════════════════════════════════════════════════════════════
   Excel Import Functions (if needed)
   ═════════════════════════════════════════════════════════════ */

/**
 * Handle drag-and-drop file upload
 * @param {DragEvent} e - Drag event
 */
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const dropZone = document.getElementById('drop-zone');
    if (dropZone) {
        dropZone.classList.add('drag-over');
    }
}

/**
 * Handle drop file upload
 * @param {DragEvent} e - Drop event
 */
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();

    const dropZone = document.getElementById('drop-zone');
    if (dropZone) {
        dropZone.classList.remove('drag-over');
    }

    const files = e.dataTransfer?.files;
    if (files && files[0]) {
        const fileInput = document.getElementById('excel-file');
        if (fileInput) {
            fileInput.files = files;
            // Trigger change event to update file label
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}

/**
 * Update file input label with selected filename
 * @param {HTMLInputElement} input - File input element
 */
function updateFileLabel(input) {
    const label = input.parentElement?.querySelector('.file-label');
    if (label && input.files && input.files[0]) {
        label.textContent = input.files[0].name;
    }
}

/**
 * Validate Excel import form before submission
 * @returns {boolean} - True if form is valid
 */
function validateImportForm() {
    const fileInput = document.getElementById('excel-file');
    
    if (!fileInput || !fileInput.files || !fileInput.files[0]) {
        alert('Please select an Excel file to import');
        return false;
    }

    const file = fileInput.files[0];
    const validExtensions = ['.xlsx', '.xls'];
    const fileName = file.name.toLowerCase();
    const isValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

    if (!isValidExtension) {
        alert('Please select a valid Excel file (.xlsx or .xls)');
        return false;
    }

    return true;
}
