// ========================================
// STATE MANAGEMENT
// ========================================
let quizData = null;
let currentQuestionIndex = 0;
let score = 0;
let answeredQuestions = new Set();
let firstAttempts = new Map(); // Track first attempt results: { questionId: { isCorrect: boolean, userAnswer: any } }
let bookmarkedQuestions = new Set();
let shuffledQuestions = [];
let touchStartX = 0;
let touchEndX = 0;

// ========================================
// DOM ELEMENTS
// ========================================
const elements = {
    // Header
    progressText: document.getElementById('progressText'),
    scoreText: document.getElementById('scoreText'),
    progressBar: document.getElementById('progressBar'),
    questionJumpButtons: document.getElementById('questionJumpButtons'),

    // Controls
    shuffleBtn: document.getElementById('shuffleBtn'),
    bookmarkBtn: document.getElementById('bookmarkBtn'),
    bookmarkIcon: document.getElementById('bookmarkIcon'),
    searchBtn: document.getElementById('searchBtn'),
    searchBox: document.getElementById('searchBox'),
    searchInput: document.getElementById('searchInput'),
    searchNextBtn: document.getElementById('searchNextBtn'),
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
        const response = await fetch('data/quiz_data.json');
        quizData = await response.json();

        // Initialize shuffled questions (original order)
        shuffledQuestions = [...quizData.questions];

        // Load bookmarks from localStorage
        loadBookmarks();

        // Create question jump buttons
        createQuestionJumpButtons();

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
    elements.searchNextBtn.addEventListener('click', searchNextQuestion);
    elements.searchCloseBtn.addEventListener('click', toggleSearch);

    // Search on Enter key
    elements.searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            searchNextQuestion();
        }
    });

    // Navigation
    elements.prevBtn.addEventListener('click', previousQuestion);
    elements.nextBtn.addEventListener('click', nextQuestion);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);

    // Swipe gestures for mobile
    document.addEventListener('touchstart', handleTouchStart, { passive: false });
    document.addEventListener('touchend', handleTouchEnd, { passive: false });
}

function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].clientX;
}

function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].clientX;
    handleSwipeGesture(e);
}

function handleSwipeGesture(e) {
    const swipeThreshold = 50; // Minimum distance for a swipe
    const diff = touchEndX - touchStartX;

    if (Math.abs(diff) > swipeThreshold) {
        // Prevent default browser behavior (like back/forward navigation)
        if (e.cancelable) e.preventDefault();

        if (diff < 0) {
            // Swipe Left -> Next Question
            nextQuestion();
        } else {
            // Swipe Right -> Previous Question
            previousQuestion();
        }
    }
}

// ========================================
// QUESTION DISPLAY
// ========================================
function displayQuestion() {
    const question = shuffledQuestions[currentQuestionIndex];
    if (!question) return;

    // Update question number with status badge
    const firstAttempt = firstAttempts.get(question.id);
    if (firstAttempt) {
        const statusBadge = firstAttempt.isCorrect ?
            '<span style="color: #10b981; font-size: 0.9em; margin-left: 0.5rem;">정답</span>' :
            '<span style="color: #ef4444; font-size: 0.9em; margin-left: 0.5rem;">오답</span>';
        elements.quizQuestionNumber.innerHTML = `Q${question.id} ${statusBadge}`;
    } else {
        elements.quizQuestionNumber.textContent = `Q${question.id}`;
    }

    elements.quizQuestionText.innerHTML = question.question.replace(/\n/g, '<br>');

    // Clear previous options
    elements.optionsContainer.innerHTML = '';

    // Hide feedback when displaying question
    elements.quizFeedback.classList.add('hidden');

    // Display question image if exists
    const existingImage = elements.quizCard.querySelector('.question-image');
    if (existingImage) {
        existingImage.remove();
    }

    if (question.image) {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'question-image';

        const img = document.createElement('img');
        img.src = question.image;
        img.alt = 'Question Image';
        img.onerror = () => {
            imageContainer.innerHTML = '<p class="image-error">⚠️ 이미지를 불러올 수 없습니다.</p>';
        };

        imageContainer.appendChild(img);
        elements.quizQuestionText.after(imageContainer);
    }

    // HOTSPOT 문제 처리
    if (question.questionType === 'HOTSPOT' && question.statements) {
        displayHotspotQuestion(question);
    } else if (question.questionType === 'MATCHING' && question.matchingItems) {
        displayMatchingQuestion(question);
    } else if (question.questionType === 'DROPDOWN' && question.dropdowns) {
        displayDropdownQuestion(question);
    } else if (question.questionType === 'DRAG_DROP' && question.dragOptions) {
        displayDragDropQuestion(question);
    } else if (question.questionType === 'MULTIPLE_CHOICE_MULTI') {
        displayMultipleChoiceMultiQuestion(question);
    } else {
        // Create option buttons (일반 문제 - 단일/복수 선택)
        question.options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.textContent = `${option.letter}. ${option.text}`;
            button.dataset.letter = option.letter;

            // Always allow clicking to select (no visual indicators on options)
            button.addEventListener('click', () => toggleSelection(button, question));

            elements.optionsContainer.appendChild(button);
        });

        // 제출 버튼 추가 (항상 표시)
        const submitBtn = document.createElement('button');
        submitBtn.className = 'option-btn submit-btn';
        submitBtn.textContent = firstAttempts.has(question.id) ? '다시 제출' : '제출';
        submitBtn.addEventListener('click', () => submitMultipleChoice(question));
        elements.optionsContainer.appendChild(submitBtn);
    }

    updateUI();
}

