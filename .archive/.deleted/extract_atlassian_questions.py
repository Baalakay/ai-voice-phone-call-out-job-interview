#!/usr/bin/env python3
"""
Extract EXACT questions from Atlassian template for all three roles.
Based on: https://gravywork.atlassian.net/wiki/spaces/GWIS/pages/931069961/Skill+Assessment+Templates
"""

def get_atlassian_exact_questions():
    """Return the EXACT questions from the Atlassian documentation"""
    
    return {
        "banquet_server": {
            "role_name": "Banquet Server / Food Runner",
            "language_requirement": "bilingual",
            "intro_note": "This interview can be conducted in English or Spanish. Which language would you prefer? Please say English or Spanish.",
            "questions": {
                "intro": "Hi, I'm calling about your application for a banquet server position. This interview can be conducted in English or Spanish. Which language would you prefer? Please say English or Spanish.",
                
                # EXPERIENCE & RESPONSIBILITIES (3-part sequence from Atlassian)
                "experience_1": "Tell me about where you've worked as a banquet server or food runner.",
                "experience_2": "When did you work in that role?",  # Note: Atlassian says "encourages rough timeframe — years/seasons/events, not exact dates"
                "experience_3": "And what were your main responsibilities in that job?",
                
                # KNOWLEDGE CHECKS (4 questions from Atlassian)
                "knowledge_setup": "How do you know if a place setting is correct? Describe it.",
                "knowledge_wine": "When pouring wine, which side do you approach from, and why?", 
                "knowledge_clearing": "From which side do you clear plates?",
                "knowledge_scenario": "If a guest says they are vegetarian but their entrée has meat, what do you do?",
                
                # ENGLISH COMMUNICATION (2 questions from Atlassian)
                "english_greeting": "How would you greet a guest when they arrive at your table?",
                "english_complaint": "If a guest says their food is cold, what do you do?",
                
                "goodbye": "Thank you for completing the assessment. We'll review your responses and be in touch within the next few days. Have a great day!"
            }
        },
        
        "bartender": {
            "role_name": "Bartender", 
            "language_requirement": "english_only",
            "intro_note": "This interview is conducted in English since bartenders must be able to interact with guests in English. If you are not comfortable continuing in English, you may end the interview here.",
            "questions": {
                "intro": "Hi, I'm calling about your bartender application. This interview is conducted in English since bartenders must be able to interact with guests in English. If you are not comfortable continuing in English, you may end the interview here.",
                
                # EXPERIENCE & RESPONSIBILITIES (3-part sequence from Atlassian)
                "experience_1": "Tell me about where you've worked as a bartender.",
                "experience_2": "When did you work in that role?",
                "experience_3": "And what were your main responsibilities?",
                
                # KNOWLEDGE CHECKS (5 questions from Atlassian)
                "knowledge_glassware_1": "In what glass would you typically serve a Cosmopolitan?",
                "knowledge_glassware_2": "In what glass would you typically serve an Old Fashioned?", 
                "knowledge_margarita": "What are the basic ingredients in a Margarita?",
                "knowledge_old_fashioned": "What are the basics of an Old Fashioned?",
                "knowledge_tools": "What tools would you use to shake and strain a cocktail?",
                "knowledge_service": "If a guest is overly intoxicated, how do you handle it?",
                
                "goodbye": "Thank you for completing the assessment. We'll review your responses and be in touch within the next few days. Have a great day!"
            }
        },
        
        "host": {
            "role_name": "Host",
            "language_requirement": "english_only", 
            "intro_note": "This interview is conducted in English since hosts must be able to interact with guests in English. If you are not comfortable continuing in English, you may end the interview here.",
            "questions": {
                "intro": "Hi, I'm calling about your host application. This interview is conducted in English since hosts must be able to interact with guests in English. If you are not comfortable continuing in English, you may end the interview here.",
                
                # EXPERIENCE & RESPONSIBILITIES (3-part sequence from Atlassian)
                "experience_1": "Tell me about where you've worked as a host.",
                "experience_2": "When did you work in that role?",
                "experience_3": "And what were your main responsibilities?",
                
                # KNOWLEDGE CHECKS (5 questions from Atlassian)
                "knowledge_pos": "Have you used a reservation system like Toast, OpenTable, or Resy? How do you use it?",
                "knowledge_seating": "When assigning tables, how do you decide where to seat guests?",
                "knowledge_phone": "What information should you collect when a guest calls to make a reservation?",
                "knowledge_reservation": "How would you handle a guest who arrives saying they have a reservation, but you don't see it in the system?",
                "knowledge_walkin": "How do you handle a walk-in group of 10 guests?",
                
                "goodbye": "Thank you for completing the assessment. We'll review your responses and be in touch within the next few days. Have a great day!"
            }
        }
    }

def print_all_questions():
    """Print all questions for review"""
    questions = get_atlassian_exact_questions()
    
    print("🎙️ EXACT QUESTIONS FROM ATLASSIAN TEMPLATE FOR RE-RECORDING")
    print("="*80)
    
    for role_key, role_data in questions.items():
        print(f"\n📋 {role_data['role_name'].upper()}")
        print(f"Language Requirement: {role_data['language_requirement']}")
        print("-" * 60)
        
        for question_key, question_text in role_data['questions'].items():
            print(f"{question_key:20} | {question_text}")
        
        print(f"\nTotal Questions: {len(role_data['questions'])}")
    
    return questions

if __name__ == "__main__":
    questions = print_all_questions()
    
    print("\n🔍 QUESTION COUNT SUMMARY:")
    print("-" * 40)
    for role_key, role_data in questions.items():
        count = len(role_data['questions'])
        print(f"{role_data['role_name']:25} | {count:2} questions")
    
    total = sum(len(role_data['questions']) for role_data in questions.values())
    print(f"{'TOTAL AUDIO FILES NEEDED':25} | {total:2} files")
