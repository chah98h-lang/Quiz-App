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
    } else if (question.questionType === 'MULTIPLE_CHOICE_MULTI') {
        displayMultipleChoiceMultiQuestion(question);
    } else {
        // Create option buttons (일반 문제 - 단일/복수 선택)
        question.options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.textContent = `${option.letter}. ${option.text}`;
            button.dataset.letter = option.letter;

            // Check if already answered
            if (answeredQuestions.has(question.id)) {
                button.disabled = true;
                // 복수 정답 확인
                const correctAnswers = question.answer.includes('\n') || question.answer.includes(',') ? 
                    question.answer.split(/[\n,]/).map(a => a.trim()) : [question.answer];
                
                if (correctAnswers.includes(option.letter)) {
                    button.classList.add('correct');
                }
            } else {
                button.addEventListener('click', () => toggleSelection(button));
            }

            elements.optionsContainer.appendChild(button);
        });

        // 제출 버튼 추가 (아직 답변하지 않은 경우)
        if (!answeredQuestions.has(question.id)) {
            const submitBtn = document.createElement('button');
            submitBtn.className = 'option-btn submit-btn';
            submitBtn.textContent = '제출';
            submitBtn.addEventListener('click', () => submitMultipleChoice(question));
            elements.optionsContainer.appendChild(submitBtn);
        }
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
        <div class="hotspot-col-answer">Yes</div>
        <div class="hotspot-col-answer">No</div>
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
        yesInput.value = 'Yes';
        yesInput.id = `q${question.id}-s${index}-yes`;
        yesDiv.appendChild(yesInput);
        row.appendChild(yesDiv);
        
        // No 체크박스
        const noDiv = document.createElement('div');
        noDiv.className = 'hotspot-checkbox';
        const noInput = document.createElement('input');
        noInput.type = 'radio';
        noInput.name = `statement-${index}`;
        noInput.value = 'No';
        noInput.id = `q${question.id}-s${index}-no`;
        noDiv.appendChild(noInput);
        row.appendChild(noDiv);
        
        // 이미 답변한 경우 표시
        if (answeredQuestions.has(question.id)) {
            yesInput.disabled = true;
            noInput.disabled = true;
            
            const correctAnswer = question.answer[index];
            if (correctAnswer === 'Yes') {
                yesInput.checked = true;
                yesDiv.classList.add('correct-answer');
            } else {
                noInput.checked = true;
                noDiv.classList.add('correct-answer');
            }
        }
        
        table.appendChild(row);
    });
    
    container.appendChild(table);
    
    // 제출 버튼 (아직 답변하지 않은 경우)
    if (!answeredQuestions.has(question.id)) {
        const submitBtn = document.createElement('button');
        submitBtn.className = 'option-btn submit-hotspot-btn';
        submitBtn.textContent = '제출';
        submitBtn.addEventListener('click', () => submitHotspotAnswer(question));
        container.appendChild(submitBtn);
    }
}

