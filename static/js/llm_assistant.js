// LLM Assistant JavaScript for AI Assistant Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chat interface
    initializeLLMAssistant();
    
    // Configure agent settings modal
    const agentSettingsBtn = document.getElementById('agent-settings-btn');
    if (agentSettingsBtn) {
        agentSettingsBtn.addEventListener('click', function() {
            const agentSettingsModal = new bootstrap.Modal(document.getElementById('agentSettingsModal'));
            agentSettingsModal.show();
        });
    }
    
    // Temperature range display update
    const temperatureRange = document.getElementById('temperature-range');
    const temperatureValue = document.getElementById('temperature-value');
    if (temperatureRange && temperatureValue) {
        temperatureRange.addEventListener('input', function() {
            temperatureValue.textContent = this.value;
        });
    }
    
    // Save agent settings
    const saveAgentSettingsBtn = document.getElementById('save-agent-settings');
    if (saveAgentSettingsBtn) {
        saveAgentSettingsBtn.addEventListener('click', function() {
            saveAgentSettings();
            bootstrap.Modal.getInstance(document.getElementById('agentSettingsModal')).hide();
            showToast('Agent settings saved successfully', 'success');
        });
    }
    
    // Initialize file upload handlers
    initializeFileUpload();
    
    // Initialize web scraper form
    initializeWebScraper();
    
    // Event listeners for response handling
    // Socket.IO is currently not used, we'll process the response after fetch
});

// Initialize the LLM Assistant chat interface
function initializeLLMAssistant() {
    const sendPromptBtn = document.getElementById('send-prompt');
    const promptInput = document.getElementById('prompt-input');
    const chatMessages = document.getElementById('chat-messages');
    
    if (!sendPromptBtn || !promptInput || !chatMessages) return;
    
    // Send message when clicking the send button
    sendPromptBtn.addEventListener('click', function() {
        sendMessage();
    });
    
    // Send message when pressing Enter (but allow Shift+Enter for new lines)
    promptInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Keep focus on input when chat is clicked
    chatMessages.addEventListener('click', function() {
        promptInput.focus();
    });
}

// Send a message to the LLM
async function sendMessage() {
    const promptInput = document.getElementById('prompt-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendPromptBtn = document.getElementById('send-prompt');
    const agentType = document.getElementById('agent-selector').value;
    const useRag = document.getElementById('useRag').checked;
    
    if (!promptInput || !chatMessages || !sendPromptBtn) return;
    
    const prompt = promptInput.value.trim();
    if (!prompt) return;
    
    // Disable input while processing
    promptInput.disabled = true;
    sendPromptBtn.disabled = true;
    
    // Add user message to chat
    const messageId = Date.now().toString();
    appendUserMessage(prompt);
    
    // Add assistant message with loading indicator
    appendAssistantMessageLoading(messageId);
    
    // Clear input
    promptInput.value = '';
    
    try {
        // Prepare the fetch options
        const fetchOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                agent_type: agentType,
                use_rag: useRag,
                message_id: messageId,
                settings: getAgentSettings()
            })
        };
        
        // Send the request and get a stream response
        const response = await fetch('/api/llm/query', fetchOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Set up the EventSource for the stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        // Replace loading indicator with an empty paragraph
        const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
        if (messageElement) {
            const messageContent = messageElement.querySelector('.message-content');
            if (messageContent) {
                messageContent.innerHTML = '<p></p>';
            }
        }
        
        // Process the streaming response
        let buffer = '';
        let done = false;
        
        while (!done) {
            const { value, done: readerDone } = await reader.read();
            if (readerDone) {
                done = true;
                break;
            }
            
            // Decode the chunk
            buffer += decoder.decode(value, { stream: true });
            
            // Process complete SSE messages
            let lines = buffer.split('\n\n');
            buffer = lines.pop() || ''; // Keep the last incomplete chunk in the buffer
            
            for (const line of lines) {
                if (!line.trim() || !line.startsWith('data: ')) continue;
                
                const data = line.substring(6); // Remove 'data: ' prefix
                
                if (data === '[DONE]') {
                    done = true;
                    break;
                }
                
                try {
                    const parsed = JSON.parse(data);
                    
                    if (parsed.error) {
                        handleLLMError(parsed.error, messageId);
                        done = true;
                        break;
                    }
                    
                    if (parsed.text) {
                        appendResponseChunk(parsed.text, messageId);
                    }
                } catch (e) {
                    console.error('Error parsing streaming response:', e);
                }
            }
        }
        
        completeResponse(messageId);
    } catch (error) {
        handleLLMError(error.message, messageId);
    } finally {
        // Re-enable input
        promptInput.disabled = false;
        sendPromptBtn.disabled = false;
        promptInput.focus();
    }
}

// Append a user message to the chat
function appendUserMessage(text) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message user-message';
    messageElement.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Append an assistant message with loading indicator
function appendAssistantMessageLoading(messageId) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message assistant-message';
    messageElement.setAttribute('data-message-id', messageId);
    messageElement.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Append a chunk of response to an existing assistant message
