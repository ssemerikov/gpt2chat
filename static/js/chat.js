class ChatApp {
    constructor() {
        this.conversationId = null;
        this.isProcessing = false;

        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            chatForm: document.getElementById('chatForm'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            newChatBtn: document.getElementById('newChatBtn'),
            statusIndicator: document.getElementById('statusIndicator'),
            charCount: document.getElementById('charCount'),
            temperatureSlider: document.getElementById('temperatureSlider'),
            temperatureValue: document.getElementById('temperatureValue'),
            maxLengthSlider: document.getElementById('maxLengthSlider'),
            maxLengthValue: document.getElementById('maxLengthValue')
        };

        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.checkHealth();
        await this.createNewConversation();
    }

    setupEventListeners() {
        this.elements.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        this.elements.newChatBtn.addEventListener('click', () => {
            this.createNewConversation();
        });

        this.elements.messageInput.addEventListener('input', (e) => {
            this.updateCharCount(e.target.value.length);
        });

        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.elements.temperatureSlider.addEventListener('input', (e) => {
            this.elements.temperatureValue.textContent = e.target.value;
        });

        this.elements.maxLengthSlider.addEventListener('input', (e) => {
            this.elements.maxLengthValue.textContent = e.target.value;
        });
    }

    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();

            if (data.status === 'healthy' && data.model_loaded) {
                this.setStatus('connected', 'Підключено');
            } else {
                this.setStatus('error', 'Помилка моделі');
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.setStatus('error', 'Помилка з\'єднання');
        }
    }

    setStatus(status, text) {
        const dot = this.elements.statusIndicator.querySelector('.status-dot');
        const statusText = this.elements.statusIndicator.querySelector('.status-text');

        dot.className = `status-dot ${status === 'connected' ? 'connected' : ''}`;
        statusText.textContent = text;
    }

    async createNewConversation() {
        try {
            const response = await fetch('/api/conversations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.conversationId = data.conversation_id;
                this.clearMessages();
                this.addSystemMessage('Новий чат створено. Почніть розмову!');
            }
        } catch (error) {
            console.error('Error creating conversation:', error);
            this.addSystemMessage('Помилка при створенні чату', 'error');
        }
    }

    async sendMessage() {
        if (this.isProcessing) return;

        const message = this.elements.messageInput.value.trim();

        if (!message) return;

        if (!this.conversationId) {
            await this.createNewConversation();
        }

        this.isProcessing = true;
        this.elements.sendBtn.disabled = true;
        this.elements.messageInput.disabled = true;

        // Додаємо повідомлення користувача
        this.addMessage('user', message);
        this.elements.messageInput.value = '';
        this.updateCharCount(0);

        // Показуємо індикатор завантаження
        const loadingId = this.showLoading();

        try {
            const response = await fetch(`/api/conversations/${this.conversationId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    temperature: parseFloat(this.elements.temperatureSlider.value),
                    max_length: parseInt(this.elements.maxLengthSlider.value)
                })
            });

            const data = await response.json();

            this.removeLoading(loadingId);

            if (data.success) {
                this.addMessage('assistant', data.response);
            } else {
                this.addSystemMessage('Помилка: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeLoading(loadingId);
            this.addSystemMessage('Помилка при відправці повідомлення', 'error');
        } finally {
            this.isProcessing = false;
            this.elements.sendBtn.disabled = false;
            this.elements.messageInput.disabled = false;
            this.elements.messageInput.focus();
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(contentDiv);

        // Видаляємо welcome message якщо є
        const welcomeMessage = this.elements.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(text, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'system-message';
        messageDiv.textContent = text;
        messageDiv.style.textAlign = 'center';
        messageDiv.style.color = type === 'error' ? 'var(--danger-color)' : 'var(--secondary-color)';
        messageDiv.style.fontSize = '14px';
        messageDiv.style.padding = '10px';

        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant';
        loadingDiv.id = 'loading-' + Date.now();

        const loadingContent = document.createElement('div');
        loadingContent.className = 'message-content message-loading';
        loadingContent.innerHTML = '<span></span><span></span><span></span>';

        loadingDiv.appendChild(loadingContent);
        this.elements.chatMessages.appendChild(loadingDiv);
        this.scrollToBottom();

        return loadingDiv.id;
    }

    removeLoading(loadingId) {
        const loadingDiv = document.getElementById(loadingId);
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    clearMessages() {
        this.elements.chatMessages.innerHTML = '';
    }

    updateCharCount(count) {
        this.elements.charCount.textContent = `${count} символів`;
    }

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
}

// Ініціалізація додатку
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
