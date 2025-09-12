"""
Real Assessment Prompts based on GravyWork Skill Assessment Templates
Source: https://gravywork.atlassian.net/wiki/x/CQB-Nw

These prompts use the exact evaluation criteria from GravyWork's official documentation.
"""

def get_assessment_prompt(skill_type: str, transcript: str) -> str:
    """Generate assessment prompt with real GravyWork evaluation criteria."""
    
    prompts = {
        'banquet_server': f"""
You are evaluating a BANQUET SERVER / FOOD RUNNER candidate based on GravyWork's official assessment criteria.

INTERVIEW TRANSCRIPT:
{transcript}

EVALUATION CRITERIA FROM GRAVYWORK ASSESSMENT TEMPLATE:

EXPERIENCE & RESPONSIBILITIES (Must mention 3+ duties):
✓ Required duties: 
  - Set up / break down event space (linens, flatware, buffet stations)
  - Serve food and beverages (deliver plated meals, pour/refill wine/water)
  - Follow course sequence (appetizer/salad → entrée → dessert)
  - Clear and reset tables (pre-bussing, full resets)
  - Guest interaction (greet guests, handle requests)
  - Team communication (work with captains, kitchen, bartenders)

• PASS: Credible workplace/timeframe + ≥2 duties mentioned
• REVIEW: Vague workplace, no timeframe, or only 1 duty  
• FAIL: No workplace/timeframe, no relevant duties

KNOWLEDGE CHECKS:
1. Place Setting: IDEAL = Forks left (salad outside, entrée inside), knife/spoon right, napkin folded, bread plate with butter knife above forks, wine glass at tip of knife, water glass above/right, aligned. ACCEPTABLE = Multiple correct placements. RED FLAG = Vague/incorrect.

2. Wine Service: IDEAL = From the right, because glasses are on right and beverages served from right. ACCEPTABLE = "From the right". RED FLAG = "From the left" or "Doesn't matter".

3. Clearing: IDEAL = From the right, to avoid reaching across guests. ACCEPTABLE = "Usually from the right". RED FLAG = "From the left".

4. Guest Scenario: IDEAL = Apologize, notify captain/chef, offer alternative, ensure satisfaction. ACCEPTABLE = "Tell the chef and replace it". RED FLAG = "Ignore them" or "Tell them to eat it".

ENGLISH COMMUNICATION:
• Greeting: IDEAL = "Good evening, welcome! May I start you with water or a drink?" ACCEPTABLE = "Hello, how are you today?" RED FLAG = One-word reply or non-English.
• Complaint: IDEAL = "I'm so sorry about that. I'll take it back and have it fixed right away." ACCEPTABLE = "I'll bring it back to the kitchen." RED FLAG = "Not my problem" or "Just eat it".

PROVIDE ASSESSMENT:
- Overall Qualification: APPROVED / NEEDS REVIEW / REJECTED
- Experience Score: PASS / REVIEW / FAIL (with specific reasoning based on duties mentioned)
- Knowledge Score: Rate each question as IDEAL / ACCEPTABLE / RED FLAG 
- English Score: PASS / REVIEW / FAIL
- Key Strengths: What they demonstrated well
- Areas of Concern: What needs improvement or was missing
- Recommendation: Specific hiring recommendation with clear reasoning

Use ONLY the criteria above. Be thorough but concise.
        """,
        
        'bartender': f"""
You are evaluating a BARTENDER candidate based on GravyWork's official assessment criteria.

INTERVIEW TRANSCRIPT:
{transcript}

EVALUATION CRITERIA FROM GRAVYWORK ASSESSMENT TEMPLATE:

EXPERIENCE & RESPONSIBILITIES (Must mention 3+ duties):
✓ Required duties:
  - Preparing and serving drinks (cocktails, beer, wine, non-alcoholic)
  - Setting up and maintaining the bar (stocking, cleaning, organizing tools/glassware)
  - Taking and processing orders, handling payments
  - Guest engagement (recommendations, answering drink/menu questions)
  - Responsible alcohol service (checking IDs, cutting off intoxicated guests)
  - Coordinating with servers and barbacks

• PASS: ≥1 credible workplace + timeframe + ≥3 duties
• REVIEW: Only 2 duties OR vague
• FAIL: No workplace/timeframe OR irrelevant duties

KNOWLEDGE CHECKS:
1. Glassware: IDEAL = Cosmopolitan in martini/cocktail glass, Old Fashioned in lowball/rocks glass. ACCEPTABLE = "Cosmo in cocktail glass, Old Fashioned in short glass". RED FLAG = Wrong or vague.

2. Margarita: IDEAL = Tequila, triple sec/orange liqueur, lime juice, salt rim. ACCEPTABLE = "Tequila, lime, triple sec". RED FLAG = Leaves out tequila or nonsense recipe.

3. Old Fashioned: IDEAL = Whiskey/bourbon, bitters, sugar, orange garnish. ACCEPTABLE = "Whiskey, bitters, sugar". RED FLAG = Misses whiskey or invents ingredients.

4. Tools: IDEAL = Shaker tin, strainer (Hawthorne/fine mesh), jigger. ACCEPTABLE = "Shaker and strainer". RED FLAG = Doesn't know tools or says "just pour it".

5. Responsible Service: IDEAL = Politely cut them off, offer water, suggest food, offer taxi/ride. ACCEPTABLE = "Stop serving and give water". RED FLAG = "Keep serving" or ignores issue.

CRITICAL REQUIREMENTS: 
- This role requires FLUENT ENGLISH communication
- Must demonstrate RESPONSIBLE ALCOHOL SERVICE judgment
- This is a guest-facing role with high standards

PROVIDE ASSESSMENT:
- Overall Qualification: APPROVED / NEEDS REVIEW / REJECTED  
- Experience Score: PASS / REVIEW / FAIL (with specific reasoning based on duties mentioned)
- Knowledge Score: Rate each question as IDEAL / ACCEPTABLE / RED FLAG
- English Fluency: EXCELLENT / GOOD / POOR (critical evaluation)
- Responsible Service: DEMONSTRATED / UNCLEAR / CONCERNING
- Key Strengths: What they demonstrated well
- Areas of Concern: What needs improvement or was missing
- Recommendation: Specific hiring recommendation with clear reasoning

This is a high-responsibility role. Apply strict standards for alcohol service and English communication.
        """,
        
        'host': f"""
You are evaluating a HOST candidate based on GravyWork's official assessment criteria.

INTERVIEW TRANSCRIPT:
{transcript}

EVALUATION CRITERIA FROM GRAVYWORK ASSESSMENT TEMPLATE:

EXPERIENCE & RESPONSIBILITIES (Must mention 3+ duties):
✓ Required duties:
  - Greeting and seating guests
  - Managing reservations and waitlists (POS/reservation system)
  - Assigning tables based on server sections / bandwidth
  - Answering phone calls, taking guest info
  - Handling to-go orders over the phone
  - Managing special requests (large parties, celebrations)
  - Resolving discrepancies (lost reservations, unexpected party sizes)

• PASS: ≥1 credible workplace + timeframe + ≥3 duties
• REVIEW: Only 2 duties OR vague
• FAIL: No workplace/timeframe OR irrelevant duties

KNOWLEDGE CHECKS:
1. POS Systems: IDEAL = Create/update reservations, check guest notes, manage table flow, update waitlist. ACCEPTABLE = "Yes, I enter guest info and track tables". RED FLAG = "No, never used it" (unless strong other experience).

2. Seating Logic: IDEAL = Balance server sections, spread tables based on bandwidth, consider guest preferences. ACCEPTABLE = "Seat them where there's open table, but try to spread evenly". RED FLAG = "Seat randomly" or "First table I see".

3. Phone Etiquette: IDEAL = Name, party size, time/date, phone number, special notes (allergies, celebrations). ACCEPTABLE = "Name, time, party size". RED FLAG = Doesn't know what to ask.

4. Lost Reservations: IDEAL = Apologize, try to accommodate (find table, offer waitlist priority), communicate clearly. ACCEPTABLE = "Tell them I'll try to fit them in". RED FLAG = "Tell them to leave" or "Not my problem".

5. Large Walk-ins: IDEAL = Check if space can be rearranged, note wait time, split into sections if needed, flag servers for support. ACCEPTABLE = "Tell them wait time, try to seat together". RED FLAG = "Seat anywhere without checking" or refuse without explanation.

CRITICAL REQUIREMENTS:
- This role requires EXCELLENT ENGLISH communication
- Must demonstrate strong CUSTOMER SERVICE skills
- This is the first impression guests receive - high standards essential

PROVIDE ASSESSMENT:
- Overall Qualification: APPROVED / NEEDS REVIEW / REJECTED
- Experience Score: PASS / REVIEW / FAIL (with specific reasoning based on duties mentioned) 
- Knowledge Score: Rate each question as IDEAL / ACCEPTABLE / RED FLAG
- English Communication: EXCELLENT / GOOD / POOR (critical evaluation)
- Problem-Solving: STRONG / ADEQUATE / WEAK
- Customer Service Attitude: EXCELLENT / GOOD / POOR
- Key Strengths: What they demonstrated well
- Areas of Concern: What needs improvement or was missing
- Recommendation: Specific hiring recommendation with clear reasoning

This role sets the first impression. Apply high standards for communication and service orientation.
        """
    }
    
    return prompts.get(skill_type, prompts['banquet_server'])

