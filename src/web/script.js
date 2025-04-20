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
    
    function createUserMessage(message) {
        const template = userMessageTemplate.content.cloneNode(true);
        template.querySelector('.message-content p').textContent = message;
        return template;
    }
    
    function createBotMessage(message, sources) {
        const template = botMessageTemplate.content.cloneNode(true);
        template.querySelector('.message-content p').textContent = message;
        
        const sourcesList = template.querySelector('.sources ul');
        if (sources && sources.length > 0) {
            sources.forEach(source => {
                const li = document.createElement('li');
                li.textContent = source.content.substring(0, 100) + '...';
                sourcesList.appendChild(li);
            });
        } else {
            template.querySelector('.sources').style.display = 'none';
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