// ========================================
// HOTSPOT QUESTION DISPLAY
// ========================================
function displayHotspotQuestion(question) {
    const container = elements.optionsContainer;

    // 테이블 생성
    const table = document.createElement('div');
    table.className = 'hotspot-table';

    // 헤더
    const header = document.createElement('div');
    header.className = 'hotspot-header';
    header.innerHTML = `
        <div class="hotspot-col-statement">Statements</div>
        <div class="hotspot-col-answer">예</div>
        <div class="hotspot-col-answer">아니오</div>
    `;
    table.appendChild(header);

    // 각 statement에 대한 행 생성
    question.statements.forEach((statement, index) => {
        const row = document.createElement('div');
        row.className = 'hotspot-row';
        row.dataset.index = index;

        // Statement 텍스트
        const statementDiv = document.createElement('div');
        statementDiv.className = 'hotspot-statement';
        statementDiv.textContent = statement;
        row.appendChild(statementDiv);

        // Yes 체크박스
        const yesDiv = document.createElement('div');
        yesDiv.className = 'hotspot-checkbox';
        const yesInput = document.createElement('input');
        yesInput.type = 'radio';
        yesInput.name = `statement-${index}`;
        yesInput.value = '예';
        yesInput.id = `q${question.id}-s${index}-yes`;
        yesDiv.appendChild(yesInput);
        row.appendChild(yesDiv);

        // No 체크박스
        const noDiv = document.createElement('div');
        noDiv.className = 'hotspot-checkbox';
        const noInput = document.createElement('input');
        noInput.type = 'radio';
        noInput.name = `statement-${index}`;
        noInput.value = '아니오';
        noInput.id = `q${question.id}-s${index}-no`;
        noDiv.appendChild(noInput);
        row.appendChild(noDiv);

        // No visual indicators when displaying - clean state
        // Users can select answers freely

        table.appendChild(row);
    });

    container.appendChild(table);

    // 제출 버튼 (항상 표시)
    const submitBtn = document.createElement('button');
    submitBtn.className = 'option-btn submit-hotspot-btn';
    submitBtn.textContent = firstAttempts.has(question.id) ? '다시 제출' : '제출';
    submitBtn.addEventListener('click', () => submitHotspotAnswer(question));
    container.appendChild(submitBtn);
}

