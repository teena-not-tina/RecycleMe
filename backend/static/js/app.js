// 애플리케이션 전역 변수 및 상태
const API_BASE_URL = '/api';
let currentUser = null;
let authToken = null;
let lastClassificationResult = null;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 로컬 스토리지에서 사용자 상태 복원
    restoreUserState();
    
    // UI 이벤트 리스너 설정
    setupUIEventListeners();
    
    // 웹캠 초기화
    setupWebcam();
    
    // 파일 업로드 영역 초기화
    setupDropArea();
    
    // 챗봇 초기화
    setupChatbot();
    
    // 배지 추가: 개발 서버 표시
    addDevelopmentBadge();
});

// 사용자 상태 복원
function restoreUserState() {
    const savedUserData = localStorage.getItem('userData');
    const savedToken = localStorage.getItem('authToken');
    
    if (savedUserData && savedToken) {
        try {
            currentUser = JSON.parse(savedUserData);
            authToken = savedToken;
            updateUIForLoggedInUser();
            fetchUserPoints();
        } catch (error) {
            console.error('저장된 사용자 데이터 복원 실패:', error);
            logoutUser();
        }
    }
}

// UI 이벤트 리스너 설정
function setupUIEventListeners() {
    // 로그인 버튼
    document.getElementById('login-btn').addEventListener('click', () => {
        const loginModal = new bootstrap.Modal(document.getElementById('login-modal'));
        loginModal.show();
    });
    
    // 로그아웃 버튼
    document.getElementById('logout-btn').addEventListener('click', logoutUser);
    
    // 로그인 폼 제출
    document.getElementById('login-submit').addEventListener('click', handleLoginSubmit);
    
    // 회원가입 폼 제출
    document.getElementById('register-submit').addEventListener('click', handleRegisterSubmit);
    
    // 모달 전환 링크
    document.getElementById('switch-to-register').addEventListener('click', (e) => {
        e.preventDefault();
        const loginModal = bootstrap.Modal.getInstance(document.getElementById('login-modal'));
        loginModal.hide();
        const registerModal = new bootstrap.Modal(document.getElementById('register-modal'));
        registerModal.show();
    });
    
    document.getElementById('switch-to-login').addEventListener('click', (e) => {
        e.preventDefault();
        const registerModal = bootstrap.Modal.getInstance(document.getElementById('register-modal'));
        registerModal.hide();
        const loginModal = new bootstrap.Modal(document.getElementById('login-modal'));
        loginModal.show();
    });
    
    // 포인트 적립 버튼
    document.getElementById('earn-points').addEventListener('click', handleEarnPoints);
}

// 웹캠 설정
function setupWebcam() {
    const startCameraBtn = document.getElementById('start-camera');
    const stopCameraBtn = document.getElementById('stop-camera');
    const captureImageBtn = document.getElementById('capture-image');
    const webcamElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('canvas');
    
    let stream = null;
    
    startCameraBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' } 
            });
            webcamElement.srcObject = stream;
            
            startCameraBtn.classList.add('d-none');
            stopCameraBtn.classList.remove('d-none');
            captureImageBtn.classList.remove('d-none');
        } catch (error) {
            console.error('웹캠 접근 오류:', error);
            alert('카메라에 접근할 수 없습니다. 권한을 확인해주세요.');
        }
    });
    
    stopCameraBtn.addEventListener('click', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            webcamElement.srcObject = null;
            
            startCameraBtn.classList.remove('d-none');
            stopCameraBtn.classList.add('d-none');
            captureImageBtn.classList.add('d-none');
        }
    });
    
    captureImageBtn.addEventListener('click', () => {
        // 캔버스 준비
        const context = canvasElement.getContext('2d');
        canvasElement.width = webcamElement.videoWidth;
        canvasElement.height = webcamElement.videoHeight;
        context.drawImage(webcamElement, 0, 0, canvasElement.width, canvasElement.height);
        
        // 이미지 데이터 가져오기
        const imageData = canvasElement.toDataURL('image/jpeg');
        
        // 백엔드로 이미지 전송 및 분류
        classifyImage(imageData);
    });
}

