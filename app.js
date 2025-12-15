// ========================================
// STATE MANAGEMENT
// ========================================
let quizData = null;
let currentQuestionIndex = 0;
let score = 0;
let answeredQuestions = new Set();
let bookmarkedQuestions = new Set();
let shuffledQuestions = [];

// ========================================
// DOM ELEMENTS
// ========================================
const elements = {
    // Header
    progressText: document.getElementById('progressText'),
    scoreText: document.getElementById('scoreText'),
    progressBar: document.getElementById('progressBar'),

    // Controls
    shuffleBtn: document.getElementById('shuffleBtn'),
    bookmarkBtn: document.getElementById('bookmarkBtn'),
    bookmarkIcon: document.getElementById('bookmarkIcon'),
    searchBtn: document.getElementById('searchBtn'),
    searchBox: document.getElementById('searchBox'),
    searchInput: document.getElementById('searchInput'),
    searchCloseBtn: document.getElementById('searchCloseBtn'),

    // Quiz
    quizCard: document.getElementById('quizCard'),
    quizQuestionNumber: document.getElementById('quizQuestionNumber'),
    quizQuestionText: document.getElementById('quizQuestionText'),
    optionsContainer: document.getElementById('optionsContainer'),
    quizFeedback: document.getElementById('quizFeedback'),
    feedbackContent: document.getElementById('feedbackContent'),
    quizExplanation: document.getElementById('quizExplanation'),

    // Navigation
    prevBtn: document.getElementById('prevBtn'),
    nextBtn: document.getElementById('nextBtn'),
    questionIndicator: document.getElementById('questionIndicator')
};

// ========================================
// INITIALIZATION
// ========================================
async function init() {
    try {
        // Load quiz data
        const response = await fetch('quiz_data.json');
        quizData = await response.json();

        // Initialize shuffled questions (original order)
        shuffledQuestions = [...quizData.questions];

        // Load bookmarks from localStorage
        loadBookmarks();

        // Display first question
        displayQuestion();
        updateUI();

        // Setup event listeners
        setupEventListeners();

        console.log('Quiz app initialized successfully!');
    } catch (error) {
        console.error('Error loading quiz data:', error);
        elements.quizQuestionText.textContent = '퀴즈 데이터를 불러오는데 실패했습니다.';
    }
}

// ========================================
// EVENT LISTENERS
// ========================================
function setupEventListeners() {
    // Controls
    elements.shuffleBtn.addEventListener('click', shuffleQuestions);
    elements.bookmarkBtn.addEventListener('click', toggleBookmark);
    elements.searchBtn.addEventListener('click', toggleSearch);
    elements.searchCloseBtn.addEventListener('click', toggleSearch);
    elements.searchInput.addEventListener('input', handleSearch);

    // Navigation
    elements.prevBtn.addEventListener('click', previousQuestion);
    elements.nextBtn.addEventListener('click', nextQuestion);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);
}

// ========================================
// QUESTION DISPLAY
// ========================================
function displayQuestion() {
    const question = shuffledQuestions[currentQuestionIndex];
    if (!question) return;

    // Update question
    elements.quizQuestionNumber.textContent = `Q${question.id}`;
    elements.quizQuestionText.textContent = question.question;

    // Clear previous options
    elements.optionsContainer.innerHTML = '';

    // Hide feedback
    elements.quizFeedback.classList.add('hidden');

    // Create option buttons
    question.options.forEach(option => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        button.textContent = `${option.letter}. ${option.text}`;
        button.dataset.letter = option.letter;

        // Check if already answered
        if (answeredQuestions.has(question.id)) {
            button.disabled = true;
            if (option.letter === question.answer) {
                button.classList.add('correct');
            }
        } else {
            button.addEventListener('click', () => selectAnswer(option.letter, question));
        }

        elements.optionsContainer.appendChild(button);
    });

    updateUI();
}

