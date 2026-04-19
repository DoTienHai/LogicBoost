/**
 * Mini Game - Quick Challenge Game Logic
 * Sudden Death Mode: First wrong answer ends the game
 */

let currentQuestion = null;
let timeRemaining = 60;
let currentScore = 0;
let gameActive = true;
let timerInterval = null;
let selectedAnswer = null;

/**
 * Initialize and start the game
 * Load first question and start timer
 */
function initGame() {
    currentScore = 0;
    gameActive = true;
    timeRemaining = 60;
    selectedAnswer = null;
    document.getElementById('score').textContent = '0';
    loadQuestion();
}

/**
 * Start the countdown timer
 * When timer reaches 0, end the game
 */
function startTimer() {
    // Always clear existing timer before starting a new one
    clearInterval(timerInterval);
    timerInterval = null;

    document.getElementById('timer').textContent = timeRemaining;

    timerInterval = setInterval(() => {
        timeRemaining--;
        document.getElementById('timer').textContent = timeRemaining;

        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            endGame();
        }
    }, 1000);
}

/**
 * Fetch a new question from the backend
 * Displays the question and starts the timer
 */
function loadQuestion() {
    // Safety: ensure timer is stopped
    clearInterval(timerInterval);
    timerInterval = null;

    document.getElementById('answer-section').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('loading').innerHTML = 'Loading question...';

    fetch(window.miniGameApiUrl || '/mini_game/question')
        .then(res => res.json())
        .then(data => {
            currentQuestion = data;
            timeRemaining = data.time_limit || 60;
            displayQuestion(data);
            // Restore game state and start fresh timer
            gameActive = true;
            startTimer();
        })
        .catch(err => {
            console.error('loadQuestion fetch error:', err);
            document.getElementById('loading').innerHTML = 'Error loading question';
        });
}

/**
 * Display question on the page
 * Render Markdown + LaTeX content
 * Show appropriate answer input (multiple choice or free text)
 */
function displayQuestion(question) {
    try {
        // Validate question data
        if (!question) {
            console.error('displayQuestion: question is null/undefined');
            document.getElementById('loading').innerHTML = 'Error: No question data';
            return;
        }

        // Validate question text
        const questionText = question.question;
        if (!questionText) {
            console.error('displayQuestion: question.question is null/undefined', question);
            document.getElementById('loading').innerHTML = 'Error: Question text missing';
            return;
        }

        document.getElementById('loading').style.display = 'none';
        document.getElementById('answer-section').style.display = 'block';

        // Display question with Markdown + LaTeX rendering
        const questionSection = document.getElementById('question-section');

        let questionHtml = `<h3>${question.title || 'Question'}</h3>`;

        if (question.question_image) {
            questionHtml += `<img src="/static/images/questions/${question.question_image}" alt="Question image" style="max-width: 100%; margin: 15px 0;">`;
        }

        // Create a temporary div for question content
        const questionContentDiv = document.createElement('div');
        questionContentDiv.className = 'question-content';

        // Step 1: Render Markdown - use marked.parse with safe conversion
        try {
            questionContentDiv.innerHTML = marked.parse(questionText);
        } catch (markdownError) {
            console.error('Markdown parsing error:', markdownError, 'Text:', questionText);
            questionContentDiv.innerHTML = `<p>${questionText}</p>`;
        }

        questionSection.innerHTML = questionHtml;
        questionSection.appendChild(questionContentDiv);

        // Step 2: Render LaTeX in the question content
        if (typeof renderMathInElement !== 'undefined') {
            renderMathInElement(questionContentDiv, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false }
                ],
                throwOnError: false
            });
        }

        // Display answer options
        const optionsContainer = document.getElementById('options');
        if (question.option_a) {
            // Multiple choice
            const options = [
                { key: 'a', text: question.option_a },
                { key: 'b', text: question.option_b },
                { key: 'c', text: question.option_c },
                { key: 'd', text: question.option_d },
            ];

            optionsContainer.innerHTML = options.map(opt => `
                <button class="option-btn" onclick="selectAnswer('${opt.key}', event)" data-answer="${opt.key}">
                    <span class="option-letter">${opt.key.toUpperCase()}</span>
                    <span class="option-text">${opt.text}</span>
                </button>
            `).join('');

            document.getElementById('text-answer').style.display = 'none';
            document.getElementById('text-answer').value = '';
        } else {
            // Free text input
            optionsContainer.innerHTML = '';
            document.getElementById('text-answer').style.display = 'block';
            document.getElementById('text-answer').value = '';
            document.getElementById('text-answer').focus();
        }
    } catch (err) {
        console.error('displayQuestion error:', err);
        console.error('Stack:', err.stack);
        document.getElementById('loading').innerHTML = 'Error displaying question: ' + err.message;
    }
}

