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
        
        // Send to backend with improved error handling
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
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
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
            if (error.message.includes('HTTP 500')) {
                showNotification('Server error - please check API keys', 'error');
            } else {
                showNotification('Network error occurred', 'error');
            }
        });
    }

    function addMessage(role, content, provider = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';
        
        let headerText = '';
        const timestamp = new Date().toLocaleTimeString();
        
        if (role === 'user') {
            headerText = `You • ${timestamp}`;
        } else if (role === 'assistant') {
            headerText = `${provider ? provider : 'AI'} Assistant • ${timestamp}`;
        }
        
        messageHeader.innerHTML = `<span class="role">${headerText}</span>`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Add copy button for assistant messages
        if (role === 'assistant') {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.innerHTML = '📋';
            copyBtn.title = 'Copy message';
            copyBtn.onclick = () => copyToClipboard(content);
            messageHeader.appendChild(copyBtn);
        }
        
        messageContent.innerHTML = `<p>${formatMessage(content)}</p>`;
        
        messageDiv.appendChild(messageHeader);
        messageDiv.appendChild(messageContent);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Message copied to clipboard', 'success');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            showNotification('Failed to copy message', 'error');
        });
    }

    function formatMessage(message) {
        // Enhanced formatting - convert newlines to <br> and handle markdown-like formatting
        return message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
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
                const uploadMessage = `📎 Uploaded file: ${file.name}`;
                if (data.content_preview) {
                    addMessage('user', uploadMessage + '\n\nContent preview:\n' + data.content_preview);
                } else {
                    addMessage('user', uploadMessage);
                }
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
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                const { apis } = data;
                
                // Update UI based on API availability
                if (!apis.openai && !apis.gemini) {
                    showNotification('⚠️ No API keys configured. Please check your settings.', 'error');
                } else {
                    const available = [];
                    if (apis.openai) available.push('OpenAI');
                    if (apis.gemini) available.push('Gemini');
                    
                    // Filter AI provider options based on availability
                    updateAIProviderOptions(apis);
                    
                    console.log(`Available APIs: ${available.join(', ')}`);
                }
            })
            .catch(error => {
                console.error('Error checking API status:', error);
            });
    }
    
    function updateAIProviderOptions(apis) {
        const select = document.getElementById('ai-provider');
        const options = select.options;
        
        // Disable unavailable options
        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            if (option.value === 'openai' && !apis.openai) {
                option.disabled = true;
                option.text = 'OpenAI (GPT-3.5) - API Key Required';
            } else if (option.value === 'gemini' && !apis.gemini) {
                option.disabled = true;
                option.text = 'Google Gemini - API Key Required';
            }
        }
        
        // Select first available option
        if (!apis.openai && apis.gemini) {
            select.value = 'gemini';
        } else if (apis.openai && !apis.gemini) {
            select.value = 'openai';
        }
    }
});