function submitHotspotAnswer(question) {
    const userAnswers = [];
    let allAnswered = true;

    // 각 statement의 답변 수집
    question.statements.forEach((statement, index) => {
        const yesInput = document.getElementById(`q${question.id}-s${index}-yes`);
        const noInput = document.getElementById(`q${question.id}-s${index}-no`);

        if (yesInput.checked) {
            userAnswers.push('예');
        } else if (noInput.checked) {
            userAnswers.push('아니오');
        } else {
            allAnswered = false;
        }
    });

    // 모든 statement에 답변했는지 확인
    if (!allAnswered) {
        alert('모든 항목에 답변해주세요!');
        return;
    }

    // 정답 확인
    let correctCount = 0;
    console.log('=== HOTSPOT 답변 비교 ===');
    console.log('사용자 답변:', userAnswers);
    console.log('정답:', question.answer);
    userAnswers.forEach((answer, index) => {
        console.log(`문항 ${index + 1}: 사용자="${answer}", 정답="${question.answer[index]}", 일치=${answer === question.answer[index]}`);
        if (answer === question.answer[index]) {
            correctCount++;
        }
    });
    console.log('맞은 개수:', correctCount);

    const isCorrect = correctCount === question.statements.length;

    // Track first attempt only
    if (!firstAttempts.has(question.id)) {
        firstAttempts.set(question.id, {
            isCorrect: isCorrect,
            userAnswer: userAnswers
        });

        // Update score only on first attempt
        if (isCorrect) score++;
    }

    // 답변 표시
    answeredQuestions.add(question.id);

    // UI 업데이트 - 정답 표시하지만 비활성화하지 않음
    question.statements.forEach((statement, index) => {
        const row = document.querySelector(`.hotspot-row[data-index="${index}"]`);
        const yesDiv = row.querySelector('.hotspot-checkbox:nth-child(2)');
        const noDiv = row.querySelector('.hotspot-checkbox:nth-child(3)');

        // Remove previous styling
        yesDiv.classList.remove('user-correct', 'user-incorrect', 'correct-answer');
        noDiv.classList.remove('user-correct', 'user-incorrect', 'correct-answer');

        // 사용자가 선택한 답변과 정답 비교
        const correctAnswer = question.answer[index];
        const userAnswer = userAnswers[index];

        if (userAnswer === correctAnswer) {
            // 맞은 경우 - 사용자가 선택한 것을 초록색으로
            if (userAnswer === '예') {
                yesDiv.classList.add('user-correct');
            } else {
                noDiv.classList.add('user-correct');
            }
        } else {
            // 틀린 경우 - 사용자가 선택한 것은 빨간색, 정답은 초록색으로
            if (userAnswer === '예') {
                yesDiv.classList.add('user-incorrect');
            } else {
                noDiv.classList.add('user-incorrect');
            }

            if (correctAnswer === '예') {
                yesDiv.classList.add('correct-answer');
            } else {
                noDiv.classList.add('correct-answer');
            }
        }
    });

    // 피드백 표시
    const firstAttempt = firstAttempts.get(question.id);
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);

    let feedbackText = isCorrect ?
        `✓ 정답입니다! (${correctCount}/${question.statements.length})` :
        `✗ ${correctCount}/${question.statements.length}개 정답`;

    // Add first attempt indicator if this is a re-attempt
    if (firstAttempt && JSON.stringify(firstAttempt.userAnswer) !== JSON.stringify(userAnswers)) {
        feedbackText += ` (처음 시도: ${firstAttempt.isCorrect ? '정답' : '오답'})`;
    }

    elements.feedbackContent.textContent = feedbackText;
    elements.quizExplanation.innerHTML = (question.explanation || '설명이 제공되지 않았습니다.').replace(/\n/g, '<br>');

    updateUI();
}

// ========================================
// MATCHING QUESTION DISPLAY
// ========================================
function displayMatchingQuestion(question) {
    const container = elements.optionsContainer;

    // 매칭 테이블 생성
    const matchingContainer = document.createElement('div');
    matchingContainer.className = 'matching-container';

    // 수식 문제인지 확인 (Formula Part가 포함된 경우)
    const isFormulaQuestion = question.matchingItems.some(item =>
        item.item.includes('Formula Part'));

    if (isFormulaQuestion) {
        matchingContainer.classList.add('formula-layout');
    }

    // 수식 기호 매핑
    const formulaOperators = ['', '÷', '×'];

    question.matchingItems.forEach((item, index) => {
        const itemRow = document.createElement('div');
        itemRow.className = 'matching-row';

        // 항목 이름
        const itemLabel = document.createElement('div');
        itemLabel.className = 'matching-item-label';
        itemLabel.textContent = item.item;
        itemRow.appendChild(itemLabel);

        // 선택지 드롭다운
        const selectDiv = document.createElement('div');
        selectDiv.className = 'matching-select';

        const select = document.createElement('select');
        select.className = 'matching-dropdown';
        select.id = `matching-${index}`;

        // 기본 옵션
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- 선택하세요 --';
        select.appendChild(defaultOption);

        // 선택지 추가
        item.options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt;
            select.appendChild(option);
        });

        // No visual indicators when displaying - clean state

        selectDiv.appendChild(select);
        itemRow.appendChild(selectDiv);

        matchingContainer.appendChild(itemRow);

        // 수식 문제인 경우 연산자 추가 (DOM 요소로)
        if (isFormulaQuestion && index < question.matchingItems.length - 1) {
            const operator = document.createElement('div');
            operator.className = 'formula-operator';
            operator.textContent = formulaOperators[index + 1];
            matchingContainer.appendChild(operator);
        }
    });

    container.appendChild(matchingContainer);

    // 제출 버튼 (항상 표시)
    const submitBtn = document.createElement('button');
    submitBtn.className = 'option-btn submit-matching-btn';
    submitBtn.textContent = firstAttempts.has(question.id) ? '다시 제출' : '제출';
    submitBtn.addEventListener('click', () => submitMatchingAnswer(question));
    container.appendChild(submitBtn);
}