function appendResponseChunk(text, messageId) {
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (!messageElement) return;
    
    const messageContent = messageElement.querySelector('.message-content');
    
    // If this is the first chunk, remove the typing indicator and add a <p>
    if (messageContent.querySelector('.typing-indicator')) {
        messageContent.innerHTML = '<p></p>';
    }
    
    const paragraph = messageContent.querySelector('p');
    if (paragraph) {
        // Apply formatting to the new text
        const formattedText = formatResponseText(text);
        
        // Append the new chunk to the existing text
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = formattedText;
        
        // Add a span with animation to the new text
        const span = document.createElement('span');
        span.className = 'streaming-text';
        span.innerHTML = tempDiv.innerHTML;
        
        paragraph.appendChild(span);
        
        // After animation completes, remove the span but keep the content
        setTimeout(() => {
            if (span.parentNode) {
                const content = span.innerHTML;
                span.insertAdjacentHTML('beforebegin', content);
                span.remove();
            }
        }, 300);
        
        scrollToBottom();
    }
}

// Mark a response as complete
function completeResponse(messageId) {
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (!messageElement) return;
    
    // The typing indicator should already be gone by now,
    // but let's ensure it's removed
    const typingIndicator = messageElement.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    
    scrollToBottom();
}

// Handle LLM error
function handleLLMError(errorMessage, messageId) {
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (!messageElement) return;
    
    const messageContent = messageElement.querySelector('.message-content');
    messageContent.innerHTML = `
        <p class="text-danger">
            <i class="fas fa-exclamation-triangle"></i> Error: ${escapeHtml(errorMessage)}
        </p>
    `;
    
    // Re-enable input fields
    const promptInput = document.getElementById('prompt-input');
    const sendPromptBtn = document.getElementById('send-prompt');
    
    if (promptInput) promptInput.disabled = false;
    if (sendPromptBtn) sendPromptBtn.disabled = false;
    
    scrollToBottom();
    showToast(errorMessage, 'danger');
}

// Scroll the chat to the bottom
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Initialize file upload functionality
function initializeFileUpload() {
    const documentUploadForm = document.getElementById('document-upload-form');
    
    if (documentUploadForm) {
        documentUploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('document-file');
            const descriptionInput = document.getElementById('document-description');
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showToast('Please select a file to upload', 'warning');
                return;
            }
            
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('document', file);
            
            if (descriptionInput.value) {
                formData.append('description', descriptionInput.value);
            }
            
            // Show loading toast
            showToast('Uploading document...', 'info');
            
            try {
                const response = await fetchWithTimeout('/api/rag/upload-document', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast('Document uploaded and indexed successfully', 'success');
                    
                    // Reset form
                    documentUploadForm.reset();
                    
                    // Add system message about the upload
                    const chatMessages = document.getElementById('chat-messages');
                    if (chatMessages) {
                        const messageElement = document.createElement('div');
                        messageElement.className = 'message system-message';
                        messageElement.innerHTML = `
                            <div class="message-content">
                                <p><i class="fas fa-file-upload"></i> Document "${escapeHtml(file.name)}" has been uploaded and indexed.</p>
                            </div>
                        `;
                        
                        chatMessages.appendChild(messageElement);
                        scrollToBottom();
                    }
                } else {
                    throw new Error(data.message || 'Failed to upload document');
                }
            } catch (error) {
                handleFetchError(error, 'upload document');
            }
        });
    }
}

// Initialize web scraper functionality
function initializeWebScraper() {
    const webScraperForm = document.getElementById('web-scraper-form');
    
    if (webScraperForm) {
        webScraperForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const urlInput = document.getElementById('webpage-url');
            const descriptionInput = document.getElementById('webpage-description');
            
            if (!urlInput.value.trim()) {
                showToast('Please enter a valid URL', 'warning');
                return;
            }
            
            // Show loading toast
            showToast('Scraping webpage...', 'info');
            
            try {
                const response = await fetchWithTimeout('/api/rag/scrape-webpage', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: urlInput.value.trim(),
                        description: descriptionInput.value.trim()
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast('Webpage scraped and indexed successfully', 'success');
                    
                    // Reset form
                    webScraperForm.reset();
                    
                    // Add system message about the scraping
                    const chatMessages = document.getElementById('chat-messages');
                    if (chatMessages) {
                        const messageElement = document.createElement('div');
                        messageElement.className = 'message system-message';
                        messageElement.innerHTML = `
                            <div class="message-content">
                                <p><i class="fas fa-globe"></i> Webpage "${escapeHtml(urlInput.value)}" has been scraped and indexed.</p>
                            </div>
                        `;
                        
                        chatMessages.appendChild(messageElement);
                        scrollToBottom();
                    }
                } else {
                    throw new Error(data.message || 'Failed to scrape webpage');
                }
            } catch (error) {
                handleFetchError(error, 'scrape webpage');
            }
        });
    }
}

// Get current agent settings
function getAgentSettings() {
    const temperature = document.getElementById('temperature-range')?.value || 0.7;
    const maxTokens = document.getElementById('max-tokens')?.value || 1024;
    const webSearch = document.getElementById('capability-web-search')?.checked || true;
    const codeExecution = document.getElementById('capability-code-execution')?.checked || true;
    const documentAnalysis = document.getElementById('capability-document-analysis')?.checked || true;
    
    return {
        temperature: parseFloat(temperature),
        max_tokens: parseInt(maxTokens),
        capabilities: {
            web_search: webSearch,
            code_execution: codeExecution,
            document_analysis: documentAnalysis
        }
    };
}

// Save agent settings
function saveAgentSettings() {
    const settings = getAgentSettings();
    
    // Store settings locally
    localStorage.setItem('agent_settings', JSON.stringify(settings));
    
    // Optionally send to server to save in user preferences
    fetch('/api/llm/save-agent-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    }).catch(error => {
        console.error('Error saving agent settings:', error);
    });
}
