/**
 * More AI In Ee Edit Please - Main Application
 *
 * Handles tab switching, persona interactions, and mystery box functionality
 */

// ============================================
// Application State
// ============================================

const AppState = {
    currentTab: 'automation',
    urgentTimerInterval: null,
    mysteryHistory: []
};

// ============================================
// Mystery Box Services
// ============================================

const MYSTERY_SERVICES = [
    {
        icon: '🎤',
        title: 'Shower Concert Critic',
        desc: 'AI-powered feedback on your shower singing. Includes key suggestions and vocal coaching for soap opera performances.'
    },
    {
        icon: '🍕',
        title: 'Pizza Topping Mediator',
        desc: 'Resolves pizza topping disputes with diplomatic precision. Suggests compromise solutions that satisfy everyone (or no one).'
    },
    {
        icon: '🎮',
        title: 'Video Game NPC Generator',
        desc: 'Creates custom NPCs based on people in your life. Your boss now gives you side quests!'
    },
    {
        icon: '🌙',
        title: 'Dream Interpreter Pro',
        desc: 'Analyzes your dreams and connects them to your grocery shopping habits. Results may vary wildly.'
    },
    {
        icon: '🎨',
        title: 'Doodle Analyzer',
        desc: 'Interprets your meeting doodles as serious art. Provides gallery-worthy descriptions of your stick figures.'
    },
    {
        icon: '🐱',
        title: 'Pet Thought Translator',
        desc: 'Translates what your pet is thinking. Spoiler: It\'s mostly "feed me" and "why did you leave?"'
    },
    {
        icon: '📚',
        title: 'Book Ending Spoiler Avoider',
        desc: 'Monitors your reading speed and prevents accidental glances at the last page. Eye-tracking technology included.'
    },
    {
        icon: '☕',
        title: 'Coffee Shop Order Optimizer',
        desc: 'Calculates the perfect level of coffee order complexity to seem sophisticated without annoying the barista.'
    },
    {
        icon: '🎵',
        title: 'Elevator Music Curator',
        desc: 'Customizes elevator music based on who\'s in the elevator with you. Awkward silence? Not anymore!'
    },
    {
        icon: '🌮',
        title: 'Taco Tuesday Enforcer',
        desc: 'Ensures you never miss Taco Tuesday. Sends increasingly urgent reminders. Will shame you if you eat other food.'
    },
    {
        icon: '🎪',
        title: 'Life Event Exaggerator',
        desc: 'Makes mundane events sound epic for social media. "I went to the store" becomes "An adventure of legendary proportions."'
    },
    {
        icon: '🧦',
        title: 'Sock Matching AI',
        desc: 'Uses advanced algorithms to reunite lost socks. Success rate: 12%. But that\'s 12% more than you had!'
    },
    {
        icon: '🌈',
        title: 'Rainbow Forecast',
        desc: 'Predicts rainbow appearances with unprecedented accuracy. Includes double rainbow probability metrics.'
    },
    {
        icon: '🎯',
        title: 'Procrastination Optimizer',
        desc: 'Helps you procrastinate more efficiently. Suggests the perfect productive-feeling tasks to avoid actual work.'
    },
    {
        icon: '🍿',
        title: 'Movie Plot Predictor',
        desc: 'Predicts movie endings 10 minutes in. Can be turned off if you actually want to enjoy the film.'
    },
    {
        icon: '🎲',
        title: 'Decision Paralyzer',
        desc: 'For people who can\'t decide: This AI presents you with MORE options. Now you really can\'t choose!'
    }
];

// ============================================
// Initialize Application
// ============================================

/**
 * Initialize application on DOM load
 */
function initApp() {
    // Set up tab functionality
    setupTabs();

    // Set up persona hover effects
    setupPersonaCards();

    // Set up mystery box
    setupMysteryBox();

    // Set up urgent timer
    startUrgentTimer();

    // Set up CTA button
    setupCTAButton();

    console.log('More AI ! I Need It! Please! - Initialized');
}

// ============================================
// Tab Functionality
// ============================================

/**
 * Set up tab switching
 */
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);

            // Play sound if available
            if (typeof playDingSound === 'function') {
                playDingSound();
            }

            // Create sparkles if available
            if (typeof createSparkleBurst === 'function') {
                createSparkleBurst(5);
            }
        });
    });
}

/**
 * Switch to a different tab
 */
function switchTab(tabName) {
    // Update state
    AppState.currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        const contentId = content.id.replace('-tab', '');
        if (contentId === tabName) {
            content.classList.remove('hidden');
            content.classList.add('active');
        } else {
            content.classList.add('hidden');
            content.classList.remove('active');
        }
    });
}

// ============================================
// Persona Cards
// ============================================

/**
 * Set up persona card hover effects
 */
function setupPersonaCards() {
    const personaCards = document.querySelectorAll('.persona-card');

    personaCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.classList.add('hovered');

            // Optional: play subtle sound
            if (typeof playDingSound === 'function') {
                playDingSound();
            }
        });

        card.addEventListener('mouseleave', () => {
            card.classList.remove('hovered');
        });
    });
}

// ============================================
// Mystery Box
// ============================================