function submitMatchingAnswer(question) {
    const userAnswers = [];
    let allAnswered = true;

    // 각 항목의 선택 수집
    question.matchingItems.forEach((item, index) => {
        const select = document.getElementById(`matching-${index}`);
        if (select.value) {
            userAnswers.push(select.value);
        } else {
            allAnswered = false;
        }
    });

    // 모든 항목에 답변했는지 확인
    if (!allAnswered) {
        alert('모든 항목을 선택해주세요!');
        return;
    }

    // 정답 확인
    let correctCount = 0;
    userAnswers.forEach((answer, index) => {
        if (answer === question.matchingItems[index].answer) {
            correctCount++;
        }
    });

    const isCorrect = correctCount === question.matchingItems.length;

    // Track first attempt only
    if (!firstAttempts.has(question.id)) {
        firstAttempts.set(question.id, {
            isCorrect: isCorrect,
            userAnswer: userAnswers
        });

        // Update score only on first attempt
        if (isCorrect) score++;
    }

    // 답변 표시
    answeredQuestions.add(question.id);

    // UI 업데이트
    question.matchingItems.forEach((item, index) => {
        const select = document.getElementById(`matching-${index}`);
        const selectDiv = select.parentElement;

        // Remove previous styling
        selectDiv.classList.remove('correct-answer', 'wrong-answer');
        const existingLabel = selectDiv.querySelector('.correct-answer-label');
        if (existingLabel) existingLabel.remove();

        // 정답 표시
        if (userAnswers[index] === item.answer) {
            selectDiv.classList.add('correct-answer');
        } else {
            selectDiv.classList.add('wrong-answer');
            // 정답도 표시
            const correctLabel = document.createElement('div');
            correctLabel.className = 'correct-answer-label';
            correctLabel.textContent = `정답: ${item.answer}`;
            selectDiv.appendChild(correctLabel);
        }
    });

    // 피드백 표시
    const firstAttempt = firstAttempts.get(question.id);
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);

    let feedbackText = isCorrect ?
        `✓ 정답입니다! (${correctCount}/${question.matchingItems.length})` :
        `✗ ${correctCount}/${question.matchingItems.length}개 정답`;

    // Add first attempt indicator if this is a re-attempt
    if (firstAttempt && JSON.stringify(firstAttempt.userAnswer) !== JSON.stringify(userAnswers)) {
        feedbackText += ` (처음 시도: ${firstAttempt.isCorrect ? '정답' : '오답'})`;
    }

    elements.feedbackContent.textContent = feedbackText;
    elements.quizExplanation.innerHTML = (question.explanation || '설명이 제공되지 않았습니다.').replace(/\n/g, '<br>');

    updateUI();
}

// ========================================
// DROPDOWN QUESTION DISPLAY
// ========================================
function displayDropdownQuestion(question) {
    const container = elements.optionsContainer;

    // 드롭다운 컨테이너 생성
    const dropdownContainer = document.createElement('div');
    dropdownContainer.className = 'dropdown-container';

    question.dropdowns.forEach((dropdown, index) => {
        const dropdownDiv = document.createElement('div');
        dropdownDiv.className = 'dropdown-item';

        const select = document.createElement('select');
        select.className = 'dropdown-select';
        select.id = `dropdown-${dropdown.id}`;

        // 기본 옵션
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- 선택하세요 --';
        select.appendChild(defaultOption);

        // 선택지 추가
        dropdown.options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.letter;
            option.textContent = `${opt.letter}. ${opt.text}`;
            select.appendChild(option);
        });

        // No visual indicators when displaying - clean state

        dropdownDiv.appendChild(select);
        dropdownContainer.appendChild(dropdownDiv);
    });

    container.appendChild(dropdownContainer);

    // 제출 버튼 (항상 표시)
    const submitBtn = document.createElement('button');
    submitBtn.className = 'option-btn submit-dropdown-btn';
    submitBtn.textContent = firstAttempts.has(question.id) ? '다시 제출' : '제출';
    submitBtn.addEventListener('click', () => submitDropdownAnswer(question));
    container.appendChild(submitBtn);
}

