// GravyWork Assessment Analysis Dashboard
// Handles listing assessments and displaying detailed analysis

class AnalysisDashboard {
    constructor() {
        this.bucketUrl = 'https://innovativesol-gravywork-assets-dev.s3.amazonaws.com';
        this.assessments = [];
        this.selectedAssessment = null;
        this.filteredAssessments = [];
        this.initializeApp();
    }

    initializeApp() {
        this.bindEventListeners();
        this.loadAssessments();
    }

    bindEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => this.filterAssessments(e.target.value));

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.addEventListener('click', () => this.loadAssessments());

        // Retry button
        const retryBtn = document.getElementById('retryBtn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.retryLoadAnalysis());
        }
    }

    async loadAssessments() {
        const container = document.getElementById('assessmentsList');
        const refreshBtn = document.getElementById('refreshBtn');
        
        // Show loading state
        container.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Discovering assessments...</span>
                <div class="loading-progress" style="margin-top: 0.5rem; font-size: 0.9rem; color: #666;">
                    This may take a moment as we search for completed assessments...
                </div>
            </div>
        `;
        
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            // Since we can't directly list S3 objects from the browser,
            // we'll try to load a known list or use a pattern-based approach
            const assessments = await this.discoverAssessments();
            this.assessments = assessments;
            this.filteredAssessments = [...assessments];
            this.renderAssessmentsList();
        } catch (error) {
            console.error('Error loading assessments:', error);
            container.innerHTML = `
                <div class="loading-state">
                    <i class="fas fa-exclamation-triangle" style="color: var(--error-color);"></i>
                    <span>Unable to load assessments</span>
                    <button onclick="window.analysisDashboard.loadAssessments()" class="btn-retry" style="margin-top: 1rem;">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }

    async discoverAssessments() {
        // Read from the global assessment index instead of guessing IDs
        console.log('🔍 Loading assessments from global index...');
        
        try {
            const indexResponse = await fetch(`${this.bucketUrl}/assessments_index.json`);
            
            if (!indexResponse.ok) {
                console.error('Failed to load assessment index:', indexResponse.status, indexResponse.statusText);
                return [];
            }
            
            const indexData = await indexResponse.json();
            console.log(`📊 Found ${indexData.total_count} assessments in index`);
            
            // Transform the index data to match our expected format
            const assessments = indexData.assessments.map(assessment => ({
                id: assessment.id,
                role: assessment.role,
                date: this.formatDate(assessment.date),
                time: this.formatTime(assessment.time),
                status: assessment.status,
                timestamp: new Date(assessment.analyzed_at)
            }));
            
            console.log(`✅ Loaded ${assessments.length} assessments from index`);
            return assessments;
            
        } catch (error) {
            console.error('Error loading assessment index:', error);
            return [];
        }
    }
    

    formatDate(dateStr) {
        // Convert YYYYMMDD to readable format
        const year = dateStr.slice(0, 4);
        const month = dateStr.slice(4, 6);
        const day = dateStr.slice(6, 8);
        return new Date(`${year}-${month}-${day}`).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }

    formatTime(timeStr) {
        // Convert HHMMSS to readable format
        const hour = parseInt(timeStr.slice(0, 2));
        const minute = timeStr.slice(2, 4);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const hour12 = hour % 12 || 12;
        return `${hour12}:${minute} ${ampm}`;
    }

    filterAssessments(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        if (!term) {
            this.filteredAssessments = [...this.assessments];
        } else {
            this.filteredAssessments = this.assessments.filter(assessment => 
                assessment.id.toLowerCase().includes(term) ||
                assessment.role.toLowerCase().includes(term) ||
                assessment.status.toLowerCase().includes(term)
            );
        }
        this.renderAssessmentsList();
    }

    renderAssessmentsList() {
        const container = document.getElementById('assessmentsList');
        
        if (this.filteredAssessments.length === 0) {
            container.innerHTML = `
                <div class="loading-state">
                    <i class="fas fa-search"></i>
                    <span>No assessments found</span>
                    <div style="margin-top: 1rem; font-size: 0.8rem; color: #6b7280;">
                        Available assessments will appear here.<br>
                        Try refreshing or check the console for details.
                    </div>
                </div>
            `;
            return;
        }

        const html = this.filteredAssessments.map(assessment => `
            <div class="assessment-item ${this.selectedAssessment?.id === assessment.id ? 'selected' : ''}" 
                 data-assessment-id="${assessment.id}"
                 onclick="window.analysisDashboard.selectAssessment('${assessment.id}')">
                <div class="assessment-header">
                    <div class="assessment-role">${assessment.role}</div>
                    <div class="assessment-status status-${assessment.status}">
                        ${assessment.status.toUpperCase()}
                    </div>
                </div>
                <div class="assessment-id">${assessment.id}</div>
                <div class="assessment-date">${assessment.date} at ${assessment.time}</div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async selectAssessment(assessmentId) {
        // Update UI selection
        document.querySelectorAll('.assessment-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-assessment-id="${assessmentId}"]`)?.classList.add('selected');

        // Find the assessment
        this.selectedAssessment = this.assessments.find(a => a.id === assessmentId);
        
        // Hide welcome state and show loading
        document.getElementById('welcomeState').classList.add('hidden');
        document.getElementById('errorState').classList.add('hidden');
        document.getElementById('analysisContent').classList.add('hidden');
        
        // Show loading in main panel
        const mainPanel = document.querySelector('.main-panel');
        const loadingHtml = `
            <div class="loading-state" style="height: 100%;">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Loading analysis...</span>
            </div>
        `;
        
        const tempLoading = document.createElement('div');
        tempLoading.innerHTML = loadingHtml;
        tempLoading.style.position = 'absolute';
        tempLoading.style.top = '0';
        tempLoading.style.left = '0';
        tempLoading.style.right = '0';
        tempLoading.style.bottom = '0';
        tempLoading.style.background = 'white';
        tempLoading.style.display = 'flex';
        tempLoading.style.alignItems = 'center';
        tempLoading.style.justifyContent = 'center';
        tempLoading.className = 'temp-loading';
        
        mainPanel.appendChild(tempLoading);

        try {
            await this.loadAnalysis(assessmentId);
        } catch (error) {
            this.showError(error.message);
        } finally {
            // Remove loading overlay
            const loadingOverlay = document.querySelector('.temp-loading');
            if (loadingOverlay) {
                loadingOverlay.remove();
            }
        }
    }

    async loadAnalysis(assessmentId) {
        const response = await fetch(`${this.bucketUrl}/assessments/${assessmentId}/analysis_results.json`);
        
        if (!response.ok) {
            throw new Error(`Analysis not found for assessment: ${assessmentId}`);
        }
        
        const results = await response.json();
        this.displayAnalysis(results, assessmentId);
    }

    displayAnalysis(results, assessmentId) {
        const container = document.getElementById('analysisContent');
        const analysis = results.llm_analysis;
        
        if (!analysis) {
            throw new Error('No analysis data found in results');
        }

        const assessment = this.selectedAssessment;
        const html = `
            <div class="analysis-header">
                <div class="analysis-title">
                    <h2>${assessment.role.replace(/\b\w/g, l => l.toUpperCase())} Assessment</h2>
                    <div class="analysis-subtitle">${assessmentId}</div>
                </div>
                <div class="analysis-actions">
                    <button class="btn-action" onclick="window.print()">
                        <i class="fas fa-print"></i> Print
                    </button>
                    <button class="btn-action" onclick="window.analysisDashboard.exportAnalysis()">
                        <i class="fas fa-download"></i> Export
                    </button>
                </div>
            </div>

            <div class="overall-score">
                <h3>Overall Assessment Result</h3>
                <div class="score">${analysis.overall_assessment?.recommendation || analysis.overall_recommendation || 'Unknown'}</div>
                <div class="recommendation">${analysis.overall_assessment?.reasoning || analysis.overall_reasoning || 'No reasoning available'}</div>
                <div class="score-details">
                    <div class="score-detail">
                        <div class="score-detail-value">${analysis.overall_assessment?.categories_above_70_percent || 0}/3</div>
                        <div class="score-detail-label">Categories Passed</div>
                    </div>
                    <div class="score-detail">
                        <div class="score-detail-value">${assessment.date}</div>
                        <div class="score-detail-label">Assessment Date</div>
                    </div>
                </div>
            </div>

            <div class="categories-section">
                ${this.buildCategoriesHTML(analysis, results.transcripts)}
            </div>
        `;
        
        container.innerHTML = html;
        container.classList.remove('hidden');
        this.initializeAccordions();
    }

    buildCategoriesHTML(analysis, transcripts) {
        const categoryBreakdown = analysis.category_breakdown || {};
        const questionDetails = analysis.question_details || {};
        
        return Object.entries(categoryBreakdown).map(([categoryName, categoryData]) => {
            const questions = categoryData.questions_included || [];
            const statusClass = categoryData.status.includes('✅') ? 'status-pass' : 'status-fail';
            
            return `
                <div class="category-section">
                    <div class="category-header" data-category="${categoryName}">
                        <div class="category-title">
                            <h4>${categoryName}</h4>
                            <div class="category-score">
                                <span class="category-status ${statusClass}">${categoryData.status}</span>
                                <span class="category-percentage">${categoryData.average_score} (${categoryData.percentage})</span>
                                <span class="expand-icon">▶</span>
                            </div>
                        </div>
                    </div>
                    <div class="category-content" data-category-content="${categoryName}">
                        ${questions.map(questionKey => {
                            const questionData = questionDetails[questionKey];
                            if (!questionData) return '';
                            
                            return `
                                <div class="question-item">
                                    <div class="question-header" data-question="${questionKey}">
                                        <div class="question-title">
                                            <span class="question-text">${this.getQuestionText(questionKey)}</span>
                                            <span class="question-score">
                                                ${questionData.level} 
                                                <strong>${questionData.score}</strong>
                                            </span>
                                        </div>
                                    </div>
                                    <div class="question-details" data-question-details="${questionKey}">
                                        <div class="original-question-section">
                                            <div class="answer-label">
                                                <i class="fas fa-question-circle"></i> Original Question
                                            </div>
                                            <div class="answer-text original-question">"${this.getOriginalQuestion(questionKey)}"</div>
                                        </div>
                                        <div class="answer-section">
                                            <div class="answer-label">
                                                <i class="fas fa-user"></i> Candidate Response
                                            </div>
                                            <div class="answer-text">"${this.getCandidateAnswer(questionKey, transcripts || {})}"</div>
                                        </div>
                                        <div class="reasoning-section">
                                            <div class="answer-label">
                                                <i class="fas fa-brain"></i> AI Analysis
                                            </div>
                                            <div class="answer-text">${questionData.reasoning}</div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }).join('');
    }

    buildFallbackQuestionsHTML(questionDetails, transcripts) {
        // Create a single "Assessment Questions" category for older assessments without category breakdown
        const questions = Object.keys(questionDetails);
        
        return `
            <div class="category-section">
                <div class="category-header" data-category="Assessment Questions">
                    <div class="category-title">
                        <h4>Assessment Questions</h4>
                        <div class="category-score">
                            <span class="category-status status-info">📋 Details Available</span>
                            <span class="category-percentage">${questions.length} questions</span>
                            <span class="expand-icon">▶</span>
                        </div>
                    </div>
                </div>
                <div class="category-content" data-category-content="Assessment Questions">
                    ${questions.map((questionKey, index) => {
                        const questionData = questionDetails[questionKey];
                        if (!questionData) return '';
                        
                        return `
                            <div class="question-item">
                                <div class="question-header" data-question="${questionKey}">
                                    <div class="question-title">
                                        <span class="question-text">${this.getActualQuestionText(questionKey, index + 1)}</span>
                                        <span class="question-score">
                                            ${questionData.level || '📝'} 
                                            <strong>${questionData.score || 'N/A'}</strong>
                                        </span>
                                    </div>
                                </div>
                                <div class="question-details" data-question-details="${questionKey}">
                                    <div class="original-question-section">
                                        <div class="answer-label">
                                            <i class="fas fa-question-circle"></i> Original Question
                                        </div>
                                        <div class="answer-text original-question">"${this.getOriginalQuestion(questionKey)}"</div>
                                    </div>
                                    <div class="answer-section">
                                        <div class="answer-label">
                                            <i class="fas fa-user"></i> Candidate Response
                                        </div>
                                        <div class="answer-text">"${this.getCandidateAnswer(questionKey, transcripts || {})}"</div>
                                    </div>
                                    <div class="reasoning-section">
                                        <div class="answer-label">
                                            <i class="fas fa-brain"></i> AI Analysis
                                        </div>
                                        <div class="answer-text">${questionData.reasoning || 'Analysis available'}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    getActualQuestionText(questionKey, questionNumber) {
        // Map question keys to actual questions asked based on assessment template
        const questionMap = {
            // Generic question keys from older assessments (banquet server)
            'q1': 'Tell me about your responsibilities as a banquet server',
            'q2': 'Describe your work experience in restaurants or hospitality', 
            'q3': 'Tell me about a challenging situation you handled at work',
            'q4': 'How do you know if a place setting is correct? Describe it.',
            'q5': 'When pouring wine, which side do you approach from, and why?',
            
            // Specific question keys from newer assessments
            'experience_1': 'Describe your work experience in restaurants or hospitality',
            'experience_2': 'Tell me about your responsibilities in previous roles', 
            'experience_3': 'Tell me about a challenging situation you handled at work',
            'knowledge_setup': 'How do you know if a place setting is correct? Describe it.',
            'knowledge_wine': 'When pouring wine, which side do you approach from, and why?',
            'knowledge_clearing': 'From which side do you clear plates?',
            'knowledge_scenario': 'If a guest says they are vegetarian but their entrée has meat, what do you do?',
            'english_greeting': 'How would you greet a guest when they arrive at your table?',
            'english_complaint': 'If a guest says their food is cold, what do you do?',
            'knowledge_service': 'If a guest is overly intoxicated, how do you handle it?',
            'knowledge_margarita': 'What are the basic ingredients in a Margarita?',
            'knowledge_old_fashioned': 'What are the basics of an Old Fashioned?',
            'knowledge_tools': 'What tools would you use to shake and strain a cocktail?',
            'knowledge_cosmopolitan_glass': 'In what glass would you typically serve a Cosmopolitan?',
            'knowledge_old_fashioned_glass': 'In what glass would you typically serve an Old Fashioned?'
        };
        
        return questionMap[questionKey] || `Question ${questionNumber}`;
    }

    getQuestionText(questionKey) {
        const questionMap = {
            // Experience Questions (all roles)
            'experience_1': 'Work Experience Background',
            'experience_2': 'Employment Timeline', 
            'experience_3': 'Job Responsibilities',
            
            // Bartender Knowledge Questions
            'knowledge_service': 'Responsible Alcohol Service',
            'knowledge_cosmopolitan_glass': 'Cosmopolitan Glassware Knowledge',
            'knowledge_old_fashioned_glass': 'Old Fashioned Glassware Knowledge',
            'knowledge_glassware_1': 'Cosmopolitan Glassware Knowledge',
            'knowledge_glassware_2': 'Old Fashioned Glassware Knowledge',
            'knowledge_margarita': 'Margarita Recipe Knowledge',
            'knowledge_old_fashioned': 'Old Fashioned Recipe Knowledge',
            'knowledge_tools': 'Bartending Tools Knowledge',
            
            // Banquet Server Knowledge Questions
            'knowledge_setup': 'Place Setting Knowledge',
            'knowledge_wine': 'Wine Service Technique',
            'knowledge_clearing': 'Plate Clearing Technique',
            'knowledge_scenario': 'Guest Dietary Issue Handling',
            'english_greeting': 'Guest Greeting Skills',
            'english_complaint': 'Complaint Handling Skills',
            
            // Host Knowledge Questions
            'knowledge_pos': 'POS/Reservation System Experience',
            'knowledge_seating': 'Table Assignment Strategy',
            'knowledge_phone': 'Phone Reservation Etiquette',
            'knowledge_reservation': 'Missing Reservation Handling',
            'knowledge_walkin': 'Large Walk-in Group Management',
            
            // Legacy mappings for older assessments
            'place_setting': 'Place Setting Knowledge',
            'wine_service': 'Wine Service Technique',
            'plate_clearing': 'Plate Clearing Technique',
            'guest_interaction': 'Guest Interaction Skills'
        };
        
        return questionMap[questionKey] || questionKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getOriginalQuestion(questionKey) {
        // Map question keys to the actual questions asked to candidates
        const originalQuestions = {
            // Experience Questions (all roles)
            'experience_1': 'Tell me about where you\'ve worked in restaurants or hospitality',
            'experience_2': 'When did you work in that role?',
            'experience_3': 'What were your main responsibilities in that job?',
            
            // Bartender Knowledge Questions
            'knowledge_service': 'If a guest is overly intoxicated, how do you handle it?',
            'knowledge_cosmopolitan_glass': 'In what glass would you typically serve a Cosmopolitan?',
            'knowledge_old_fashioned_glass': 'In what glass would you typically serve an Old Fashioned?',
            'knowledge_glassware_1': 'In what glass would you typically serve a Cosmopolitan?',
            'knowledge_glassware_2': 'In what glass would you typically serve an Old Fashioned?',
            'knowledge_margarita': 'What are the basic ingredients in a Margarita?',
            'knowledge_old_fashioned': 'What are the basics of an Old Fashioned?',
            'knowledge_tools': 'What tools would you use to shake and strain a cocktail?',
            
            // Banquet Server Knowledge Questions
            'knowledge_setup': 'How do you know if a place setting is correct? Describe it.',
            'knowledge_wine': 'When pouring wine, which side do you approach from, and why?',
            'knowledge_clearing': 'From which side do you clear plates?',
            'knowledge_scenario': 'If a guest says they are vegetarian but their entrée has meat, what do you do?',
            'english_greeting': 'How would you greet a guest when they arrive at your table?',
            'english_complaint': 'If a guest says their food is cold, what do you do?',
            
            // Host Knowledge Questions
            'knowledge_pos': 'Have you used a reservation system like Toast, OpenTable, or Resy? How do you use it?',
            'knowledge_seating': 'When assigning tables, how do you decide where to seat guests?',
            'knowledge_phone': 'What information should you collect when a guest calls to make a reservation?',
            'knowledge_reservation': 'How would you handle a guest who arrives saying they have a reservation, but you don\'t see it in the system?',
            'knowledge_walkin': 'How do you handle a walk-in group of 10 guests?',
            
            // Legacy mappings for older assessments
            'place_setting': 'How do you know if a place setting is correct? Describe it.',
            'wine_service': 'When pouring wine, which side do you approach from, and why?',
            'plate_clearing': 'From which side do you clear plates?',
            'guest_interaction': 'How would you greet a guest when they arrive at your table?'
        };
        
        return originalQuestions[questionKey] || 'Question not available';
    }

    getCandidateAnswer(questionKey, transcripts) {
        // Handle mapping between generic question keys (q1, q2, etc.) and actual transcript keys
        const questionMapping = {
            // Banquet Server mapping (based on question sequence and analysis reasoning)
            'q1': 'experience_2',  // Job responsibilities 
            'q2': 'experience_1',  // Work experience background
            'q3': 'experience_3',  // Challenging situations
            'q4': 'knowledge_setup', // Table setting knowledge
            'q5': 'knowledge_wine'   // Wine service knowledge
        };
        
        // Try mapped key first, then original key, then fallback
        const mappedKey = questionMapping[questionKey];
        if (mappedKey && transcripts[mappedKey]) {
            return transcripts[mappedKey];
        }
        
        return transcripts[questionKey] || 'No response recorded';
    }

    initializeAccordions() {
        // Category accordions
        const categoryHeaders = document.querySelectorAll('.category-header');
        categoryHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const categoryName = header.dataset.category;
                const content = document.querySelector(`[data-category-content="${categoryName}"]`);
                
                header.classList.toggle('active');
                content.classList.toggle('active');
            });
        });

        // Question accordions
        const questionHeaders = document.querySelectorAll('.question-header');
        questionHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const questionKey = header.dataset.question;
                const details = document.querySelector(`[data-question-details="${questionKey}"]`);
                
                header.classList.toggle('active');
                details.classList.toggle('active');
            });
        });
    }

    showError(message) {
        document.getElementById('welcomeState').classList.add('hidden');
        document.getElementById('analysisContent').classList.add('hidden');
        
        const errorContainer = document.getElementById('errorState');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorContainer.classList.remove('hidden');
    }

    retryLoadAnalysis() {
        if (this.selectedAssessment) {
            this.selectAssessment(this.selectedAssessment.id);
        }
    }

    exportAnalysis() {
        if (!this.selectedAssessment) return;
        
        // Create a simple text export of the analysis
        const analysisContent = document.getElementById('analysisContent');
        const content = analysisContent.innerText;
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.selectedAssessment.id}_analysis.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 GravyWork Analysis Dashboard - Initializing...');
    window.analysisDashboard = new AnalysisDashboard();
    console.log('✅ Analysis Dashboard initialized successfully');
});
