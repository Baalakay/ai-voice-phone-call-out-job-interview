// GravyWork Skills Assessment - Frontend JavaScript
// Handles role selection, form validation, and API calls

class AssessmentApp {
    constructor() {
        this.apiBaseUrl = 'https://eih1khont2.execute-api.us-east-1.amazonaws.com';
        this.selectedRole = null;
        this.initializeApp();
    }

    initializeApp() {
        this.bindEventListeners();
        this.setupFormValidation();
        this.loadPersistedData();
    }

    bindEventListeners() {
        // Role selection
        const roleCards = document.querySelectorAll('.role-card');
        roleCards.forEach(card => {
            card.addEventListener('click', (e) => this.selectRole(e));
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectRole(e);
                }
            });
            // Make role cards focusable
            card.setAttribute('tabindex', '0');
        });

        // Form submission
        const form = document.getElementById('assessmentForm');
        form.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Phone number formatting and persistence
        const phoneInput = document.getElementById('phoneNumber');
        phoneInput.addEventListener('input', (e) => {
            this.formatPhoneNumber(e);
            this.savePhoneNumber(e.target.value);
        });
        phoneInput.addEventListener('keyup', () => this.validateForm());
    }

    selectRole(event) {
        const clickedCard = event.currentTarget;
        const role = clickedCard.dataset.role;

        // Remove selection from all cards
        document.querySelectorAll('.role-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Add selection to clicked card
        clickedCard.classList.add('selected');
        
        // Update hidden input and instance variable
        this.selectedRole = role;
        document.getElementById('skillType').value = role;

        // Save selected role to localStorage
        this.saveSelectedRole(role);

        // Validate form after role selection
        this.validateForm();

        // Provide visual feedback
        this.showStatus(`Selected: ${this.getRoleDisplayName(role)}`, 'info', 2000);
    }

    getRoleDisplayName(role) {
        const roleNames = {
            'bartender': 'Bartender',
            'banquet_server': 'Banquet Server',
            'host': 'Host'
        };
        return roleNames[role] || role;
    }

    formatPhoneNumber(event) {
        let value = event.target.value.replace(/\D/g, '');
        
        // Handle different input lengths
        if (value.length >= 11 && value.startsWith('1')) {
            // US number with country code
            value = value.substring(1); // Remove leading 1
        }
        
        if (value.length >= 10) {
            // Format as (XXX) XXX-XXXX
            value = `(${value.substring(0, 3)}) ${value.substring(3, 6)}-${value.substring(6, 10)}`;
        } else if (value.length >= 6) {
            // Format as (XXX) XXX-X...
            value = `(${value.substring(0, 3)}) ${value.substring(3, 6)}-${value.substring(6)}`;
        } else if (value.length >= 3) {
            // Format as (XXX) X...
            value = `(${value.substring(0, 3)}) ${value.substring(3)}`;
        }

        event.target.value = value;
    }

    validateForm() {
        const phoneNumber = document.getElementById('phoneNumber').value;
        const skillType = document.getElementById('skillType').value;
        const submitBtn = document.getElementById('initiateBtn');

        // Check if phone number has at least 10 digits
        const digitsOnly = phoneNumber.replace(/\D/g, '');
        const isPhoneValid = digitsOnly.length >= 10;
        const isRoleSelected = skillType !== '';

        // Enable/disable submit button
        submitBtn.disabled = !(isPhoneValid && isRoleSelected);

        // Update button text based on validation
        const btnText = submitBtn.querySelector('.btn-text');
        if (isPhoneValid && isRoleSelected) {
            btnText.textContent = 'Start Assessment Call';
        } else if (!isRoleSelected) {
            btnText.textContent = 'Select a Role First';
        } else {
            btnText.textContent = 'Enter Valid Phone Number';
        }
    }

    setupFormValidation() {
        // Initial validation
        this.validateForm();
    }

    async handleFormSubmit(event) {
        event.preventDefault();

        const submitBtn = document.getElementById('initiateBtn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnIcon = submitBtn.querySelector('.btn-icon');
        
        // Get form data
        const phoneNumber = this.normalizePhoneNumber(document.getElementById('phoneNumber').value);
        const skillType = document.getElementById('skillType').value;

        if (!phoneNumber || !skillType) {
            this.showStatus('Please fill in all fields and select a role.', 'error');
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        btnIcon.textContent = '⏳';
        btnText.textContent = 'Initiating Call...';

        try {
            const response = await this.initiateAssessment(phoneNumber, skillType);
            
            if (response.success) {
                this.showStatus(
                    `🎉 Success! Your phone should be ringing shortly. Assessment ID: ${response.assessment_id}`,
                    'success'
                );
                
                // Reset form after successful submission
                setTimeout(() => {
                    this.resetForm();
                }, 3000);
            } else {
                throw new Error(response.message || 'Failed to initiate assessment');
            }
        } catch (error) {
            console.error('Assessment initiation error:', error);
            this.showStatus(
                `❌ Error: ${error.message}. Please try again or contact support.`,
                'error'
            );
        } finally {
            // Reset button state
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.classList.remove('loading');
                btnIcon.textContent = '📞';
                btnText.textContent = 'Start Assessment Call';
                this.validateForm(); // Re-validate to set proper button state
            }, 2000);
        }
    }

    normalizePhoneNumber(phoneNumber) {
        // Extract digits only
        const digitsOnly = phoneNumber.replace(/\D/g, '');
        
        // Add country code if missing
        if (digitsOnly.length === 10) {
            return `+1${digitsOnly}`;
        } else if (digitsOnly.length === 11 && digitsOnly.startsWith('1')) {
            return `+${digitsOnly}`;
        }
        
        return phoneNumber; // Return as-is if we can't normalize
    }

    async initiateAssessment(phoneNumber, skillType) {
        const workerId = this.generateWorkerId(skillType);
        
        const requestBody = {
            worker_phone: phoneNumber,
            skill_type: skillType,
            worker_id: workerId
        };

        console.log('Initiating assessment with:', requestBody);

        const response = await fetch(`${this.apiBaseUrl}/initiate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        return await response.json();
    }

    generateWorkerId(skillType) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '').substring(0, 15);
        const random = Math.random().toString(36).substring(2, 8);
        return `${skillType}_${timestamp}_${random}`;
    }

    showStatus(message, type, duration = 5000) {
        const statusElement = document.getElementById('statusMessage');
        
        // Clear existing classes and content
        statusElement.className = 'status-message';
        statusElement.classList.add(type);
        statusElement.textContent = message;
        statusElement.classList.remove('hidden');

        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => {
                statusElement.classList.add('hidden');
            }, duration);
        }
    }

    resetForm() {
        // Keep the phone number but reset role selection
        document.getElementById('skillType').value = '';
        
        // Reset role selection
        document.querySelectorAll('.role-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        this.selectedRole = null;
        
        // Clear the saved role from localStorage
        localStorage.removeItem('gravywork_selected_role');
        
        // Re-validate form
        this.validateForm();
        
        // Hide status message
        document.getElementById('statusMessage').classList.add('hidden');
    }

    loadPersistedData() {
        // Load and set default or persisted phone number
        const savedPhone = localStorage.getItem('gravywork_phone_number');
        const phoneInput = document.getElementById('phoneNumber');
        
        if (savedPhone) {
            phoneInput.value = savedPhone;
        } else {
            // Set default phone number
            phoneInput.value = '(234) 555-6789';
            this.savePhoneNumber('(234) 555-6789');
        }

        // Load and restore selected role
        const savedRole = localStorage.getItem('gravywork_selected_role');
        if (savedRole) {
            // Find and select the role card
            const roleCard = document.querySelector(`[data-role="${savedRole}"]`);
            if (roleCard) {
                roleCard.classList.add('selected');
                this.selectedRole = savedRole;
                document.getElementById('skillType').value = savedRole;
            }
        }

        // Validate form after loading persisted data
        this.validateForm();
    }

    savePhoneNumber(phoneNumber) {
        localStorage.setItem('gravywork_phone_number', phoneNumber);
    }

    saveSelectedRole(role) {
        localStorage.setItem('gravywork_selected_role', role);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🍽️ GravyWork Skills Assessment - Initializing...');
    new AssessmentApp();
    console.log('✅ Application initialized successfully');
});

// Add some helpful console messages for debugging
console.log('🚀 GravyWork Skills Assessment Platform');
console.log('📱 Ready to initiate AI-powered phone assessments');
console.log('🎤 Powered by ElevenLabs Rachel voice & AWS infrastructure');