function submitDropdownAnswer(question) {
    const userAnswers = {};
    let allAnswered = true;

    // 각 드롭다운의 선택 수집
    question.dropdowns.forEach((dropdown) => {
        const select = document.getElementById(`dropdown-${dropdown.id}`);
        if (select.value) {
            userAnswers[dropdown.id] = select.value;
        } else {
            allAnswered = false;
        }
    });

    // 모든 드롭다운에 답변했는지 확인
    if (!allAnswered) {
        alert('모든 항목을 선택해주세요!');
        return;
    }

    // 정답 확인
    let correctCount = 0;
    let totalCount = question.dropdowns.length;

    Object.keys(userAnswers).forEach(dropdownId => {
        if (userAnswers[dropdownId] === question.answer[dropdownId]) {
            correctCount++;
        }
    });

    const isCorrect = correctCount === totalCount;

    // Track first attempt only
    if (!firstAttempts.has(question.id)) {
        firstAttempts.set(question.id, {
            isCorrect: isCorrect,
            userAnswer: userAnswers
        });

        // Update score only on first attempt
        if (isCorrect) score++;
    }

    // 답변 표시
    answeredQuestions.add(question.id);

    // UI 업데이트
    question.dropdowns.forEach((dropdown) => {
        const select = document.getElementById(`dropdown-${dropdown.id}`);
        const dropdownDiv = select.parentElement;

        // Remove previous styling
        dropdownDiv.classList.remove('correct-answer', 'wrong-answer');
        const existingLabel = dropdownDiv.querySelector('.correct-answer-label');
        if (existingLabel) existingLabel.remove();

        // 정답 표시
        const correctAnswer = question.answer[dropdown.id];
        if (userAnswers[dropdown.id] === correctAnswer) {
            dropdownDiv.classList.add('correct-answer');
        } else {
            dropdownDiv.classList.add('wrong-answer');
            // 정답도 표시
            const correctLabel = document.createElement('div');
            correctLabel.className = 'correct-answer-label';
            const correctOption = dropdown.options.find(opt => opt.letter === correctAnswer);
            correctLabel.textContent = `정답: ${correctAnswer}. ${correctOption ? correctOption.text : ''}`;
            dropdownDiv.appendChild(correctLabel);
        }
    });

    // 피드백 표시
    const firstAttempt = firstAttempts.get(question.id);
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);

    let feedbackText = isCorrect ?
        `✓ 정답입니다!` :
        `✗ ${correctCount}/${totalCount}개 정답`;

    // Add first attempt indicator if this is a re-attempt
    if (firstAttempt && JSON.stringify(firstAttempt.userAnswer) !== JSON.stringify(userAnswers)) {
        feedbackText += ` (처음 시도: ${firstAttempt.isCorrect ? '정답' : '오답'})`;
    }

    elements.feedbackContent.textContent = feedbackText;
    elements.quizExplanation.innerHTML = (question.explanation || '설명이 제공되지 않았습니다.').replace(/\n/g, '<br>');

    updateUI();
}

// ========================================
// MULTIPLE CHOICE SELECTION (with submit button)
// ========================================
function toggleSelection(button, question) {
    // Determine if it's a multi-choice question
    // 1. Array-type answer
    // 2. String answer with newlines or commas
    const isMultiChoice = Array.isArray(question.answer) ||
        (typeof question.answer === 'string' && (question.answer.includes('\n') || question.answer.includes(',')));

    if (!isMultiChoice) {
        // Single-choice logic
        const isAlreadySelected = button.classList.contains('selected');

        // Deselect all others
        const allButtons = button.parentElement.querySelectorAll('.option-btn');
        allButtons.forEach(btn => btn.classList.remove('selected'));

        // If it wasn't already selected, select it now (toggle off if it was selected)
        if (!isAlreadySelected) {
            button.classList.add('selected');
        }
    } else {
        // Multi-choice logic: Just toggle the clicked button
        button.classList.toggle('selected');
    }
}