/**
 * Set up mystery box functionality
 */
function setupMysteryBox() {
    const mysteryBtn = document.getElementById('mystery-box-btn');
    const tryAgainBtn = document.getElementById('mystery-again-btn');

    if (mysteryBtn) {
        mysteryBtn.addEventListener('click', () => revealMystery());
    }

    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', () => resetMystery());
    }
}

/**
 * Reveal a random mystery service
 */
function revealMystery() {
    const mysteryBox = document.getElementById('mystery-box-btn');
    const mysteryResult = document.getElementById('mystery-result');

    if (!mysteryBox || !mysteryResult) return;

    // Hide box, show result
    mysteryBox.classList.add('hidden');

    // Get random service
    const service = MYSTERY_SERVICES[Math.floor(Math.random() * MYSTERY_SERVICES.length)];

    // Update result display
    document.querySelector('.mystery-result-icon').textContent = service.icon;
    document.querySelector('.mystery-result-title').textContent = service.title;
    document.querySelector('.mystery-result-desc').textContent = service.desc;

    // Show result with animation
    mysteryResult.classList.remove('hidden');

    // Add to history
    addToMysteryHistory(service);

    // Play sound and effects
    if (typeof playSlotMachineSound === 'function') {
        playSlotMachineSound();
    }

    if (typeof createConfettiBurst === 'function') {
        setTimeout(() => {
            createConfettiBurst(30);
        }, 500);
    }
}

/**
 * Reset mystery box for another try
 */
function resetMystery() {
    const mysteryBox = document.getElementById('mystery-box-btn');
    const mysteryResult = document.getElementById('mystery-result');

    if (!mysteryBox || !mysteryResult) return;

    // Hide result, show box
    mysteryResult.classList.add('hidden');
    mysteryBox.classList.remove('hidden');

    // Play sound
    if (typeof playDingSound === 'function') {
        playDingSound();
    }
}

/**
 * Add service to mystery history
 */
function addToMysteryHistory(service) {
    AppState.mysteryHistory.push(service);

    const historyList = document.getElementById('mystery-history-list');
    if (!historyList) return;

    // Remove empty message if present
    const emptyMsg = historyList.querySelector('.mystery-history-empty');
    if (emptyMsg) {
        emptyMsg.remove();
    }

    // Add new item
    const item = document.createElement('div');
    item.className = 'mystery-history-item';
    item.innerHTML = `
        <span class="history-icon">${service.icon}</span>
        <span class="history-title">${service.title}</span>
    `;

    historyList.insertBefore(item, historyList.firstChild);

    // Limit history to 10 items
    while (historyList.children.length > 10) {
        historyList.removeChild(historyList.lastChild);
    }
}

// ============================================
// Urgent Timer
// ============================================

/**
 * Start fake urgent timer
 */
function startUrgentTimer() {
    const timerText = document.getElementById('urgent-countdown');
    const banner = document.getElementById('urgent-timer-banner');

    if (!timerText || !banner) return;

    // Set initial random time (3-15 minutes)
    let remainingSeconds = Math.floor(Math.random() * (15 * 60 - 3 * 60 + 1)) + 3 * 60;

    const updateTimer = () => {
        remainingSeconds--;

        if (remainingSeconds <= 0) {
            // Reset timer with flash
            remainingSeconds = Math.floor(Math.random() * (15 * 60 - 3 * 60 + 1)) + 3 * 60;

            // Flash effect
            banner.classList.add('timer-extended-flash');
            setTimeout(() => {
                banner.classList.remove('timer-extended-flash');
            }, 1000);

            // Temporary message
            const originalHTML = timerText.innerHTML;
            timerText.textContent = 'NEW SERVICES ADDED!';
            setTimeout(() => {
                updateTimerDisplay();
            }, 2000);
        } else {
            updateTimerDisplay();
        }
    };

    const updateTimerDisplay = () => {
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;
        timerText.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    };

    // Initial display
    updateTimerDisplay();

    // Update every second
    AppState.urgentTimerInterval = setInterval(updateTimer, 1000);

    // Add blinking effect
    banner.classList.add('blinking');
}

// ============================================
// CTA Button
// ============================================

/**
 * Set up main CTA button
 */
function setupCTAButton() {
    const ctaBtn = document.getElementById('cta-main');
    const revealEl = document.getElementById('cta-reveal');

    if (!ctaBtn || !revealEl) return;

    ctaBtn.addEventListener('click', () => {
        // Hide button
        ctaBtn.style.display = 'none';

        // Show reveal text
        revealEl.classList.remove('hidden');
        revealEl.classList.add('reveal');

        // Extra confetti
        if (typeof createConfettiBurst === 'function') {
            createConfettiBurst(100);
        }

        // Play sound
        if (typeof playSlotMachineSound === 'function') {
            playSlotMachineSound();
        }
    });
}

// ============================================
// Cleanup
// ============================================

/**
 * Clean up intervals on page unload
 */
window.addEventListener('beforeunload', () => {
    if (AppState.urgentTimerInterval) {
        clearInterval(AppState.urgentTimerInterval);
    }
});

// ============================================
// Initialize on DOM Load
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
