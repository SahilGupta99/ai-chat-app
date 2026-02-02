// DOM Elements
let chatMessages, questionInput, sendButton, loading, themeToggle, apiStatus;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    chatMessages = document.getElementById('chatMessages');
    questionInput = document.getElementById('questionInput');
    sendButton = document.getElementById('sendButton');
    loading = document.getElementById('loading');
    themeToggle = document.getElementById('themeToggle');
    apiStatus = document.getElementById('apiStatus');

    setupEventListeners();
    questionInput.focus();
});

function setupEventListeners() {
    // Auto-resize textarea
    questionInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Theme toggle
    themeToggle.addEventListener('click', toggleTheme);

    // Send button
    sendButton.addEventListener('click', sendMessage);

    // Enter key to send (but allow Shift+Enter for new line)
    questionInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    document.body.classList.toggle('light-mode');

    const icon = document.body.classList.contains('dark-mode') ? 'sun' : 'moon';
    themeToggle.innerHTML = `<i class="fas fa-${icon}"></i> ${icon === 'sun' ? 'Light' : 'Dark'} Mode`;
}

// Format markdown to HTML
function formatMarkdown(text) {
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: false,
            mangle: false
        });
        return marked.parse(text);
    }

    // Fallback if marked.js not loaded
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const icon = sender === 'ai' ? 'robot' : 'user';
    const name = sender === 'ai' ? 'AI Assistant' : 'You';

    // Format AI messages with markdown
    const content = sender === 'ai' ? formatMarkdown(text) : text;

    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <i class="fas fa-${icon}"></i> ${name}
            </div>
            <div class="message-text">${content}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message to backend
async function sendMessage() {
    const question = questionInput.value.trim();
    if (!question) return;

    // Add user message
    addMessage(question, 'user');

    // Clear and reset input
    questionInput.value = '';
    questionInput.style.height = 'auto';

    // Show loading
    loading.style.display = 'flex';

    try {
        // Send with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        const data = await response.json();

        if (data.success) {
            addMessage(data.response, 'ai');
            updateStatus(data);
        } else {
            addMessage('Error: ' + (data.error || 'Unknown error'), 'ai');
            apiStatus.textContent = 'Error';
            apiStatus.className = 'mock';
        }
    } catch (error) {
        handleNetworkError(error);
    } finally {
        loading.style.display = 'none';
    }
}

function updateStatus(data) {
    if (data.is_mock) {
        if (data.status === 'offline') {
            apiStatus.textContent = 'Offline Mode';
        } else if (data.status === 'timeout') {
            apiStatus.textContent = 'Slow Connection';
        } else {
            apiStatus.textContent = 'Demo Mode';
        }
        apiStatus.className = 'mock';
    } else {
        apiStatus.textContent = 'AI Assistant Online';
        apiStatus.className = 'real';
    }
}

function handleNetworkError(error) {
    if (error.name === 'AbortError') {
        addMessage('Request timeout. Please check your connection.', 'ai');
    } else {
        addMessage('Network error. Please check your connection.', 'ai');
    }
    apiStatus.textContent = 'Connection Error';
    apiStatus.className = 'mock';
}
