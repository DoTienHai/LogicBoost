/**
 * LogicBoost - Main JavaScript
 * Language switching, initialization, and global utilities
 */

/* ═════════════════════════════════════════════════════════════
   Language Management
   ═════════════════════════════════════════════════════════════ */

/**
 * Get the current user's preferred language
 * Returns 'en' or 'vi', defaults to 'en'
 */
function getCurrentLanguage() {
    return localStorage.getItem('preferredLanguage') || 'en';
}

/**
 * Switch application language
 * Saves preference and reloads content in selected language
 * @param {string} lang - Language code ('en' or 'vi')
 */
function switchLanguage(lang) {
    if (!['en', 'vi'].includes(lang)) {
        console.warn(`Invalid language: ${lang}`);
        return;
    }

    // Save language preference to localStorage
    localStorage.setItem('preferredLanguage', lang);

    // Update button styling
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const langButton = document.getElementById(`lang-${lang}`);
    if (langButton) {
        langButton.classList.add('active');
    }

    // Log for debugging
    console.log(`Language switched to: ${lang}`);

    // If on a question page, reload content in selected language
    const questionBody = document.getElementById('question-body');
    if (questionBody) {
        reloadQuestionContent(lang);
    }
}

/**
 * Reload question content in selected language
 * Fetches content from API and re-renders with Markdown + LaTeX
 * @param {string} lang - Language code ('en' or 'vi')
 */
function reloadQuestionContent(lang) {
    const questionId = window.currentQuestionId;
    if (!questionId) {
        console.warn('Question ID not available for language switch');
        return;
    }

    // Determine which API endpoint to use
    let apiUrl = '';
    
    if (window.dailyChallengeSubmitUrl) {
        // On daily challenge page - would need a separate endpoint
        apiUrl = `/daily_challenge/question/${questionId}?lang=${lang}`;
    } else if (window.miniGameApiUrl) {
        // On mini game page
        apiUrl = `/mini_game/question/${questionId}?lang=${lang}`;
    } else if (window.realWorldApiUrl) {
        // On real-world page
        apiUrl = `/real_world/scenario/${questionId}?lang=${lang}`;
    }

    if (!apiUrl) {
        console.warn('Unable to determine API endpoint for language switch');
        return;
    }

    // Fetch content in selected language
    fetch(apiUrl)
        .then(res => res.json())
        .then(data => {
            // Update question body
            const questionBody = document.getElementById('question-body');
            if (questionBody && data.question) {
                // Step 1: Render Markdown
                questionBody.innerHTML = marked.parse(data.question);

                // Step 2: Render LaTeX (if KaTeX is loaded)
                if (typeof renderMathInElement !== 'undefined') {
                    renderMathInElement(questionBody, {
                        delimiters: [
                            { left: '$$', right: '$$', display: true },
                            { left: '$', right: '$', display: false }
                        ],
                        throwOnError: false
                    });
                }
            }

            // Update explanation if visible
            const explanationBody = document.getElementById('explanation-body');
            if (explanationBody && data.explanation) {
                explanationBody.innerHTML = marked.parse(data.explanation);
                if (typeof renderMathInElement !== 'undefined') {
                    renderMathInElement(explanationBody, {
                        delimiters: [
                            { left: '$$', right: '$$', display: true },
                            { left: '$', right: '$', display: false }
                        ],
                        throwOnError: false
                    });
                }
            }

            console.log(`Question content loaded in ${lang}`);
        })
        .catch(err => {
            console.error('Error reloading question content:', err);
        });
}

/* ═════════════════════════════════════════════════════════════
   Initialization
   ═════════════════════════════════════════════════════════════ */

/**
 * Initialize the application on page load
 */
document.addEventListener('DOMContentLoaded', function () {
    // Initialize language preference
    const currentLang = getCurrentLanguage();
    const langButton = document.getElementById(`lang-${currentLang}`);

    if (langButton) {
        langButton.classList.add('active');
    }

    // Update all language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        const btnLang = btn.id.replace('lang-', '');
        if (btnLang !== currentLang) {
            btn.classList.remove('active');
        }
    });

    // Log initialization
    console.log(`LogicBoost initialized with language: ${currentLang}`);
});

/* ═════════════════════════════════════════════════════════════
   Utility Functions
   ═════════════════════════════════════════════════════════════ */

/**
 * Format date to readable string
 * @param {Date|string} date - Date to format
 * @returns {string} - Formatted date string
 */
function formatDate(date) {
    const d = new Date(date);
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const year = d.getFullYear();
    return `${month}/${day}/${year}`;
}

/**
 * Format time in seconds to readable format (MM:SS)
 * @param {number} seconds - Seconds to format
 * @returns {string} - Formatted time string
 */
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${String(secs).padStart(2, '0')}`;
}

/**
 * Disable a button and show loading state
 * @param {HTMLElement} button - Button element to disable
 * @param {string} loadingText - Text to show while loading
 */
function disableButtonWithLoading(button, loadingText = 'Loading...') {
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = loadingText;
    button.dataset.originalText = originalText;
}

/**
 * Re-enable a button and restore original text
 * @param {HTMLElement} button - Button element to re-enable
 */
function enableButton(button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText || 'Submit';
}