// 드래그 앤 드롭 영역 설정
function setupDropArea() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-image');
    const clearBtn = document.getElementById('clear-image');
    const previewContainer = document.getElementById('image-preview');
    const previewImage = document.getElementById('preview-image');
    
    // 파일 입력창 클릭
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // 파일 선택 이벤트
    fileInput.addEventListener('change', handleFileSelect);
    
    // 드래그 앤 드롭 이벤트
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.add('highlight');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.remove('highlight');
        }, false);
    });
    
    dropArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            handleFileSelect();
        }
    });
    
    // 업로드 버튼 이벤트
    uploadBtn.addEventListener('click', () => {
        if (fileInput.files.length) {
            const file = fileInput.files[0];
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const imageData = e.target.result;
                classifyImage(imageData);
            };
            
            reader.readAsDataURL(file);
        }
    });
    
    // 지우기 버튼 이벤트
    clearBtn.addEventListener('click', () => {
        fileInput.value = '';
        previewImage.src = '';
        previewContainer.classList.add('d-none');
        uploadBtn.classList.add('d-none');
        clearBtn.classList.add('d-none');
    });
    
    function handleFileSelect() {
        if (fileInput.files.length) {
            const file = fileInput.files[0];
            
            // 이미지 파일 유효성 검사
            if (!file.type.match('image.*')) {
                alert('이미지 파일만 업로드 가능합니다.');
                fileInput.value = '';
                return;
            }
            
            // 이미지 미리보기
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewContainer.classList.remove('d-none');
                uploadBtn.classList.remove('d-none');
                clearBtn.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }
    }
}

// 챗봇 설정
function setupChatbot() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    
    // 시작 메시지 추가
    addBotMessage('안녕하세요! 재활용 분류 챗봇입니다. 무엇을 도와드릴까요?');
    addBotMessage('다음과 같은 질문을 할 수 있습니다:');
    addBotMessage('1. "신림로 430 건전지 수거함" - 주변 건전지 수거함 위치 검색');
    addBotMessage('2. "관악구 장롱 수수료" - 대형폐기물 수수료 조회');
    
    // 메시지 전송 이벤트
    sendButton.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
    
    function sendChatMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // 사용자 메시지 추가
            addUserMessage(message);
            chatInput.value = '';
            
            // 로딩 메시지 추가
            const loadingMessageId = addBotMessage('입력 중...', true);
            
            // 백엔드로 메시지 전송
            processChatMessage(message)
                .then(response => {
                    // 로딩 메시지 제거
                    removeMessage(loadingMessageId);
                    
                    // 응답에 따라 처리
                    if (response.type === 'battery_bins') {
                        // 건전지 수거함 결과 표시
                        addBotMessage(`"${response.query}" 검색 결과입니다:`);
                        response.results.forEach(bin => {
                            if (bin.message) {
                                addBotMessage(bin.message);
                            } else {
                                addBotMessage(`주소: ${bin.address}`);
                                addBotMessage(`위치: ${bin.location}`);
                                if (bin.opening_hours) {
                                    addBotMessage(`운영시간: ${bin.opening_hours}`);
                                }
                                addBotMessage('─────────────────');
                            }
                        });
                    } else if (response.type === 'waste_fees') {
                        // 폐기물 수수료 결과 표시
                        addBotMessage(`"${response.query}" 검색 결과입니다:`);
                        response.results.forEach(fee => {
                            if (fee.message) {
                                addBotMessage(fee.message);
                            } else {
                                addBotMessage(`지역: ${fee.region}`);
                                addBotMessage(`품목: ${fee.item}`);
                                addBotMessage(`규격: ${fee.specification}`);
                                addBotMessage(`수수료: ${fee.fee}`);
                                addBotMessage('─────────────────');
                            }
                        });
                    } else {
                        // 일반 메시지
                        addBotMessage(response.message || '죄송합니다. 요청을 처리할 수 없습니다.');
                    }
                })
                .catch(error => {
                    // 로딩 메시지 제거
                    removeMessage(loadingMessageId);
                    console.error('챗봇 요청 오류:', error);
                    addBotMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.');
                });
        }
    }
    
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message user-message';
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addBotMessage(message, isLoading = false) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message bot-message';
        if (isLoading) {
            messageElement.classList.add('loading');
        }
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return isLoading ? messageElement.id = `loading-${Date.now()}` : null;
    }
    
    function removeMessage(messageId) {
        if (messageId) {
            const messageElement = document.getElementById(messageId);
            if (messageElement) {
                messageElement.remove();
            }
        }
    }
}
// 이미지 분류 함수
async function classifyImage(imageData) {
    try {
        const resultCard = document.getElementById('result-card');
        resultCard.classList.add('d-none');
        
        // 로딩 표시
        showLoading(true);
        
        // 백엔드 연결이 없는 개발 환경에서는 모의 데이터로 테스트
        // 실제 환경에서는 이 부분이 백엔드 API와 통신하게 됩니다
        setTimeout(() => {
            showLoading(false);
            
            // 모의 분류 결과 생성
            const mockResult = generateMockClassificationResult();
            lastClassificationResult = mockResult;
            
            // 결과 표시
            displayClassificationResult(mockResult);
        }, 2000); // 2초 후 결과 표시 (로딩 시뮬레이션)
        
    } catch (error) {
        console.error('이미지 분류 오류:', error);
        showLoading(false);
        alert('이미지 분류 중 오류가 발생했습니다.');
    }
}

