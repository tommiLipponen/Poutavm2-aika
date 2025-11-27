// MQTT Chat Client JavaScript
// Connects to MQTT broker via WebSocket and manages chat messages

let mqttClient = null;
let clientId = 'web_' + Math.random().toString(16).substr(2, 8);
let nickname = localStorage.getItem('mqtt_nickname') || '';

// DOM elements
const messagesContainer = document.getElementById('messages-container');
const messageInput = document.getElementById('message-input');
const nicknameInput = document.getElementById('nickname-input');
const sendButton = document.getElementById('send-button');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');

// Initialize nickname from localStorage
if (nickname) {
    nicknameInput.value = nickname;
}

// MQTT Configuration
const MQTT_BROKER_WS = `ws://${window.location.hostname}/mqtt`;
const MQTT_TOPIC = 'chat/messages';

function connectMQTT() {
    console.log('Connecting to MQTT broker:', MQTT_BROKER_WS);
    
    mqttClient = mqtt.connect(MQTT_BROKER_WS, {
        clientId: clientId,
        clean: true,
        reconnectPeriod: 5000
    });
    
    mqttClient.on('connect', function() {
        console.log('Connected to MQTT broker');
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Yhdistetty MQTT brokeriin';
        sendButton.disabled = false;
        
        // Subscribe to chat topic
        mqttClient.subscribe(MQTT_TOPIC, function(err) {
            if (!err) {
                console.log('Subscribed to', MQTT_TOPIC);
            } else {
                console.error('Subscription error:', err);
            }
        });
        
        // Load existing messages
        loadMessages();
        loadStats();
    });
    
    mqttClient.on('message', function(topic, payload) {
        try {
            const message = JSON.parse(payload.toString());
            displayMessage(message);
        } catch (e) {
            console.error('Error parsing message:', e);
        }
    });
    
    mqttClient.on('error', function(error) {
        console.error('MQTT error:', error);
        statusText.textContent = 'MQTT virhe: ' + error.message;
    });
    
    mqttClient.on('offline', function() {
        console.log('MQTT offline');
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'Ei yhteyttä - yritetään uudelleen...';
        sendButton.disabled = true;
    });
    
    mqttClient.on('reconnect', function() {
        console.log('Reconnecting to MQTT broker...');
        statusText.textContent = 'Yhdistetään uudelleen...';
    });
}

function sendMessage() {
    const message = messageInput.value.trim();
    const nick = nicknameInput.value.trim() || 'Anonyymi';
    
    if (!message || !mqttClient) return;
    
    // Validate input lengths (enforce limits)
    if (nick.length > 50) {
        alert('Nimimerkki liian pitkä (max 50 merkkiä)');
        return;
    }
    
    if (message.length > 500) {
        alert('Viesti liian pitkä (max 500 merkkiä)');
        return;
    }
    
    // Save nickname to localStorage
    localStorage.setItem('mqtt_nickname', nick);
    nickname = nick;
    
    const payload = {
        nickname: nick,
        text: message,
        clientId: clientId,
        timestamp: Date.now()
    };
    
    mqttClient.publish(MQTT_TOPIC, JSON.stringify(payload), { qos: 1 }, function(err) {
        if (err) {
            console.error('Publish error:', err);
        } else {
            messageInput.value = '';
            loadStats(); // Update statistics
        }
    });
}

function displayMessage(msg, append = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const timestamp = msg.timestamp ? new Date(msg.timestamp) : new Date();
    const today = new Date();
    const isToday = timestamp.toDateString() === today.toDateString();
    
    // Show date if message is from a different day
    let timeString;
    if (isToday) {
        timeString = timestamp.toLocaleTimeString('fi-FI', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    } else {
        timeString = timestamp.toLocaleString('fi-FI', { 
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    // Handle both 'message' (from API) and 'text' (from MQTT)
    const messageText = msg.message || msg.text || '';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">${escapeHtml(msg.nickname)}</span>
            <span class="message-time">${timeString}</span>
        </div>
        <div class="message-text">${escapeHtml(messageText)}</div>
    `;
    
    if (append) {
        messagesContainer.insertBefore(messageDiv, messagesContainer.firstChild);
    } else {
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

let messageOffset = 0;
let hasMoreMessages = true;

function loadMessages(append = false) {
    const limit = 50;
    fetch(`/mqtt-chat/api/messages?limit=${limit}&offset=${messageOffset}`)
        .then(response => response.json())
        .then(data => {
            if (!append) {
                messagesContainer.innerHTML = '';
                messageOffset = 0;
            }
            
            // Store current scroll position
            const oldScrollHeight = messagesContainer.scrollHeight;
            
            data.messages.forEach(msg => {
                displayMessage(msg, append);
            });
            
            // If appending, maintain scroll position
            if (append) {
                const newScrollHeight = messagesContainer.scrollHeight;
                messagesContainer.scrollTop = newScrollHeight - oldScrollHeight;
            }
            
            messageOffset += data.messages.length;
            
            // If we got fewer messages than limit, no more to load
            hasMoreMessages = data.messages.length === limit;
            
            // Update load more button visibility
            const loadMoreBtn = document.getElementById('load-more-btn');
            if (hasMoreMessages) {
                loadMoreBtn.style.display = 'inline-block';
            } else {
                loadMoreBtn.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error loading messages:', error);
        });
}

function loadStats() {
    fetch('/mqtt-chat/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-messages').textContent = data.total_messages || 0;
            document.getElementById('messages-today').textContent = data.messages_today || 0;
            document.getElementById('unique-users').textContent = data.unique_users || 0;
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

nicknameInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        messageInput.focus();
    }
});

// Load more button handler
document.getElementById('load-more-btn')?.addEventListener('click', function() {
    if (hasMoreMessages) {
        loadMessages(true);
    }
});

// Scroll to bottom button handler
const scrollToBottomBtn = document.getElementById('scroll-to-bottom-btn');
scrollToBottomBtn?.addEventListener('click', function() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    scrollToBottomBtn.style.display = 'none';
});

// Show/hide scroll to bottom button based on scroll position
messagesContainer?.addEventListener('scroll', function() {
    const isAtBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop <= messagesContainer.clientHeight + 50;
    if (scrollToBottomBtn) {
        scrollToBottomBtn.style.display = isAtBottom ? 'none' : 'inline-block';
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    connectMQTT();
    
    // Refresh stats every 30 seconds
    setInterval(loadStats, 30000);
});