def get_system_prompt() -> str:
    """System prompt for all assessments using GravyWork standards."""
    return """
You are a senior hospitality recruiter with 15+ years of experience at high-end restaurants and event venues. 

You evaluate candidates using GravyWork's exact assessment criteria with no deviation from their documented standards.

Key evaluation principles:
• Apply criteria objectively and consistently
• Use specific examples from candidate responses  
• Flag borderline cases for human review with clear reasoning
• Maintain high standards for guest-facing positions (Bartender, Host)
• Consider safety implications (responsible alcohol service, food handling)
• Evaluate English communication critically for guest-facing roles
• Document both strengths and concerns clearly

Your assessments directly impact hiring decisions for hospitality positions. Be thorough, fair, and professional while maintaining GravyWork's quality standards.
"""

def get_experience_evaluation_prompt(skill_type: str, responses: list, template_data: dict) -> str:
    """Generate focused experience evaluation prompt."""
    
    core_duties = template_data['experience_criteria']['core_duties']
    evaluation_criteria = template_data['experience_criteria']['evaluation']
    
    return f"""
Evaluate the EXPERIENCE section for this {skill_type} candidate.

CANDIDATE RESPONSES TO EXPERIENCE QUESTIONS:
{' '.join(responses)}

REQUIRED CORE DUTIES (must mention {template_data['experience_criteria']['minimum_duties']}+ of these):
{chr(10).join(f"• {duty}" for duty in core_duties)}

EVALUATION CRITERIA:
• PASS: {evaluation_criteria['pass']}
• REVIEW: {evaluation_criteria['review']}
• FAIL: {evaluation_criteria['fail']}

PROVIDE:
1. Score: PASS / REVIEW / FAIL
2. Duties mentioned: List specific duties candidate described
3. Workplace credibility: Assessment of workplace/timeframe mentioned
4. Reasoning: Why you gave this score
5. Recommendation: Should they advance to knowledge checks?
"""

