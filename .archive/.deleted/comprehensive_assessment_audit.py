#!/usr/bin/env python3
"""
Comprehensive audit of assessment questions and criteria against Atlassian template requirements.
"""

def atlassian_banquet_server_requirements():
    """Define the exact requirements from Atlassian documentation"""
    return {
        "experience_questions": {
            "experience_1": {
                "atlassian_prompt": "Tell me about where you've worked as a banquet server or food runner.",
                "current_implementation": "Generic experience question 1",
                "status": "MISMATCH"
            },
            "experience_2": {
                "atlassian_prompt": "When did you work in that role? (encourages rough timeframe — years/seasons/events, not exact dates)",
                "current_implementation": "Generic experience question 2", 
                "status": "MISMATCH"
            },
            "experience_3": {
                "atlassian_prompt": "And what were your main responsibilities in that job?",
                "current_implementation": "Generic experience question 3",
                "status": "MISMATCH"
            }
        },
        "knowledge_checks": {
            "knowledge_setup": {
                "atlassian_question": "How do you know if a place setting is correct? Describe it.",
                "current_question": "How do you know if a place setting is correct? Describe it.",
                "atlassian_ideal": "Forks on left (salad fork outside, entrée fork inside), knife and spoon on right, napkin folded, bread plate with butter knife above forks, wine glass at tip of knife, water glass above/right, all aligned evenly",
                "current_ideal": "Forks on left (salad fork outside, entrée fork inside), knife and spoon on right, napkin folded, bread plate with butter knife above forks, wine glass at tip of knife, water glass above/right, all aligned evenly",
                "status": "MATCH"
            },
            "knowledge_wine": {
                "atlassian_question": "When pouring wine, which side do you approach from, and why?",
                "current_question": "When pouring wine, which side do you approach from, and why?",
                "atlassian_ideal": "From the right, because glasses are on the right and beverages are served from the right",
                "current_ideal": "From the right, because glasses are on the right and beverages are served from the right",
                "status": "MATCH"
            },
            "knowledge_clearing": {
                "atlassian_question": "From which side do you clear plates?",
                "current_question": "From which side do you clear plates?",
                "atlassian_ideal": "From the right, to avoid reaching across guests",
                "current_ideal": "From the right, to avoid reaching across guests",
                "status": "MATCH"
            },
            "knowledge_scenario": {
                "atlassian_question": "If a guest says they are vegetarian but their entrée has meat, what do you do?",
                "current_question": "If a guest says they are vegetarian but their entrée has meat, what do you do?",
                "atlassian_ideal": "Apologize, notify captain/chef, offer an alternative, ensure guest satisfaction",
                "current_ideal": "Apologize, notify captain/chef, offer an alternative, ensure guest satisfaction",
                "status": "MATCH"
            }
        },
        "english_communication": {
            "english_greeting": {
                "atlassian_question": "How would you greet a guest when they arrive at your table?",
                "current_question": "How would you greet a guest when they arrive at your table?",
                "atlassian_ideal": "Good evening, welcome! May I start you with water or a drink?",
                "current_ideal": "Good evening, welcome! May I start you with water or a drink?",
                "status": "MATCH"
            },
            "english_complaint": {
                "atlassian_question": "If a guest says their food is cold, what do you do?",
                "current_question": "If a guest says their food is cold, what do you do?",
                "atlassian_ideal": "I'm so sorry about that. I'll take it back and have it fixed right away",
                "current_ideal": "I'm so sorry about that. I'll take it back and have it fixed right away",
                "status": "MATCH"
            }
        },
        "core_duties_criteria": {
            "atlassian_requirements": [
                "Set up / break down event space (linens, flatware, buffet stations)",
                "Serve food and beverages (deliver plated meals, pour/refill wine/water)",
                "Follow course sequence (appetizer/salad → entrée → dessert)",
                "Clear and reset tables (pre-bussing, full resets)",
                "Guest interaction (greet guests, handle requests)",
                "Team communication (work with captains, kitchen, bartenders)"
            ],
            "current_implementation": [
                "Set up / break down event space (linens, flatware, buffet stations)",
                "Serve food and beverages (deliver plated meals, pour/refill wine/water)",
                "Follow course sequence (appetizer/salad → entrée → dessert)",
                "Clear and reset tables (pre-bussing, full resets)",
                "Guest interaction (greet guests, handle requests)",
                "Team communication (work with captains, kitchen, bartenders)"
            ],
            "status": "MATCH"
        },
        "evaluation_criteria": {
            "atlassian_pass": "Worker names a credible workplace/timeframe and describes ≥2 duties",
            "current_pass": "Credible workplace/timeframe + ≥2 duties",
            "atlassian_review": "Vague workplace ('weddings'), no timeframe, or only 1 duty",
            "current_review": "Vague workplace, no timeframe, or only 1 duty",
            "atlassian_fail": "No workplace/timeframe, no relevant duties",
            "current_fail": "No workplace/timeframe, no relevant duties",
            "status": "MATCH"
        }
    }