function submitMultipleChoice(question) {
    // Get all selected options
    const selectedButtons = elements.optionsContainer.querySelectorAll('.option-btn.selected');

    if (selectedButtons.length === 0) {
        alert('답을 선택해주세요!');
        return;
    }

    const selectedLetters = Array.from(selectedButtons).map(btn => btn.dataset.letter);

    // Parse correct answers (단일 또는 복수)
    let correctAnswers = [];
    if (Array.isArray(question.answer)) {
        // 배열이면 그대로 사용
        correctAnswers = question.answer;
    } else if (question.answer.includes('\n')) {
        correctAnswers = question.answer.split('\n').map(a => a.trim()).filter(a => a.length === 1);
    } else if (question.answer.includes(',')) {
        correctAnswers = question.answer.split(',').map(a => a.trim()).filter(a => a.length === 1);
    } else {
        correctAnswers = [question.answer.trim()];
    }

    // Check if answer is correct
    const isCorrect = selectedLetters.length === correctAnswers.length &&
        selectedLetters.every(letter => correctAnswers.includes(letter));

    // Track first attempt only
    if (!firstAttempts.has(question.id)) {
        firstAttempts.set(question.id, {
            isCorrect: isCorrect,
            userAnswer: selectedLetters
        });

        // Update score only on first attempt
        if (isCorrect) {
            score++;
        }
    }

    // Mark as answered
    answeredQuestions.add(question.id);

    // Update UI to show correct answers
    const allButtons = elements.optionsContainer.querySelectorAll('.option-btn');
    allButtons.forEach(btn => {
        if (btn.classList.contains('submit-btn')) {
            return;
        }

        btn.classList.remove('selected');

        const letter = btn.dataset.letter;
        if (correctAnswers.includes(letter)) {
            btn.classList.add('correct');
        }

        if (selectedLetters.includes(letter) && !correctAnswers.includes(letter)) {
            btn.classList.add('incorrect');
        }
    });

    // Show feedback
    const firstAttempt = firstAttempts.get(question.id);
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);

    const correctCount = selectedLetters.filter(l => correctAnswers.includes(l)).length;
    let feedbackText = isCorrect ? '✓ 정답입니다!' : `✗ ${correctCount}/${correctAnswers.length}개 정답`;

    // Add first attempt indicator if this is a re-attempt
    if (firstAttempt && firstAttempt.userAnswer.toString() !== selectedLetters.toString()) {
        feedbackText += ` (처음 시도: ${firstAttempt.isCorrect ? '정답' : '오답'})`;
    }

    elements.feedbackContent.textContent = feedbackText;
    elements.quizExplanation.innerHTML = (question.explanation || '설명이 제공되지 않았습니다.').replace(/\n/g, '<br>');

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
    elements.quizExplanation.innerHTML = (question.explanation || '설명이 제공되지 않았습니다.').replace(/\n/g, '<br>');

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
    firstAttempts.clear();
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

function searchNextQuestion() {
    const query = elements.searchInput.value.toLowerCase().trim();

    if (!query) {
        alert('검색어를 입력해주세요.');
        return;
    }

    // 현재 위치 다음부터 검색
    let found = false;
    let searchStartIndex = currentQuestionIndex + 1;

    // 현재 위치 다음부터 끝까지 검색
    for (let i = searchStartIndex; i < shuffledQuestions.length; i++) {
        if (shuffledQuestions[i].question.toLowerCase().includes(query)) {
            currentQuestionIndex = i;
            found = true;
            break;
        }
    }

    // 못 찾았으면 처음부터 현재 위치까지 검색
    if (!found) {
        for (let i = 0; i < searchStartIndex; i++) {
            if (shuffledQuestions[i].question.toLowerCase().includes(query)) {
                currentQuestionIndex = i;
                found = true;
                break;
            }
        }
    }

    if (found) {
        displayQuestion();
        updateUI();
        // 검색어는 유지 (다음 검색을 위해)
    } else {
        alert(`"${query}"를 포함하는 문제를 더 이상 찾을 수 없습니다.`);
    }
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();

    if (!query) {
        return;
    }

    // 현재 위치 다음부터 검색
    let found = false;
    let searchStartIndex = currentQuestionIndex + 1;

    // 현재 위치 다음부터 끝까지 검색
    for (let i = searchStartIndex; i < shuffledQuestions.length; i++) {
        if (shuffledQuestions[i].question.toLowerCase().includes(query)) {
            currentQuestionIndex = i;
            found = true;
            break;
        }
    }

    // 못 찾았으면 처음부터 현재 위치까지 검색
    if (!found) {
        for (let i = 0; i < searchStartIndex; i++) {
            if (shuffledQuestions[i].question.toLowerCase().includes(query)) {
                currentQuestionIndex = i;
                found = true;
                break;
            }
        }
    }

    if (found) {
        displayQuestion();
        updateUI();
        elements.searchInput.value = ''; // 검색 후 입력창 비우기
    } else {
        alert(`"${query}"를 포함하는 문제를 찾을 수 없습니다.`);
    }
}

