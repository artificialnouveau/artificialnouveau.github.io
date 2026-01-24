// Drone Cursor System
// Two drones: one follows mouse, one follows the mouse drone when it stops

class Drone {
    constructor(color, isAutonomous = false) {
        this.x = window.innerWidth / 2;
        this.y = window.innerHeight / 2;
        this.targetX = this.x;
        this.targetY = this.y;
        this.velocityX = 0;
        this.velocityY = 0;
        this.rotation = 0;
        this.tilt = 0;
        this.color = color;
        this.isAutonomous = isAutonomous;
        this.propellerRotation = 0;

        // Create drone element
        this.element = this.createDroneElement();
        document.body.appendChild(this.element);

        // Movement tracking
        this.lastMoveTime = Date.now();
        this.isMoving = false;
    }

    createDroneElement() {
        const drone = document.createElement('div');
        drone.className = `drone ${this.isAutonomous ? 'autonomous' : 'cursor'}`;

        const svg = `
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Drone body -->
                <g class="drone-body">
                    <!-- Center body -->
                    <rect x="40" y="40" width="20" height="20" fill="${this.color}" stroke="${this.color}" stroke-width="2" rx="2"/>
                    <circle cx="50" cy="50" r="6" fill="rgba(0,0,0,0.8)"/>

                    <!-- Camera (only for autonomous drone) -->
                    ${this.isAutonomous ? `
                        <circle cx="50" cy="50" r="4" fill="#b010ff" opacity="0.8"/>
                        <circle cx="50" cy="50" r="2" fill="#ff10f0" opacity="0.9"/>
                    ` : ''}

                    <!-- Arms -->
                    <line x1="50" y1="50" x2="20" y2="20" stroke="${this.color}" stroke-width="3"/>
                    <line x1="50" y1="50" x2="80" y2="20" stroke="${this.color}" stroke-width="3"/>
                    <line x1="50" y1="50" x2="20" y2="80" stroke="${this.color}" stroke-width="3"/>
                    <line x1="50" y1="50" x2="80" y2="80" stroke="${this.color}" stroke-width="3"/>
                </g>

                <!-- Propellers -->
                <g class="propeller" data-propeller="1" style="transform-origin: 20px 20px">
                    <ellipse cx="20" cy="20" rx="8" ry="3" fill="${this.color}" opacity="0.6"/>
                    <ellipse cx="20" cy="20" rx="3" ry="8" fill="${this.color}" opacity="0.4"/>
                </g>
                <g class="propeller" data-propeller="2" style="transform-origin: 80px 20px">
                    <ellipse cx="80" cy="20" rx="8" ry="3" fill="${this.color}" opacity="0.6"/>
                    <ellipse cx="80" cy="20" rx="3" ry="8" fill="${this.color}" opacity="0.4"/>
                </g>
                <g class="propeller" data-propeller="3" style="transform-origin: 20px 80px">
                    <ellipse cx="20" cy="80" rx="8" ry="3" fill="${this.color}" opacity="0.6"/>
                    <ellipse cx="20" cy="80" rx="3" ry="8" fill="${this.color}" opacity="0.4"/>
                </g>
                <g class="propeller" data-propeller="4" style="transform-origin: 80px 80px">
                    <ellipse cx="80" cy="80" rx="8" ry="3" fill="${this.color}" opacity="0.6"/>
                    <ellipse cx="80" cy="80" rx="3" ry="8" fill="${this.color}" opacity="0.4"/>
                </g>

                <!-- Scanning lines for autonomous drone -->
                ${this.isAutonomous ? `
                    <line class="scan-line" x1="50" y1="50" x2="50" y2="0" stroke="#00f0ff" stroke-width="1" opacity="0.6">
                        <animateTransform
                            attributeName="transform"
                            type="rotate"
                            from="0 50 50"
                            to="360 50 50"
                            dur="3s"
                            repeatCount="indefinite"/>
                    </line>
                ` : ''}
            </svg>
        `;

        drone.innerHTML = svg;
        drone.style.cssText = `
            position: fixed;
            width: 60px;
            height: 60px;
            pointer-events: none;
            z-index: 10000;
            transform: translate(-50%, -50%);
            filter: drop-shadow(0 0 10px ${this.color}) drop-shadow(0 0 20px ${this.color});
        `;

        return drone;
    }

    setTarget(x, y) {
        this.targetX = x;
        this.targetY = y;
    }

    update() {
        // Smooth following with easing
        const ease = this.isAutonomous ? 0.03 : 0.15;
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;

        this.velocityX = dx * ease;
        this.velocityY = dy * ease;

        this.x += this.velocityX;
        this.y += this.velocityY;

        // Calculate tilt based on velocity
        const speed = Math.sqrt(this.velocityX ** 2 + this.velocityY ** 2);
        this.isMoving = speed > 0.5;

        if (this.isMoving) {
            this.lastMoveTime = Date.now();
        }

        if (speed > 0.1) {
            const angle = Math.atan2(this.velocityY, this.velocityX);
            this.rotation = angle * (180 / Math.PI);
            this.tilt = Math.min(speed * 2, 15);
        } else {
            this.tilt *= 0.9;
        }

        // Spin propellers
        this.propellerRotation += speed * 10 + 5;

        // Update DOM
        this.element.style.left = `${this.x}px`;
        this.element.style.top = `${this.y}px`;
        this.element.style.transform = `
            translate(-50%, -50%)
            rotate(${this.rotation}deg)
            rotateX(${this.tilt}deg)
        `;

        // Animate propellers
        const propellers = this.element.querySelectorAll('.propeller');
        propellers.forEach((prop, index) => {
            const offset = index * 90;
            prop.style.transform = `rotate(${this.propellerRotation + offset}deg)`;
        });
    }

    hasStoppedMoving() {
        return Date.now() - this.lastMoveTime > 100;
    }
}

// Initialize drones
let mouseDrone, autonomousDrone;
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let lastMouseDroneX = mouseX;
let lastMouseDroneY = mouseY;

function initDrones() {
    // Hide default cursor
    document.body.style.cursor = 'none';
    document.querySelectorAll('a, button, input, textarea, select').forEach(el => {
        el.style.cursor = 'none';
    });

    // Create drones
    mouseDrone = new Drone('#ff10f0', false);  // Hot pink for mouse drone
    autonomousDrone = new Drone('#00f0ff', true);  // Cyan for autonomous drone

    // Track mouse
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Animation loop
    function animate() {
        // Mouse drone follows cursor
        mouseDrone.setTarget(mouseX, mouseY);
        mouseDrone.update();

        // Autonomous drone behavior:
        // - When mouse drone is moving, autonomous drone stops
        // - When mouse drone stops, autonomous drone moves to its location
        if (mouseDrone.hasStoppedMoving()) {
            // Mouse drone has stopped, move autonomous drone to where mouse drone is
            autonomousDrone.setTarget(mouseDrone.x, mouseDrone.y);
        } else {
            // Mouse drone is moving, autonomous drone stays put (targets its own position)
            autonomousDrone.setTarget(autonomousDrone.x, autonomousDrone.y);
        }

        autonomousDrone.update();

        requestAnimationFrame(animate);
    }

    animate();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDrones);
} else {
    initDrones();
}
