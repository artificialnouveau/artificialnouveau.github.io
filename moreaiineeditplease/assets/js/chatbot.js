/**
 * AI Service Advisor Chatbot
 * Helps users find the right AI services for their needs
 */

// ============================================
// Chatbot State
// ============================================

const ChatbotState = {
    isOpen: false,
    messages: []
};

// ============================================
// Service Recommendations Database
// ============================================

const ServiceRecommendations = {
    // Keywords mapped to service recommendations
    keywords: {
        // Social situations
        'social': ['Razer Project AVA', 'Social Battery Monitor', 'AI Dating Profile Writer', 'Rent-a-Human'],
        'awkward': ['GoveeLife Smart Ice Maker', 'Auto-Sorry Bot', 'AI Dating Profile Writer', 'Social Battery Monitor'],
        'conversation': ['AI Dating Profile Writer', 'MoltMatch Dating AI', 'AI Customer Service'],
        'friends': ['Rent-a-Human', 'Text Back Timer', 'Razer Project AVA'],
        'party': ['Social Battery Monitor', 'Excuse Generator Pro', 'Razer Project AVA'],
        'introvert': ['Social Battery Monitor', 'Excuse Generator Pro', 'Replika AI Companion'],
        'shy': ['MoltMatch Dating AI', 'Confidence Boost Sessions', 'Personal Hype Person'],
        'networking': ['AI Dating Profile Writer', 'AI Politician', 'Self-Esteem Projector'],
        'small talk': ['AI Dating Profile Writer', 'AI Customer Service', 'Razer Project AVA'],

        // Emotional support
        'confidence': ['Confidence Boost Sessions', 'Personal Hype Person', 'Imposter Syndrome Fighter'],
        'sad': ['Replika AI Companion', 'Victory Lap Narrator', 'Confidence Boost Sessions'],
        'anxious': ['AI Fortune Teller', 'Replika AI Companion', 'DoNotPay "AI Lawyer"'],
        'stressed': ['AI Fortune Teller', 'Replika AI Companion', 'Time Perception Adjuster'],
        'motivated': ['Personal Hype Person', 'Victory Lap Narrator', 'Difficulty Level Changer'],
        'depressed': ['Replika AI Companion', 'Victory Lap Narrator', 'AI Fortune Teller'],
        'lonely': ['Replika AI Companion', 'Razer Project AVA', 'Rent-a-Human'],
        'overwhelmed': ['AI Fortune Teller', 'Time Perception Adjuster', 'Social Battery Monitor'],
        'insecure': ['Self-Esteem Projector', 'Imposter Syndrome Fighter', 'Compliment Amplifier'],
        'jealous': ['AI Fortune Teller', 'Compliment Amplifier', 'Memory Editor'],
        'angry': ['AI Fortune Teller', 'Sleep Arguments Winner', 'Replika AI Companion'],

        // Productivity & Work
        'productive': ['Time Perception Adjuster', 'Procrastination Optimizer', 'Difficulty Level Changer'],
        'work': ['Time Perception Adjuster', 'AI Politician', 'MoltMatch Dating AI'],
        'meeting': ['AI Politician', 'Personal Hype Person', 'GoveeLife Smart Ice Maker'],
        'procrastinate': ['Procrastination Optimizer', 'Difficulty Level Changer', 'Personal Hype Person'],
        'lazy': ['Procrastination Optimizer', 'Personal Hype Person', 'Difficulty Level Changer'],
        'boring': ['Time Perception Adjuster', 'Procrastination Optimizer', 'Main Character Syndrome AI'],
        'focus': ['Time Perception Adjuster', 'DoNotPay "AI Lawyer"', 'Procrastination Optimizer'],
        'boss': ['AI Politician', 'MoltMatch Dating AI', 'Sleep Arguments Winner'],
        'interview': ['MoltMatch Dating AI', 'Personal Hype Person', 'AI Actress'],
        'presentation': ['Personal Hype Person', 'AI Actress', 'Confidence Boost Sessions'],
        'job': ['MoltMatch Dating AI', 'AI Politician', 'Self-Esteem Projector'],

        // Apologies & Conflict
        'sorry': ['Auto-Sorry Bot', 'Excuse Generator Pro', 'AI Politician'],
        'apology': ['Demand Apology AI', 'Auto-Sorry Bot', 'AI Politician'],
        'argue': ['Sleep Arguments Winner', 'AI Politician', 'AI Fortune Teller'],
        'fight': ['Sleep Arguments Winner', 'AI Politician', 'Compliment Amplifier'],
        'conflict': ['AI Politician', 'AI Fortune Teller', 'MoltMatch Dating AI'],
        'confrontation': ['MoltMatch Dating AI', 'AI Politician', 'Personal Hype Person'],
        'difficult conversation': ['MoltMatch Dating AI', 'AI Politician', 'AI Fortune Teller'],

        // Relationships & Dating
        'dating': ['Razer Project AVA', 'Text Back Timer', 'Confidence Boost Sessions'],
        'text': ['Text Back Timer', 'Sleep Arguments Winner', 'Excuse Generator Pro'],
        'crush': ['Text Back Timer', 'Razer Project AVA', 'Confidence Boost Sessions'],
        'breakup': ['Replika AI Companion', 'MoltMatch Dating AI', 'Memory Editor'],
        'relationship': ['Text Back Timer', 'MoltMatch Dating AI', 'AI Fortune Teller'],
        'ex': ['Memory Editor', 'Embarrassment Eraser', 'Replika AI Companion'],
        'flirt': ['Razer Project AVA', 'Confidence Boost Sessions', 'Text Back Timer'],
        'rejection': ['Replika AI Companion', 'AI Fortune Teller', 'Confidence Boost Sessions'],

        // Daily Life & Habits
        'morning': ['Personal Hype Person', 'Victory Lap Narrator', 'Main Character Syndrome AI'],
        'excuse': ['Excuse Generator Pro', 'AI Politician', 'DoNotPay "AI Lawyer"'],
        'late': ['Excuse Generator Pro', 'Time Perception Adjuster', 'AI Politician'],
        'cancel': ['Excuse Generator Pro', 'AI Politician', 'Social Battery Monitor'],
        'leave': ['Social Battery Monitor', 'Excuse Generator Pro', 'Razer Project AVA'],
        'tired': ['Social Battery Monitor', 'Excuse Generator Pro', 'Time Perception Adjuster'],
        'sleep': ['Sleep Arguments Winner', 'Time Perception Adjuster', 'Replika AI Companion'],
        'exercise': ['Personal Hype Person', 'Difficulty Level Changer', 'Victory Lap Narrator'],
        'diet': ['DoNotPay "AI Lawyer"', 'Difficulty Level Changer', 'Victory Lap Narrator'],

        // Reality & Self-Perception
        'reality': ['DoNotPay "AI Lawyer"', 'Memory Editor', 'Life Filter'],
        'memory': ['Memory Editor', 'Embarrassment Eraser', 'Razer Project AVA'],
        'embarrass': ['Embarrassment Eraser', 'Memory Editor', 'AI Fortune Teller'],
        'cringe': ['Embarrassment Eraser', 'Memory Editor', 'AI Fortune Teller'],
        'past': ['Memory Editor', 'Embarrassment Eraser', 'AI Fortune Teller'],
        'regret': ['Memory Editor', 'AI Fortune Teller', 'Replika AI Companion'],
        'mistake': ['Embarrassment Eraser', 'AI Fortune Teller', 'Memory Editor'],
        'fail': ['AI Fortune Teller', 'Victory Lap Narrator', 'Compliment Amplifier'],
        'success': ['Victory Lap Narrator', 'Success Rate Inflator', 'Main Character Syndrome AI'],

        // Performance & Image
        'perform': ['AI Actress', 'Personal Hype Person', 'Self-Esteem Projector'],
        'fake': ['Self-Esteem Projector', 'AI Actress', 'Life Filter'],
        'pretend': ['AI Actress', 'Self-Esteem Projector', 'AI Politician'],
        'lie': ['AI Politician', 'Excuse Generator Pro', 'Memory Editor'],
        'impress': ['AI Actress', 'Self-Esteem Projector', 'Main Character Syndrome AI'],
        'cool': ['Main Character Syndrome AI', 'Self-Esteem Projector', 'Life Filter'],
        'popular': ['Life Filter', 'Main Character Syndrome AI', 'Self-Esteem Projector'],

        // Entertainment & Fun
        'fun': ['Main Character Syndrome AI', 'Victory Lap Narrator', 'Life Filter'],
        'dramatic': ['AI Actress', 'Main Character Syndrome AI', 'Life Filter'],
        'famous': ['AI Actress', 'Main Character Syndrome AI', 'Self-Esteem Projector'],
        'movie': ['AI Actress', 'Main Character Syndrome AI', 'Life Filter'],
        'celebrity': ['AI Actress', 'Main Character Syndrome AI', 'Self-Esteem Projector'],
        'attention': ['Main Character Syndrome AI', 'AI Actress', 'Self-Esteem Projector'],

        // Specific Scenarios
        'family': ['Razer Project AVA', 'Excuse Generator Pro', 'Memory Editor'],
        'parents': ['AI Politician', 'Excuse Generator Pro', 'Razer Project AVA'],
        'wedding': ['Social Battery Monitor', 'Razer Project AVA', 'AI Dating Profile Writer'],
        'funeral': ['Replika AI Companion', 'AI Customer Service', 'AI Fortune Teller'],
        'holiday': ['Social Battery Monitor', 'Excuse Generator Pro', 'Razer Project AVA'],
        'reunion': ['Memory Editor', 'AI Dating Profile Writer', 'Self-Esteem Projector'],
        'gym': ['Personal Hype Person', 'Self-Esteem Projector', 'Difficulty Level Changer'],
        'restaurant': ['AI Customer Service', 'Demand Apology AI', 'Confidence Boost Sessions'],
        'shopping': ['AI Customer Service', 'Demand Apology AI', 'Excuse Generator Pro'],

        // Customer Service & Complaints
        'complain': ['AI Customer Service', 'Demand Apology AI', 'AI Politician'],
        'customer service': ['AI Customer Service', 'Demand Apology AI', 'AI Politician'],
        'refund': ['AI Customer Service', 'Demand Apology AI', 'AI Politician'],
        'karen': ['AI Customer Service', 'Demand Apology AI', 'AI Fortune Teller'],
        'manager': ['AI Customer Service', 'Demand Apology AI', 'AI Politician']
    }
};