// 로딩 표시 함수
function showLoading(isLoading) {
    // 실제 구현에서는 로딩 인디케이터를 표시/숨김
    console.log(isLoading ? '로딩 중...' : '로딩 완료');
}

// 모의 분류 결과 생성
function generateMockClassificationResult() {
    // 랜덤하게 쓰레기 항목 생성
    const categories = ['plastic', 'paper', 'can', 'vinyl', 'glass', 'styrofoam', 'battery', 'bulky_waste', 'other'];
    const selectedCategories = [];
    
    // 1~5개 항목 랜덤 선택
    const itemCount = Math.floor(Math.random() * 5) + 1;
    
    for (let i = 0; i < itemCount; i++) {
        const randomCategory = categories[Math.floor(Math.random() * categories.length)];
        selectedCategories.push(randomCategory);
    }
    
    // 탐지 결과 생성
    const detections = selectedCategories.map(category => ({
        category: category,
        confidence: 0.7 + Math.random() * 0.3, // 70~100% 신뢰도
        box: {
            x1: Math.random() * 100,
            y1: Math.random() * 100,
            x2: 100 + Math.random() * 200,
            y2: 100 + Math.random() * 200
        }
    }));
    
    // 재활용 가능 항목 카운트
    const recyclableCategories = ['plastic', 'paper', 'can', 'vinyl', 'glass', 'styrofoam'];
    const recyclableCount = detections.filter(d => recyclableCategories.includes(d.category)).length;
    
    // 특수 메시지 생성
    const specialMessages = [];
    
    // 배터리 메시지
    if (detections.some(d => d.category === 'battery')) {
        specialMessages.push({
            type: 'battery',
            message: '건전지 수거함 위치가 궁금하시면 \'주소+ 건전지 수거함\'이라고 검색하세요',
            action: 'search_battery_bins'
        });
    }
    
    // 대형폐기물 메시지
    if (detections.some(d => d.category === 'bulky_waste' || d.category === 'other')) {
        specialMessages.push({
            type: 'other',
            message: '종량제 봉투를 사용하시거나 대형폐기물일 경우 \'관악구 장롱 수수료\'라고 검색하세요',
            action: 'search_waste_fees'
        });
    }
    
    // 포인트 메시지
    if (recyclableCount > 0) {
        specialMessages.push({
            type: 'points',
            message: `재활용 가능한 항목 ${recyclableCount}개가 감지되었습니다. 적립금을 적립하시겠습니까?`,
            points: recyclableCount * 10,
            action: 'add_points'
        });
    }
    
    return {
        result: {
            image_id: 'mock-image-' + Date.now(),
            detections: detections,
            timestamp: new Date().toISOString()
        },
        points_eligible: recyclableCount * 10,
        special_messages: specialMessages
    };
}

