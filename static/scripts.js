document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');
    const fileInput = document.getElementById('file-input');
    const aiProvider = document.getElementById('ai-provider');
    const chatMessages = document.getElementById('chat-messages');
    const loading = document.getElementById('loading');
    const notification = document.getElementById('notification');

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    // Send message on Enter (but not Shift+Enter)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send button click
    sendBtn.addEventListener('click', sendMessage);

    // Clear conversation
    clearBtn.addEventListener('click', clearConversation);

    // File upload
    fileInput.addEventListener('change', handleFileUpload);

    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage('user', message);
        
        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Show loading
        showLoading();
        
        // Send to backend
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                ai_provider: aiProvider.value
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showNotification('Error: ' + data.error, 'error');
            } else {
                // Add AI response to chat
                addMessage('assistant', data.response, data.provider);
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showNotification('Network error occurred', 'error');
        });
    }

    function addMessage(role, content, provider = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';
        
        let headerText = '';
        if (role === 'user') {
            headerText = 'You';
        } else if (role === 'assistant') {
            headerText = provider ? `${provider} Assistant` : 'AI Assistant';
        }
        
        messageHeader.innerHTML = `<span class="role">${headerText}</span>`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p>${formatMessage(content)}</p>`;
        
        messageDiv.appendChild(messageHeader);
        messageDiv.appendChild(messageContent);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMessage(message) {
        // Basic formatting - convert newlines to <br>
        return message.replace(/\n/g, '<br>');
    }

    function clearConversation() {
        if (confirm('Are you sure you want to clear the conversation?')) {
            fetch('/clear_conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                // Clear chat messages except system message
                const systemMessage = chatMessages.querySelector('.message.system');
                chatMessages.innerHTML = '';
                if (systemMessage) {
                    chatMessages.appendChild(systemMessage);
                }
                showNotification('Conversation cleared', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error clearing conversation', 'error');
            });
        }
    }

    function handleFileUpload() {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        showLoading();

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showNotification('Upload error: ' + data.error, 'error');
            } else {
                showNotification('File uploaded: ' + data.filename, 'success');
                
                // Add file upload message to chat
                addMessage('user', `📎 Uploaded file: ${data.filename}`);
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showNotification('Upload failed', 'error');
        })
        .finally(() => {
            // Clear file input
            fileInput.value = '';
        });
    }

    function showLoading() {
        loading.classList.remove('hidden');
    }

    function hideLoading() {
        loading.classList.add('hidden');
    }

    function showNotification(message, type = 'info') {
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 5000);
    }

    // AI provider change handler
    aiProvider.addEventListener('change', function() {
        const providerName = this.options[this.selectedIndex].text;
        showNotification(`Switched to ${providerName}`, 'info');
    });

    // Handle streaming responses (future enhancement)
    function handleStreamedResponse(response) {
        // This would be implemented for real-time streaming
        // Currently, responses are sent as complete messages
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            sendMessage();
        }
        
        // Escape to clear input
        if (e.key === 'Escape') {
            messageInput.value = '';
            messageInput.style.height = 'auto';
            messageInput.blur();
        }
    });

    // Initialize
    messageInput.focus();
    
    // Show welcome message based on available APIs
    checkAPIStatus();
    
    function checkAPIStatus() {
        // This could be enhanced to check API key validity
        const currentProvider = aiProvider.value;
        const providerName = aiProvider.options[aiProvider.selectedIndex].text;
        
        // You could add a health check endpoint to verify API keys
        console.log(`Using ${providerName} as AI provider`);
    }
});