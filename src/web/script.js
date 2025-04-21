document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing chat UI');
    
    const messagesContainer = document.getElementById('messages-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const userMessageTemplate = document.getElementById('user-message-template');
    const botMessageTemplate = document.getElementById('bot-message-template');
    
    let currentConversationId = null;
    
    updateSendButtonState();
    messageInput.focus();
    
    messageInput.addEventListener('input', function() {
        console.log('Input event triggered, value:', messageInput.value);
        updateSendButtonState();
        
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
    
    sendButton.addEventListener('click', function() {
        console.log('Send button clicked');
        sendMessage();
    });
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    function updateSendButtonState() {
        sendButton.disabled = !messageInput.value.trim();
    }
    
    function formatBotMessage(message) {
        if (!message) return '';
        
        if (message.toLowerCase().includes('hello') || message.toLowerCase().includes('hi')) {
            message = '👋 ' + message;
        } else if (message.toLowerCase().includes('thank')) {
            message = '🙏 ' + message;
        } else if (message.toLowerCase().includes('error') || message.toLowerCase().includes('sorry')) {
            message = '❗ ' + message;
        } else if (message.toLowerCase().includes('successful') || message.toLowerCase().includes('complete')) {
            message = '✅ ' + message;
        } else {
            message = '🤖 ' + message;
        }
        
        message = message.replace(/(\d+\.\s)([^\n]+)/g, (match, number, content) => {
            let emoji = '•';
            if (content.toLowerCase().includes('step')) emoji = '🔄';
            else if (content.toLowerCase().includes('install')) emoji = '📥';
            else if (content.toLowerCase().includes('create')) emoji = '✨';
            else if (content.toLowerCase().includes('update')) emoji = '🔄';
            else if (content.toLowerCase().includes('delete')) emoji = '🗑️';
            else if (content.toLowerCase().includes('add')) emoji = '➕';
            else if (content.toLowerCase().includes('remove')) emoji = '➖';
            else if (content.toLowerCase().includes('fix')) emoji = '🔧';
            else if (content.toLowerCase().includes('test')) emoji = '🧪';
            else emoji = '•';
            
            return `<br>${emoji} ${content}<br>`;
        });
        
        message = message.replace(/(-|\*)\s([^\n]+)/g, (match, bullet, content) => {
            let emoji = '•';
            if (content.toLowerCase().includes('step')) emoji = '🔄';
            else if (content.toLowerCase().includes('install')) emoji = '📥';
            else if (content.toLowerCase().includes('create')) emoji = '✨';
            else if (content.toLowerCase().includes('update')) emoji = '🔄';
            else if (content.toLowerCase().includes('delete')) emoji = '🗑️';
            else if (content.toLowerCase().includes('add')) emoji = '➕';
            else if (content.toLowerCase().includes('remove')) emoji = '➖';
            else if (content.toLowerCase().includes('fix')) emoji = '🔧';
            else if (content.toLowerCase().includes('test')) emoji = '🧪';
            else emoji = '•';
            
            return `<br>${emoji} ${content}<br>`;
        });
        
        message = message.replace(/(\d{1,2}\/\d{1,2}\/\d{2,4}|\d{4}-\d{2}-\d{2})/g, '📅 $1');
        
        message = message.replace(/\n/g, '<br>');
        
        return message;
    }
    
    function createUserMessage(message) {
        const template = userMessageTemplate.content.cloneNode(true);
        template.querySelector('.message-content p').textContent = message;
        return template;
    }
    
    function createBotMessage(message, sources) {
        const template = botMessageTemplate.content.cloneNode(true);
        template.querySelector('p').innerHTML = formatBotMessage(message);
        const sourcesDiv = template.querySelector('.sources');
        const sourcesList = sourcesDiv.querySelector('ul');
        const sourcesHeader = sourcesDiv.querySelector('h4');
        if (sources && sources.length > 0) {
            // Replace the Sources: header with the toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.textContent = 'Show Sources';
            toggleBtn.className = 'toggle-sources-btn';
            let expanded = false;
            sourcesList.style.display = 'none';
            // Remove the static Sources: header
            if (sourcesHeader) sourcesHeader.remove();
            toggleBtn.addEventListener('click', () => {
                expanded = !expanded;
                sourcesList.style.display = expanded ? 'block' : 'none';
                toggleBtn.textContent = expanded ? 'Hide Sources' : 'Show Sources';
            });
            sourcesDiv.insertBefore(toggleBtn, sourcesList);
            // Add sources as list items (initially hidden)
            sources.forEach((source, idx) => {
                const li = document.createElement('li');
                li.innerHTML = `📄 <b>Source ${idx + 1}</b>: ${source.content.substring(0, 100)}...`;
                // Optionally: add full source as expandable/collapsible text
                if (source.content.length > 100) {
                    const expandBtn = document.createElement('button');
                    expandBtn.textContent = 'Expand';
                    expandBtn.className = 'expand-source-btn';
                    let expandedSource = false;
                    const fullContent = document.createElement('div');
                    fullContent.style.display = 'none';
                    fullContent.style.marginTop = '0.5em';
                    fullContent.style.background = '#f3f3f3';
                    fullContent.style.padding = '0.5em';
                    fullContent.style.borderRadius = '5px';
                    fullContent.textContent = source.content;
                    expandBtn.addEventListener('click', () => {
                        expandedSource = !expandedSource;
                        fullContent.style.display = expandedSource ? 'block' : 'none';
                        expandBtn.textContent = expandedSource ? 'Collapse' : 'Expand';
                    });
                    li.appendChild(expandBtn);
                    li.appendChild(fullContent);
                }
                sourcesList.appendChild(li);
            });
        } else {
            sourcesDiv.style.display = 'none';
        }
        setupFeedbackButtons(template);
        return template;
    }
    
    function setupFeedbackButtons(template) {
        const feedbackButtons = template.querySelectorAll('.feedback-button');
        feedbackButtons.forEach(button => {
            button.addEventListener('click', async () => {
                if (button.classList.contains('selected')) return;
                
                feedbackButtons.forEach(b => b.classList.remove('selected'));
                button.classList.add('selected');
                
                try {
                    let feedbackUrl = 'http://localhost:8000/chat/feedback';
                    console.log('Sending feedback to:', feedbackUrl);
                    
                    await fetch(feedbackUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            conversation_id: currentConversationId,
                            message_idx: -1, // Latest message
                            feedback: button.dataset.value
                        }),
                        mode: 'cors'
                    });
                } catch (error) {
                    console.error('Error sending feedback:', error);
                }
            });
        });
    }
    
    async function sendMessage() {
        console.log('sendMessage function called');
        const message = messageInput.value.trim();
        
        if (!message) {
            console.log('Message is empty, not sending');
            return;
        }
        
        console.log('Message to send:', message);
        
        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendButton.disabled = true;
        
        const userMessageNode = createUserMessage(message);
        messagesContainer.appendChild(userMessageNode);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        console.log('User message added to UI');
        
        try {
            const apiUrl = 'http://localhost:8000/chat/send';
            console.log('Sending message to API:', apiUrl);
            console.log('Request payload:', JSON.stringify({
                message: message,
                conversation_id: currentConversationId
            }));
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: currentConversationId
                }),
                mode: 'cors'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Received response:', data);
            
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
                console.log('Conversation ID updated:', currentConversationId);
            }
            
            const botMessageNode = createBotMessage(data.response, data.sources || []);
            messagesContainer.appendChild(botMessageNode);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to send message. Please try again.');
        } finally {
            updateSendButtonState();
        }
    }
    
    window.sendMessage = sendMessage;
});
