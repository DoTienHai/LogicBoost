/**
 * Daily Challenge - Question Display & Answer Submission
 */

let currentQuestion = null;

/**
 * Initialize daily challenge question
 * Must be called from template with currentQuestion data
 */
function initDailyQuestion(questionData) {
    currentQuestion = questionData;
}

/**
 * Submit an answer (multiple choice or free text)
 * Fetch API to backend for validation
 * Redirect to next question or summary page
 */
function submitAnswer(answer) {
    if (!currentQuestion) {
        console.error('currentQuestion is not initialized');
        return;
    }

    fetch(window.dailyChallengeSubmitUrl || '/daily_challenge/submit_answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question_id: currentQuestion.id,
            answer: answer,
            question_type: currentQuestion.type,
            question_num: currentQuestion.number,
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.completed) {
                // All questions answered - go to summary
                window.location.href = data.next_url;
            } else {
                // Move to next question
                window.location.href = data.next_url;
            }
        })
        .catch(err => {
            console.error('Error submitting answer:', err);
            alert('Error submitting your answer. Please try again.');
        });
}

/**
 * Submit free text answer
 * Validates that input is not empty before submitting
 */
function submitTextAnswer() {
    const answerInput = document.getElementById('user-answer');
    if (!answerInput) {
        console.error('Answer input field not found');
        return;
    }

    const answer = answerInput.value.trim();
    if (!answer) {
        alert('Please type an answer');
        return;
    }

    submitAnswer(answer);
}
