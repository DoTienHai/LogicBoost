/* Main JavaScript */

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

// Timer for mini game
document.addEventListener('DOMContentLoaded', function() {
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