/**
 * Handle multiple choice answer selection
 * Highlight the selected option visually
 */
function selectAnswer(key, event) {
    // Store selected answer
    selectedAnswer = key;

    // Visual feedback: highlight selected option
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.classList.remove('selected');
    });

    // Find and highlight the clicked button
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('selected');
    } else {
        // Fallback for direct calls
        const clickedBtn = document.querySelector(`[data-answer="${key}"]`);
        if (clickedBtn) {
            clickedBtn.classList.add('selected');
        }
    }
}

/**
 * Submit the user's answer to the backend
 * Check if correct: load next question (green flash)
 * Check if wrong: end game (Sudden Death)
 */
function submitMiniAnswer() {
    if (!gameActive) {
        return;
    }

    // Get answer from either text input or selected option
    let answer = null;

    const textInput = document.getElementById('text-answer');
    if (textInput && textInput.style.display !== 'none' && textInput.value.trim()) {
        // Free text answer
        answer = textInput.value.trim();
    } else if (selectedAnswer) {
        // Multiple choice answer
        answer = selectedAnswer;
    }

    if (!answer) {
        alert('Please select or type an answer');
        return;
    }

    const timeUsed = 60 - timeRemaining;

    // Disable submit while processing
    gameActive = false;

    fetch(window.miniGameSubmitUrl || '/mini_game/submit_answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question_id: currentQuestion.id,
            answer: answer,
            time_taken: timeUsed
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.game_over) {
                // Wrong answer - Game Over (Sudden Death)
                currentScore = data.score;
                endGame(data);
            } else {
                // Correct answer - Load next question
                currentScore = data.score;
                document.getElementById('score').textContent = currentScore;

                // Show visual feedback (green flash)
                showFeedback(true);

                // Reset selected answer
                selectedAnswer = null;

                // Stop current timer immediately to prevent overlap
                clearInterval(timerInterval);
                timerInterval = null;

                // Load next question after short delay
                setTimeout(() => {
                    loadQuestion();
                }, 600);
            }
        })
        .catch(err => {
            alert('Error submitting answer');
            console.error(err);
            gameActive = true;
        });
}

/**
 * Show visual feedback for answer correctness
 * Green flash = correct, Red flash = wrong
 */
function showFeedback(isCorrect) {
    const section = document.getElementById('question-section');
    section.style.backgroundColor = isCorrect ? '#d4edda' : '#f8d7da';
    setTimeout(() => {
        section.style.backgroundColor = '';
    }, 500);
}

/**
 * End the game
 * Display final score and explanation of last wrong answer
 */
function endGame(wrongAnswerData = null) {
    gameActive = false;
    clearInterval(timerInterval);
    timerInterval = null;

    // Hide question and answer sections
    document.getElementById('question-section').style.display = 'none';
    document.getElementById('answer-section').style.display = 'none';

    // Show game over screen
    const gameOverScreen = document.getElementById('game-over-screen');
    gameOverScreen.style.display = 'block';
    document.getElementById('final-score').textContent = currentScore;

    // Display wrong answer details if available
    if (wrongAnswerData && !wrongAnswerData.is_correct) {
        const reviewHtml = `
            <div class="wrong-answer">
                <h4>❌ Last Question (Wrong Answer)</h4>
                <p><strong>Correct answer:</strong> ${wrongAnswerData.correct_answer}</p>
                ${wrongAnswerData.explanation ? `<div style="margin-top: 15px; text-align: left;"><strong>Explanation:</strong><br>${wrongAnswerData.explanation}</div>` : ''}
            </div>
        `;
        document.getElementById('answer-review').innerHTML = reviewHtml;
    } else {
        document.getElementById('answer-review').innerHTML = '<p>Time ran out!</p>';
    }
}

/**
 * Reload the page to play again
 */
function playAgain() {
    location.reload();
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    initGame();
});