// ========================================
// QUESTION JUMP BUTTONS
// ========================================
function createQuestionJumpButtons() {
    if (!elements.questionJumpButtons || !quizData) return;

    const totalQuestions = quizData.questions.length;
    const buttonInterval = 50;

    elements.questionJumpButtons.innerHTML = '';

    // 50문제 단위로 버튼 생성
    for (let i = 0; i < totalQuestions; i += buttonInterval) {
        const startNum = i + 1;

        const button = document.createElement('button');
        button.className = 'jump-btn';
        button.textContent = `Q${startNum}`;
        button.dataset.startIndex = i;

        button.addEventListener('click', () => {
            jumpToQuestion(i);
        });

        elements.questionJumpButtons.appendChild(button);
    }
}

function jumpToQuestion(index) {
    currentQuestionIndex = index;
    displayQuestion();
    updateUI();
    updateJumpButtonsState();
}

function updateJumpButtonsState() {
    if (!elements.questionJumpButtons) return;

    const buttons = elements.questionJumpButtons.querySelectorAll('.jump-btn');
    const currentQuestionId = shuffledQuestions[currentQuestionIndex]?.id;

    buttons.forEach(button => {
        const startIndex = parseInt(button.dataset.startIndex);
        const endIndex = startIndex + 50;

        // 현재 문제 ID가 이 버튼의 범위에 있는지 확인
        if (currentQuestionId >= startIndex + 1 && currentQuestionId <= endIndex) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
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

    // Update score (based on first attempts only)
    const scorePercentage = firstAttempts.size > 0 ? Math.round((score / firstAttempts.size) * 100) || 0 : 0;
    elements.scoreText.textContent = `${scorePercentage}%`;

    // Update navigation buttons
    elements.prevBtn.disabled = currentQuestionIndex === 0;
    elements.nextBtn.disabled = currentQuestionIndex === total - 1;

    // Update bookmark icon
    const isBookmarked = bookmarkedQuestions.has(question.id);
    elements.bookmarkIcon.textContent = isBookmarked ? '❤️' : '🤍';

    // Update jump buttons state
    updateJumpButtonsState();
}

// ========================================
// DRAG AND DROP QUESTION DISPLAY
// ========================================
function displayDragDropQuestion(question) {
    const container = elements.optionsContainer;

    // Main container
    const dragDropContainer = document.createElement('div');
    dragDropContainer.className = 'drag-drop-container';

    // Left panel - Drag Options
    const dragPanel = document.createElement('div');
    dragPanel.className = 'drag-options-panel';
    dragPanel.innerHTML = '<div class="drag-options-title">Answer Options</div>';

    question.dragOptions.forEach((option, index) => {
        const dragOption = document.createElement('div');
        dragOption.className = 'drag-option';
        dragOption.textContent = option;
        dragOption.draggable = true;
        dragOption.dataset.option = option;
        dragOption.dataset.index = index;

        // Drag events
        dragOption.addEventListener('dragstart', handleDragStart);
        dragOption.addEventListener('dragend', handleDragEnd);

        dragPanel.appendChild(dragOption);
    });

    // Right panel - Drop Zones
    const dropPanel = document.createElement('div');
    dropPanel.className = 'drop-zones-panel';
    dropPanel.innerHTML = '<div class="drop-zones-title">Answer Area</div>';

    question.dropZones.forEach((zone, index) => {
        const zoneRow = document.createElement('div');
        zoneRow.className = 'drop-zone-row';

        const description = document.createElement('div');
        description.className = 'drop-zone-description';
        description.textContent = zone.description;

        const dropZone = document.createElement('div');
        dropZone.className = 'drop-zone';
        dropZone.dataset.index = index;
        dropZone.dataset.correctAnswer = zone.correctAnswer;

        // Drop events
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('dragleave', handleDragLeave);
        dropZone.addEventListener('drop', handleDrop);

        zoneRow.appendChild(description);
        zoneRow.appendChild(dropZone);
        dropPanel.appendChild(zoneRow);
    });

    dragDropContainer.appendChild(dragPanel);
    dragDropContainer.appendChild(dropPanel);
    container.appendChild(dragDropContainer);

    // Submit button (항상 표시)
    const submitBtn = document.createElement('button');
    submitBtn.className = 'option-btn submit-btn submit-drag-drop-btn';
    submitBtn.textContent = firstAttempts.has(question.id) ? '다시 제출' : '제출';
    submitBtn.addEventListener('click', () => submitDragDropAnswer(question));
    container.appendChild(submitBtn);
}

let draggedElement = null;

function handleDragStart(e) {
    draggedElement = e.target;
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.innerHTML);
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    e.target.classList.add('drag-over');
    return false;
}

function handleDragLeave(e) {
    e.target.classList.remove('drag-over');
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    e.preventDefault();

    const dropZone = e.target.closest('.drop-zone');
    if (!dropZone || !draggedElement) return;

    dropZone.classList.remove('drag-over');

    // 이미 채워진 경우 기존 아이템 제거
    const existingItem = dropZone.querySelector('.dropped-item');
    if (existingItem) {
        existingItem.remove();
    }

    // 새 아이템 추가 (원본은 그대로 두고 복사본만 추가)
    const droppedItem = document.createElement('div');
    droppedItem.className = 'dropped-item';
    droppedItem.textContent = draggedElement.textContent;
    droppedItem.dataset.option = draggedElement.dataset.option;

    // 클릭하면 제거
    droppedItem.addEventListener('click', () => {
        droppedItem.remove();
        dropZone.classList.remove('filled');
    });

    dropZone.appendChild(droppedItem);
    dropZone.classList.add('filled');
    // draggedElement.classList.add('used'); // 중복 사용을 위해 주석 처리

    return false;
}

function submitDragDropAnswer(question) {
    const dropZones = document.querySelectorAll('.drop-zone');
    let correct = 0;
    let total = dropZones.length;

    // 모든 드롭존이 채워졌는지 확인
    let allFilled = true;
    const userAnswers = [];
    dropZones.forEach(zone => {
        const droppedItem = zone.querySelector('.dropped-item');
        if (!droppedItem) {
            allFilled = false;
            userAnswers.push(null);
        } else {
            userAnswers.push(droppedItem.dataset.option);
        }
    });

    if (!allFilled) {
        alert('모든 답변 영역을 채워주세요.');
        return;
    }

    // 정답 확인
    dropZones.forEach(zone => {
        const droppedItem = zone.querySelector('.dropped-item');
        const userAnswer = droppedItem ? droppedItem.dataset.option : '';
        const correctAnswer = zone.dataset.correctAnswer;

        // Remove previous styling
        zone.classList.remove('correct', 'incorrect');

        if (userAnswer === correctAnswer) {
            zone.classList.add('correct');
            correct++;
        } else {
            zone.classList.add('incorrect');
        }
    });

    // Track first attempt only
    if (!firstAttempts.has(question.id)) {
        firstAttempts.set(question.id, {
            isCorrect: correct === total,
            userAnswer: userAnswers
        });

        // Update score only on first attempt
        if (correct === total) {
            score++;
        }
    }

    // 점수 업데이트
    answeredQuestions.add(question.id);

    // 피드백 표시
    const firstAttempt = firstAttempts.get(question.id);
    let feedbackText = `${correct}/${total}개 정답`;

    // Add first attempt indicator if this is a re-attempt
    if (firstAttempt && JSON.stringify(firstAttempt.userAnswer) !== JSON.stringify(userAnswers)) {
        feedbackText += ` (처음 시도: ${firstAttempt.isCorrect ? '정답' : '오답'})`;
    }

    elements.feedbackContent.textContent = feedbackText;
    elements.quizExplanation.innerHTML = (question.explanation || '설명이 제공되지 않았습니다.').replace(/\n/g, '<br>');
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.className = 'quiz-feedback ' + (correct === total ? 'correct' : 'incorrect');

    updateUI();
}

// ========================================
// IMAGE MODAL (FULLSCREEN VIEW)
// ========================================
function setupImageModal() {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');

    // Close modal on click
    if (modal) {
        modal.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    });
}

function openImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');

    if (modal && modalImage) {
        modalImage.src = imageSrc;
        modal.classList.add('active');
    }
}

// Add click handler to question images
function addImageClickHandlers() {
    document.addEventListener('click', (e) => {
        if (e.target.closest('.question-image img')) {
            const img = e.target.closest('.question-image img');
            openImageModal(img.src);
        }
    });
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
setupImageModal();
addImageClickHandlers();
init();