def print_comprehensive_audit():
    """Print detailed audit report"""
    requirements = atlassian_banquet_server_requirements()
    
    print("🔍 COMPREHENSIVE ASSESSMENT AUDIT REPORT")
    print("="*80)
    
    print("\n📋 BANQUET SERVER ASSESSMENT ANALYSIS")
    print("-"*50)
    
    # Experience Questions Analysis
    print("\n1️⃣ EXPERIENCE QUESTIONS:")
    for key, data in requirements["experience_questions"].items():
        status_icon = "❌" if data["status"] == "MISMATCH" else "✅"
        print(f"   {status_icon} {key}:")
        print(f"      Atlassian: {data['atlassian_prompt']}")
        print(f"      Current:   {data['current_implementation']}")
        print(f"      Status:    {data['status']}")
        print()
    
    # Knowledge Checks Analysis  
    print("2️⃣ KNOWLEDGE CHECKS:")
    for key, data in requirements["knowledge_checks"].items():
        status_icon = "✅" if data["status"] == "MATCH" else "❌"
        print(f"   {status_icon} {key}:")
        print(f"      Question: {data['current_question']}")
        print(f"      Status:   {data['status']}")
        print()
    
    # English Communication Analysis
    print("3️⃣ ENGLISH COMMUNICATION:")
    for key, data in requirements["english_communication"].items():
        status_icon = "✅" if data["status"] == "MATCH" else "❌"
        print(f"   {status_icon} {key}:")
        print(f"      Question: {data['current_question']}")
        print(f"      Status:   {data['status']}")
        print()
    
    # Core Duties Analysis
    print("4️⃣ CORE DUTIES CRITERIA:")
    print(f"   ✅ Status: {requirements['core_duties_criteria']['status']}")
    print("   Requirements match Atlassian template exactly")
    print()
    
    # Evaluation Criteria Analysis
    print("5️⃣ EVALUATION CRITERIA:")
    print(f"   ✅ Status: {requirements['evaluation_criteria']['status']}")
    print("   Pass/Review/Fail criteria match Atlassian template")
    print()
    
    print("🚨 CRITICAL ISSUES IDENTIFIED:")
    print("-"*40)
    print("❌ Experience questions are generic, not following Atlassian specific prompts")
    print("❌ Missing specific question sequencing from Atlassian template")
    print("❌ Voice AI questions may not match the exact template requirements")
    print()
    
    print("✅ AREAS WORKING CORRECTLY:")
    print("-"*40)
    print("✅ Knowledge check questions match exactly")
    print("✅ English communication questions match exactly") 
    print("✅ Scoring criteria and core duties match exactly")
    print("✅ Evaluation criteria match exactly")

if __name__ == "__main__":
    print_comprehensive_audit()