def get_knowledge_evaluation_prompt(skill_type: str, responses: dict, template_data: dict) -> str:
    """Generate focused knowledge evaluation prompt."""
    
    knowledge_checks = template_data['knowledge_checks']
    
    prompt = f"""
Evaluate the KNOWLEDGE CHECKS for this {skill_type} candidate.

CANDIDATE RESPONSES BY QUESTION:
"""
    
    for question_key, response in responses.items():
        if question_key in knowledge_checks:
            criteria = knowledge_checks[question_key]
            prompt += f"""
QUESTION: {criteria['question']}
RESPONSE: {response}
IDEAL: {criteria['ideal']}
ACCEPTABLE: {criteria['acceptable']}
RED FLAG: {criteria['red_flag']}
---
"""
    
    prompt += """
FOR EACH QUESTION, PROVIDE:
1. Score: IDEAL / ACCEPTABLE / RED FLAG
2. Reasoning: Why you gave this score
3. Specific examples: Quote relevant parts of their response

OVERALL KNOWLEDGE ASSESSMENT:
- Total questions answered at IDEAL level: X/Y
- Total questions answered at ACCEPTABLE level: X/Y  
- Total RED FLAGS: X/Y
- Overall knowledge competency: STRONG / ADEQUATE / WEAK
- Recommendation: Qualified for this role based on technical knowledge?
"""
    
    return prompt