// ========================================
// QUIZ ANSWER SELECTION
// ========================================
function selectAnswer(selectedLetter, question) {
    const isCorrect = selectedLetter === question.answer;

    // Mark as answered
    answeredQuestions.add(question.id);

    // Update score
    if (isCorrect) {
        score++;
    }

    // Disable all buttons
    const buttons = elements.optionsContainer.querySelectorAll('.option-btn');
    buttons.forEach(btn => {
        btn.disabled = true;

        if (btn.dataset.letter === question.answer) {
            btn.classList.add('correct');
        } else if (btn.dataset.letter === selectedLetter && !isCorrect) {
            btn.classList.add('incorrect');
        }
    });

    // Show feedback
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);

    elements.feedbackContent.textContent = isCorrect ? '✓ 정답입니다!' : '✗ 오답입니다.';
    elements.quizExplanation.textContent = question.explanation || '설명이 제공되지 않았습니다.';

    // Update UI
    updateUI();
}

// ========================================
// NAVIGATION
// ========================================
function previousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        displayQuestion();
    }
}

function nextQuestion() {
    if (currentQuestionIndex < shuffledQuestions.length - 1) {
        currentQuestionIndex++;
        displayQuestion();
    }
}

// ========================================
// SHUFFLE
// ========================================
function shuffleQuestions() {
    // Fisher-Yates shuffle
    const array = [...quizData.questions];
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }

    shuffledQuestions = array;
    currentQuestionIndex = 0;

    // Reset quiz state
    answeredQuestions.clear();
    score = 0;

    displayQuestion();

    // Visual feedback
    elements.shuffleBtn.style.transform = 'rotate(360deg)';
    setTimeout(() => {
        elements.shuffleBtn.style.transform = '';
    }, 500);
}

// ========================================
// BOOKMARK
// ========================================
function toggleBookmark() {
    const questionId = shuffledQuestions[currentQuestionIndex].id;

    if (bookmarkedQuestions.has(questionId)) {
        bookmarkedQuestions.delete(questionId);
        elements.bookmarkIcon.textContent = '🤍';
    } else {
        bookmarkedQuestions.add(questionId);
        elements.bookmarkIcon.textContent = '❤️';
    }

    saveBookmarks();
}

function loadBookmarks() {
    const saved = localStorage.getItem('az900_bookmarks');
    if (saved) {
        bookmarkedQuestions = new Set(JSON.parse(saved));
    }
}

function saveBookmarks() {
    localStorage.setItem('az900_bookmarks', JSON.stringify([...bookmarkedQuestions]));
}

// ========================================
// SEARCH
// ========================================
function toggleSearch() {
    elements.searchBox.classList.toggle('active');
    if (elements.searchBox.classList.contains('active')) {
        elements.searchInput.focus();
    } else {
        elements.searchInput.value = '';
    }
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();

    if (!query) {
        shuffledQuestions = [...quizData.questions];
    } else {
        shuffledQuestions = quizData.questions.filter(q =>
            q.question.toLowerCase().includes(query) ||
            q.options.some(opt => opt.text.toLowerCase().includes(query))
        );
    }

    currentQuestionIndex = 0;
    displayQuestion();
}

// ========================================
// UI UPDATES
// ========================================
function updateUI() {
    const question = shuffledQuestions[currentQuestionIndex];
    if (!question) return;

    // Update progress
    const progress = currentQuestionIndex + 1;
    const total = shuffledQuestions.length;
    elements.progressText.textContent = `${progress}/${total}`;
    elements.questionIndicator.textContent = `${progress} / ${total}`;

    // Update progress bar
    const percentage = (progress / total) * 100;
    elements.progressBar.style.width = `${percentage}%`;

    // Update score
    const scorePercentage = total > 0 ? Math.round((score / answeredQuestions.size) * 100) || 0 : 0;
    elements.scoreText.textContent = `${scorePercentage}%`;

    // Update navigation buttons
    elements.prevBtn.disabled = currentQuestionIndex === 0;
    elements.nextBtn.disabled = currentQuestionIndex === total - 1;

    // Update bookmark icon
    const isBookmarked = bookmarkedQuestions.has(question.id);
    elements.bookmarkIcon.textContent = isBookmarked ? '❤️' : '🤍';
}

// ========================================
// KEYBOARD SHORTCUTS
// ========================================
function handleKeyboard(e) {
    // Ignore if typing in search
    if (e.target === elements.searchInput) return;

    switch (e.key) {
        case 'ArrowLeft':
            previousQuestion();
            break;
        case 'ArrowRight':
            nextQuestion();
            break;
        case 's':
        case 'S':
            shuffleQuestions();
            break;
        case 'b':
        case 'B':
            toggleBookmark();
            break;
    }
}

// ========================================
// START APP
// ========================================
init();