// 분류 결과 표시
function displayClassificationResult(data) {
    const result = data.result || data;
    const detections = result.detections || [];
    const pointsEligible = data.points_eligible || 0;
    const specialMessages = data.special_messages || [];
    
    // 결과 카드 표시
    const resultCard = document.getElementById('result-card');
    resultCard.classList.remove('d-none');
    
    // 탐지 결과 표시
    displayDetections(detections);
    
    // 포인트 정보 표시
    const pointsBadge = document.getElementById('points-badge');
    const earnPointsBtn = document.getElementById('earn-points');
    
    pointsBadge.textContent = pointsEligible;
    
    if (pointsEligible > 0 && currentUser) {
        earnPointsBtn.classList.remove('d-none');
    } else {
        earnPointsBtn.classList.add('d-none');
    }
    
    // 특수 메시지 표시
    displaySpecialMessages(specialMessages);
}

// 탐지 결과 표시
function displayDetections(detections) {
    const webcamResultsList = document.getElementById('webcam-detection-list');
    const uploadResultsList = document.getElementById('upload-detection-list');
    const classificationResult = document.getElementById('classification-result');
    
    // 활성 탭 확인
    const activeTab = document.querySelector('.tab-pane.active');
    const resultsList = activeTab.id === 'camera' ? webcamResultsList : uploadResultsList;
    
    // 결과 초기화
    webcamResultsList.innerHTML = '';
    uploadResultsList.innerHTML = '';
    classificationResult.innerHTML = '';
    
    if (detections.length === 0) {
        resultsList.innerHTML = '<p>탐지된 항목이 없습니다.</p>';
        classificationResult.innerHTML = '<p>탐지된 항목이 없습니다.</p>';
        return;
    }
    
    // 탐지 결과 카운트
    const categoryCounts = {};
    
    detections.forEach(detection => {
        const category = detection.category;
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    // 메인 결과 표시
    classificationResult.innerHTML = '<h5>탐지된 항목:</h5>';
    
    const resultTable = document.createElement('table');
    resultTable.className = 'table table-bordered';
    
    const tableHead = document.createElement('thead');
    tableHead.innerHTML = `
        <tr>
            <th>카테고리</th>
            <th>수량</th>
        </tr>
    `;
    resultTable.appendChild(tableHead);
    
    const tableBody = document.createElement('tbody');
    
    Object.keys(categoryCounts).forEach(category => {
        const row = document.createElement('tr');
        
        const categoryCell = document.createElement('td');
        categoryCell.textContent = getCategoryDisplayName(category);
        
        const countCell = document.createElement('td');
        countCell.textContent = categoryCounts[category];
        
        row.appendChild(categoryCell);
        row.appendChild(countCell);
        tableBody.appendChild(row);
    });
    
    resultTable.appendChild(tableBody);
    classificationResult.appendChild(resultTable);
    
    // 상세 결과 표시 (활성 탭에 따라)
    detections.forEach(detection => {
        const detectionItem = document.createElement('div');
        detectionItem.className = 'detection-item';
        
        const confidence = Math.round(detection.confidence * 100);
        const category = getCategoryDisplayName(detection.category);
        
        detectionItem.innerHTML = `
            <div>
                ${category}
                <span class="badge bg-info">${confidence}%</span>
            </div>
        `;
        
        resultsList.appendChild(detectionItem);
    });
    
    // 결과 컨테이너 표시
    if (activeTab.id === 'camera') {
        document.getElementById('webcam-results').classList.remove('d-none');
    } else {
        document.getElementById('upload-results').classList.remove('d-none');
    }
}

// 카테고리 표시명 반환 (한글화)
function getCategoryDisplayName(category) {
    const categoryMap = {
        'plastic': '플라스틱',
        'paper': '종이',
        'can': '캔',
        'vinyl': '비닐',
        'glass': '유리병',
        'styrofoam': '스티로폼',
        'battery': '건전지',
        'fluorescent': '형광등',
        'bulky_waste': '대형폐기물',
        'other': '기타'
    };
    
    return categoryMap[category] || category;
}

// 특수 메시지 표시
function displaySpecialMessages(messages) {
    const specialMessagesContainer = document.getElementById('special-messages');
    specialMessagesContainer.innerHTML = '';
    
    if (messages.length === 0) return;
    
    messages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.className = `special-message ${message.type}`;
        
        const messageText = document.createElement('p');
        messageText.textContent = message.message;
        messageElement.appendChild(messageText);
        
        // 건전지/기타 쓰레기 메시지에 챗봇 링크 추가
        if (message.type === 'battery' || message.type === 'other') {
            const chatbotLink = document.createElement('a');
            chatbotLink.href = '#';
            chatbotLink.textContent = '챗봇에서 자세히 알아보기';
            chatbotLink.className = 'btn btn-sm btn-outline-primary mt-2';
            chatbotLink.addEventListener('click', (e) => {
                e.preventDefault();
                // 챗봇 탭으로 전환
                const tabEl = document.querySelector('#chatbot-tab');
                const tab = new bootstrap.Tab(tabEl);
                tab.show();
                
                // 챗봇 입력창에 자동 입력
                const chatInput = document.getElementById('chat-input');
                if (message.type === 'battery') {
                    chatInput.value = '신림로 430 건전지 수거함';
                } else {
                    chatInput.value = '관악구 장롱 수수료';
                }
            });
            messageElement.appendChild(chatbotLink);
        }
        
        specialMessagesContainer.appendChild(messageElement);
    });
}