// ============================================
// Initialize Chatbot
// ============================================

function initChatbot() {
    const chatbotButton = document.getElementById('chatbot-button');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotSend = document.getElementById('chatbot-send');
    const chatbotInput = document.getElementById('chatbot-input');

    if (!chatbotButton) return;

    // Toggle chatbot window
    chatbotButton.addEventListener('click', () => {
        toggleChatbot();
    });

    // Close chatbot
    if (chatbotClose) {
        chatbotClose.addEventListener('click', () => {
            toggleChatbot();
        });
    }

    // Send message
    if (chatbotSend) {
        chatbotSend.addEventListener('click', () => {
            sendMessage();
        });
    }

    // Send on Enter key
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

// ============================================
// Chatbot Functions
// ============================================

function toggleChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotButton = document.getElementById('chatbot-button');

    if (!chatbotWindow || !chatbotButton) return;

    ChatbotState.isOpen = !ChatbotState.isOpen;

    if (ChatbotState.isOpen) {
        chatbotWindow.classList.remove('hidden');
        chatbotButton.classList.add('minimized');
    } else {
        chatbotWindow.classList.add('hidden');
        chatbotButton.classList.remove('minimized');
    }
}

function sendMessage() {
    const input = document.getElementById('chatbot-input');
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');

    // Clear input
    input.value = '';

    // Generate bot response
    setTimeout(() => {
        const response = generateResponse(message);
        addMessage(response, 'bot');
    }, 500);
}