function submitHotspotAnswer(question) {
    const userAnswers = [];
    let allAnswered = true;
    
    // 각 statement의 답변 수집
    question.statements.forEach((statement, index) => {
        const yesInput = document.getElementById(`q${question.id}-s${index}-yes`);
        const noInput = document.getElementById(`q${question.id}-s${index}-no`);
        
        if (yesInput.checked) {
            userAnswers.push('Yes');
        } else if (noInput.checked) {
            userAnswers.push('No');
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
    userAnswers.forEach((answer, index) => {
        if (answer === question.answer[index]) {
            correctCount++;
        }
    });
    
    const isCorrect = correctCount === question.statements.length;
    
    // 답변 표시
    answeredQuestions.add(question.id);
    if (isCorrect) score++;
    
    // UI 업데이트
    question.statements.forEach((statement, index) => {
        const row = document.querySelector(`.hotspot-row[data-index="${index}"]`);
        const yesDiv = row.querySelector('.hotspot-checkbox:nth-child(2)');
        const noDiv = row.querySelector('.hotspot-checkbox:nth-child(3)');
        const yesInput = document.getElementById(`q${question.id}-s${index}-yes`);
        const noInput = document.getElementById(`q${question.id}-s${index}-no`);
        
        yesInput.disabled = true;
        noInput.disabled = true;
        
        // 정답 표시
        const correctAnswer = question.answer[index];
        if (correctAnswer === 'Yes') {
            yesDiv.classList.add('correct-answer');
        } else {
            noDiv.classList.add('correct-answer');
        }
        
        // 오답 표시
        if (userAnswers[index] !== correctAnswer) {
            if (userAnswers[index] === 'Yes') {
                yesDiv.classList.add('wrong-answer');
            } else {
                noDiv.classList.add('wrong-answer');
            }
        }
    });
    
    // 제출 버튼 제거
    const submitBtn = document.querySelector('.submit-hotspot-btn');
    if (submitBtn) submitBtn.remove();
    
    // 피드백 표시
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);
    
    elements.feedbackContent.textContent = isCorrect ? 
        `✓ 정답입니다! (${correctCount}/${question.statements.length})` : 
        `✗ ${correctCount}/${question.statements.length}개 정답`;
    elements.quizExplanation.textContent = question.explanation || '설명이 제공되지 않았습니다.';
    
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
        
        // 이미 답변한 경우
        if (answeredQuestions.has(question.id)) {
            select.disabled = true;
            select.value = item.answer;
            if (select.value === item.answer) {
                selectDiv.classList.add('correct-answer');
            }
        }
        
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
    
    // 제출 버튼
    if (!answeredQuestions.has(question.id)) {
        const submitBtn = document.createElement('button');
        submitBtn.className = 'option-btn submit-matching-btn';
        submitBtn.textContent = '제출';
        submitBtn.addEventListener('click', () => submitMatchingAnswer(question));
        container.appendChild(submitBtn);
    }
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
    
    // 답변 표시
    answeredQuestions.add(question.id);
    if (isCorrect) score++;
    
    // UI 업데이트
    question.matchingItems.forEach((item, index) => {
        const select = document.getElementById(`matching-${index}`);
        const selectDiv = select.parentElement;
        
        select.disabled = true;
        
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
    
    // 제출 버튼 제거
    const submitBtn = document.querySelector('.submit-matching-btn');
    if (submitBtn) submitBtn.remove();
    
    // 피드백 표시
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);
    
    elements.feedbackContent.textContent = isCorrect ? 
        `✓ 정답입니다! (${correctCount}/${question.matchingItems.length})` : 
        `✗ ${correctCount}/${question.matchingItems.length}개 정답`;
    elements.quizExplanation.textContent = question.explanation || '설명이 제공되지 않았습니다.';
    
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
        
        // 이미 답변한 경우
        if (answeredQuestions.has(question.id)) {
            select.disabled = true;
            const correctAnswer = question.answer[dropdown.id];
            select.value = correctAnswer;
            
            if (select.value === correctAnswer) {
                dropdownDiv.classList.add('correct-answer');
            }
        }
        
        dropdownDiv.appendChild(select);
        dropdownContainer.appendChild(dropdownDiv);
    });
    
    container.appendChild(dropdownContainer);
    
    // 제출 버튼
    if (!answeredQuestions.has(question.id)) {
        const submitBtn = document.createElement('button');
        submitBtn.className = 'option-btn submit-dropdown-btn';
        submitBtn.textContent = '제출';
        submitBtn.addEventListener('click', () => submitDropdownAnswer(question));
        container.appendChild(submitBtn);
    }
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
    
    // 답변 표시
    answeredQuestions.add(question.id);
    if (isCorrect) score++;
    
    // UI 업데이트
    question.dropdowns.forEach((dropdown) => {
        const select = document.getElementById(`dropdown-${dropdown.id}`);
        const dropdownDiv = select.parentElement;
        
        select.disabled = true;
        
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
    
    // 제출 버튼 제거
    const submitBtn = document.querySelector('.submit-dropdown-btn');
    if (submitBtn) submitBtn.remove();
    
    // 피드백 표시
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);
    
    elements.feedbackContent.textContent = isCorrect ? 
        `✓ 정답입니다!` : 
        `✗ ${correctCount}/${totalCount}개 정답`;
    elements.quizExplanation.textContent = question.explanation || '설명이 제공되지 않았습니다.';
    
    updateUI();
}

// ========================================
// MULTIPLE CHOICE SELECTION (with submit button)
// ========================================
function toggleSelection(button) {
    // Toggle selected state
    button.classList.toggle('selected');
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
    if (question.answer.includes('\n')) {
        correctAnswers = question.answer.split('\n').map(a => a.trim()).filter(a => a.length === 1);
    } else if (question.answer.includes(',')) {
        correctAnswers = question.answer.split(',').map(a => a.trim()).filter(a => a.length === 1);
    } else {
        correctAnswers = [question.answer.trim()];
    }
    
    // Check if answer is correct
    const isCorrect = selectedLetters.length === correctAnswers.length &&
                      selectedLetters.every(letter => correctAnswers.includes(letter));
    
    // Mark as answered
    answeredQuestions.add(question.id);
    
    // Update score
    if (isCorrect) {
        score++;
    }
    
    // Disable all buttons and show correct answers
    const allButtons = elements.optionsContainer.querySelectorAll('.option-btn');
    allButtons.forEach(btn => {
        if (btn.classList.contains('submit-btn')) {
            btn.remove();
            return;
        }
        
        btn.disabled = true;
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
    elements.quizFeedback.classList.remove('hidden');
    elements.quizFeedback.classList.toggle('correct', isCorrect);
    elements.quizFeedback.classList.toggle('incorrect', !isCorrect);
    
    const correctCount = selectedLetters.filter(l => correctAnswers.includes(l)).length;
    elements.feedbackContent.textContent = isCorrect ? 
        '✓ 정답입니다!' : 
        `✗ ${correctCount}/${correctAnswers.length}개 정답`;
    elements.quizExplanation.textContent = question.explanation || '설명이 제공되지 않았습니다.';
    
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