// 포인트 적립 처리
async function handleEarnPoints() {
    if (!currentUser || !lastClassificationResult) return;
    
    // 개발 환경에서는 모의 적립 처리
    const pointsEarned = lastClassificationResult.points_eligible || 0;
    
    // 포인트 적립 효과
    currentUser.points = (parseInt(currentUser.points) || 0) + pointsEarned;
    
    // 로컬 스토리지 업데이트
    localStorage.setItem('userData', JSON.stringify(currentUser));
    
    // UI 업데이트
    document.getElementById('user-points').textContent = currentUser.points;
    
    // 포인트 내역 업데이트
    addMockPointTransaction({
        id: 'mock-transaction-' + Date.now(),
        description: '재활용 항목 적립',
        amount: pointsEarned,
        created_at: new Date()
    });
    
    // 성공 메시지
    alert(`${pointsEarned} 포인트가 적립되었습니다!`);
    
    // 적립 버튼 비활성화
    document.getElementById('earn-points').classList.add('d-none');
}

// 모의 포인트 트랜잭션 추가
function addMockPointTransaction(transaction) {
    // 로컬 스토리지에서 트랜잭션 목록 가져오기
    let transactions = JSON.parse(localStorage.getItem('mockTransactions')) || [];
    
    // 새 트랜잭션 추가
    transactions.unshift(transaction);
    
    // 로컬 스토리지에 저장
    localStorage.setItem('mockTransactions', JSON.stringify(transactions));
    
    // 포인트 내역 UI 업데이트
    displayMockPointsHistory();
}

// 로그인 처리
async function handleLoginSubmit() {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        alert('이메일과 비밀번호를 모두 입력해주세요.');
        return;
    }
    
    try {
        // 개발 환경에서는 간단한 로그인 처리 (모의 데이터)
        // 실제 환경에서는 이 부분에 실제 API 호출 코드가 들어갑니다.
        const mockUser = {
            id: '123456',
            email: email,
            display_name: email.split('@')[0],
            points: 100
        };
        
        currentUser = mockUser;
        authToken = 'mock-token-' + Date.now();
        
        // 로컬 스토리지에 저장
        localStorage.setItem('userData', JSON.stringify(currentUser));
        localStorage.setItem('authToken', authToken);
        
        // UI 업데이트
        updateUIForLoggedInUser();
        
        // 모달 닫기
        const loginModal = bootstrap.Modal.getInstance(document.getElementById('login-modal'));
        loginModal.hide();
        
        alert('개발 환경에서 로그인되었습니다. 실제 백엔드에 연결되지 않았습니다.');
        
    } catch (error) {
        console.error('로그인 오류:', error);
        alert('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.');
    }
}