function addMessage(text, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user' ? 'user-message' : 'bot-message';

    if (sender === 'bot') {
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';
        messageDiv.appendChild(avatar);
    }

    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = text;
    messageDiv.appendChild(content);

    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Store message
    ChatbotState.messages.push({ text, sender });
}

function generateResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();

    // Find matching keywords
    let recommendations = new Set();
    let matchedKeywords = [];

    for (const [keyword, services] of Object.entries(ServiceRecommendations.keywords)) {
        if (lowerMessage.includes(keyword)) {
            matchedKeywords.push(keyword);
            services.forEach(service => recommendations.add(service));
        }
    }

    // Generate response with personality
    if (recommendations.size > 0) {
        const serviceList = Array.from(recommendations).slice(0, 4); // Limit to 4 recommendations

        const intros = [
            'Perfect! I found exactly what you need:',
            'Great news! These services are perfect for you:',
            'I know just what you need! Check these out:',
            'Based on what you told me, here are your best matches:',
            'You\'re in luck! These AI services are made for this:'
        ];

        const intro = intros[Math.floor(Math.random() * intros.length)];
        let response = `${intro}<br><br>`;

        serviceList.forEach(service => {
            response += `<strong>✨ ${service}</strong><br>`;
        });

        const outros = [
            '<br>Need more recommendations? Tell me more about your situation!',
            '<br>Want to explore other options? Just let me know what else you need!',
            '<br>These should help! Need anything else?',
            '<br>Try these out! What else can I help you find?'
        ];

        response += outros[Math.floor(Math.random() * outros.length)];
        return response;
    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
        return `Hey there! 👋 I'm here to help you find the perfect AI services. Tell me what you need!<br><br>
        Try things like:<br>
        • "I'm anxious about a job interview"<br>
        • "Need help with awkward family gatherings"<br>
        • "I keep procrastinating"<br>
        • "Help me get over my ex"<br>
        • "I need to cancel plans without feeling guilty"`;
    } else if (lowerMessage.includes('thank')) {
        const responses = [
            'You\'re welcome! Happy to help! 😊',
            'No problem! That\'s what I\'m here for! 🎉',
            'Anytime! Feel free to ask me anything else!',
            'My pleasure! Let me know if you need more recommendations!'
        ];
        return responses[Math.floor(Math.random() * responses.length)];
    } else if (lowerMessage.includes('help')) {
        return `I can help you find AI services for all kinds of situations! Try asking about:<br><br>
        <strong>😰 Emotional stuff:</strong> confidence, anxiety, stress, loneliness<br>
        <strong>👥 Social situations:</strong> parties, networking, conversations, dating<br>
        <strong>💼 Work life:</strong> meetings, interviews, procrastination, bosses<br>
        <strong>💔 Relationships:</strong> breakups, texting, conflicts, family drama<br>
        <strong>🎭 Daily life:</strong> excuses, apologies, embarrassing moments<br><br>
        Just tell me what you're dealing with!`;
    } else {
        return `Hmm, I'm not sure I caught that. Can you tell me more specifically what you need?<br><br>
        For example:<br>
        • "I'm stressed about work"<br>
        • "Help me be less awkward at parties"<br>
        • "I need an excuse to leave early"<br>
        • "Boost my confidence"<br>
        • "I can't stop thinking about something embarrassing"<br><br>
        What's going on? I'm here to help! 💪`;
    }
}

// ============================================
// Initialize on Load
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
} else {
    initChatbot();
}
