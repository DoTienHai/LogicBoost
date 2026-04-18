/* Main JavaScript */

// Language switching
function switchLanguage(lang) {
    // Save language preference to localStorage
    localStorage.setItem('preferredLanguage', lang);
    
    // Update button styling
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`lang-${lang}`).classList.add('active');
    
    // Log for debugging
    console.log(`Language switched to: ${lang}`);
    
    // TODO: Fetch and render content in selected language
    // This will be implemented when you add bilingual content to templates
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set initial language preference
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
    document.getElementById(`lang-${savedLanguage}`).classList.add('active');
    document.querySelectorAll('.lang-btn').forEach(btn => {
        if (!btn.id.includes(savedLanguage)) {
            btn.classList.remove('active');
        }
    });
    
    // Timer for mini game
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        let timeLeft = 60;
        setInterval(() => {
            if (timeLeft > 0) {
                timeLeft--;
                timerElement.textContent = timeLeft;
            }
        }, 1000);
    }
});

function selectAnswer(option) {
    alert(`You selected: ${option}`);
}

function submitAnswer() {
    const answer = document.getElementById('user-answer').value;
    if (!answer) {
        alert('Please enter an answer');
        return;
    }
    alert(`You answered: ${answer}`);
}