// 회원가입 처리
async function handleRegisterSubmit() {
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const displayName = document.getElementById('display-name').value.trim();
    
    if (!email || !password) {
        alert('이메일과 비밀번호를 모두 입력해주세요.');
        return;
    }
    
    try {
        // 개발 환경에서는 간단한 회원가입 처리 (모의 데이터)
        // 실제 환경에서는 이 부분에 실제 API 호출 코드가 들어갑니다.
        const mockUser = {
            id: '123456',
            email: email,
            display_name: displayName || email.split('@')[0],
            points: 0
        };
        
        currentUser = mockUser;
        authToken = 'mock-token-' + Date.now();
        
        // 로컬 스토리지에 저장
// 로컬 스토리지에 저장
        localStorage.setItem('userData', JSON.stringify(currentUser));
        localStorage.setItem('authToken', authToken);
        
        // UI 업데이트
        updateUIForLoggedInUser();
        
        // 모달 닫기
        const registerModal = bootstrap.Modal.getInstance(document.getElementById('register-modal'));
        registerModal.hide();
        
        alert('개발 환경에서 회원가입되었습니다. 실제 백엔드에 연결되지 않았습니다.');
        
    } catch (error) {
        console.error('회원가입 오류:', error);
        alert('회원가입에 실패했습니다. 다시 시도해주세요.');
    }
}

// 로그아웃 처리
function logoutUser() {
    // 상태 초기화
    currentUser = null;
    authToken = null;
    lastClassificationResult = null;
    
    // 로컬 스토리지 데이터 삭제
    localStorage.removeItem('userData');
    localStorage.removeItem('authToken');
    
    // UI 업데이트
    updateUIForLoggedOutUser();
    
    // 결과 카드 숨기기
    document.getElementById('result-card').classList.add('d-none');
}

// 로그인 사용자 UI 업데이트
function updateUIForLoggedInUser() {
    if (!currentUser) return;
    
    // 사용자 정보 패널 업데이트
    document.getElementById('user-info').classList.add('d-none');
    document.getElementById('logged-in-user').classList.remove('d-none');
    
    document.getElementById('user-name').textContent = currentUser.display_name || '사용자';
    document.getElementById('user-email').textContent = currentUser.email || '';
    document.getElementById('user-points').textContent = currentUser.points || '0';
    
    // 포인트 내역 패널 초기화
    displayMockPointsHistory();
}

// 로그아웃 사용자 UI 업데이트
function updateUIForLoggedOutUser() {
    // 사용자 정보 패널 업데이트
    document.getElementById('user-info').classList.remove('d-none');
    document.getElementById('logged-in-user').classList.add('d-none');
    
    // 포인트 내역 패널 초기화
    document.getElementById('points-history').innerHTML = '<p class="text-muted">로그인 후 포인트 내역을 확인하세요.</p>';
}

// 사용자 포인트 정보 가져오기
function fetchUserPoints() {
    // 개발 환경에서는 포인트 내역을 모의 데이터로 표시합니다
    displayMockPointsHistory();
}

// 모의 포인트 내역 표시
function displayMockPointsHistory() {
    const historyContainer = document.getElementById('points-history');
    historyContainer.innerHTML = '';
    
    // 로컬 스토리지에서 트랜잭션 가져오기
    let transactions = JSON.parse(localStorage.getItem('mockTransactions')) || [];
    
    // 트랜잭션이 없으면 기본 데이터 생성
    if (transactions.length === 0) {
        // 모의 포인트 트랜잭션 데이터
        transactions = [
            {
                id: '1',
                description: '재활용 항목 적립',
                amount: 30,
                created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() // 어제
            },
            {
                id: '2',
                description: '재활용 항목 적립',
                amount: 20,
                created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString() // 3일 전
            },
            {
                id: '3',
                description: '포인트 사용: 에코백 교환',
                amount: -50,
                created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString() // 1주일 전
            }
        ];
        
        // 로컬 스토리지에 저장
        localStorage.setItem('mockTransactions', JSON.stringify(transactions));
    }
    
    if (transactions.length === 0) {
        historyContainer.innerHTML = '<p class="text-muted">포인트 내역이 없습니다.</p>';
        return;
    }
    
    transactions.forEach(transaction => {
        const item = document.createElement('div');
        item.className = 'points-transaction';
        
        const amount = transaction.amount;
        const isPositive = amount > 0;
        const formattedAmount = isPositive ? `+${amount}` : amount;
        const formattedDate = new Date(transaction.created_at).toLocaleDateString();
        
        item.innerHTML = `
            <div class="d-flex justify-content-between">
                <div>${transaction.description}</div>
                <div class="transaction-amount ${isPositive ? 'positive' : 'negative'}">${formattedAmount}</div>
            </div>
            <div class="text-muted small">${formattedDate}</div>
        `;
        
        historyContainer.appendChild(item);
    });
}

// 챗봇 메시지 처리
async function processChatMessage(message) {
    // 개발 환경에서 모의 응답 생성
    return new Promise((resolve) => {
        // 응답 지연 시뮬레이션 (1초)
        setTimeout(() => {
            if (message.includes('건전지 수거함')) {
                // 주소 추출 (주소 + 건전지 수거함 형식)
                const address = message.replace('건전지 수거함', '').trim();
                
                // 모의 건전지 수거함 데이터
                resolve({
                    type: 'battery_bins',
                    query: message,
                    results: [
                        {
                            address: address || '신림로 430',
                            location: '관악구청 1층 로비',
                            opening_hours: '09:00-18:00'
                        },
                        {
                            address: address ? `${address} 인근` : '신림로 3',
                            location: '신림역 지하상가 입구',
                            opening_hours: '06:00-24:00'
                        },
                        {
                            address: address ? `${address} 인근` : '신림동 1423-15',
                            location: '신림동주민센터 앞',
                            opening_hours: '24시간'
                        }
                    ]
                });
            } else if (message.includes('수수료')) {
                // 지역 및 품목 추출 (지역 품목 수수료 형식)
                const parts = message.replace('수수료', '').trim().split(' ');
                const region = parts[0] || '관악구';
                const item = parts[1] || '장롱';
                
                // 모의 수수료 데이터
                resolve({
                    type: 'waste_fees',
                    query: message,
                    results: [
                        {
                            region: region,
                            item: item,
                            specification: '1명용',
                            fee: '6,000원'
                        },
                        {
                            region: region,
                            item: item,
                            specification: '2명용',
                            fee: '8,000원'
                        },
                        {
                            region: region,
                            item: item,
                            specification: '3명용',
                            fee: '10,000원'
                        },
                        {
                            region: region,
                            item: item,
                            specification: '4명용 이상',
                            fee: '15,000원'
                        }
                    ]
                });
            } else {
                // 기타 메시지에 대한 기본 응답
                resolve({
                    type: 'general',
                    message: '안녕하세요! 재활용 분류 챗봇입니다. 다음과 같은 질문을 할 수 있습니다:\n\n1. "[주소] 건전지 수거함" - 주변 건전지 수거함 위치 검색\n2. "[지역] [품목] 수수료" - 대형폐기물 수수료 조회'
                });
            }
        }, 1000);
    });
}

// 개발 환경 배지 추가
function addDevelopmentBadge() {
    const badge = document.createElement('div');
    badge.style.position = 'fixed';
    badge.style.bottom = '10px';
    badge.style.right = '10px';
    badge.style.backgroundColor = 'rgba(255, 0, 0, 0.7)';
    badge.style.color = 'white';
    badge.style.padding = '5px 10px';
    badge.style.borderRadius = '5px';
    badge.style.fontSize = '12px';
    badge.style.zIndex = '9999';
    badge.textContent = '개발 환경 (백엔드 연결 없음)';
    
    document.body.appendChild(badge);
}