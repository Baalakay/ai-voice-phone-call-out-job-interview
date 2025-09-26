#!/usr/bin/env python3
"""
Comprehensive comparison of Voice AI questions vs Atlassian template requirements.
"""

def get_atlassian_requirements():
    """Exact requirements from Atlassian documentation"""
    return {
        "banquet_server": {
            "experience_questions": {
                "experience_1": {
                    "atlassian_exact": "Tell me about where you've worked as a banquet server or food runner.",
                    "current_voice_ai": "Tell me about where you've worked as a banquet server.",
                    "status": "MISMATCH - Missing 'or food runner'"
                },
                "experience_2": {
                    "atlassian_exact": "When did you work in that role? (encourages rough timeframe — years/seasons/events, not exact dates)",
                    "current_voice_ai": "When did you work in that role? You can give me approximate timeframes like years or seasons.",
                    "status": "CLOSE - Good but missing 'events' option"
                },
                "experience_3": {
                    "atlassian_exact": "And what were your main responsibilities in that job?",
                    "current_voice_ai": "And what were your main responsibilities in that job?",
                    "status": "EXACT MATCH"
                }
            },
            "knowledge_questions": {
                "knowledge_setup": {
                    "atlassian_exact": "How do you know if a place setting is correct? Describe it.",
                    "current_voice_ai": "How do you know if a place setting is correct? Describe it.",
                    "status": "EXACT MATCH"
                },
                "knowledge_wine": {
                    "atlassian_exact": "When pouring wine, which side do you approach from, and why?",
                    "current_voice_ai": "When pouring wine, which side do you approach from, and why?",
                    "status": "EXACT MATCH"
                },
                "knowledge_clearing": {
                    "atlassian_exact": "From which side do you clear plates?",
                    "current_voice_ai": "From which side do you clear plates?",
                    "status": "EXACT MATCH"
                },
                "knowledge_scenario": {
                    "atlassian_exact": "If a guest says they are vegetarian but their entrée has meat, what do you do?",
                    "current_voice_ai": "If a guest says they are vegetarian but their entrée has meat, what do you do?",
                    "status": "EXACT MATCH"
                }
            },
            "english_questions": {
                "english_greeting": {
                    "atlassian_exact": "How would you greet a guest when they arrive at your table?",
                    "current_voice_ai": "How would you greet a guest when they arrive at your table?",
                    "status": "EXACT MATCH"
                },
                "english_complaint": {
                    "atlassian_exact": "If a guest says their food is cold, what do you do?",
                    "current_voice_ai": "If a guest says their food is cold, what do you do?",
                    "status": "EXACT MATCH"
                }
            }
        }
    }

def get_other_voice_ai_discrepancies():
    """Other voice AI question discrepancies found in different files"""
    return {
        "generate_complete_audio_set.py": {
            "experience_1": "Tell me about your banquet or catering experience. Where have you worked and for how long?",
            "experience_2": "What specific duties did you perform as a banquet server or food runner?",
            "experience_3": "Describe a challenging banquet event you worked and how you handled it.",
            "knowledge_scenario": "A guest complains their steak is overcooked. What do you do?",
            "english_greeting": "Please greet a table of guests in English.",
            "english_complaint": "A guest says their food is cold. Respond in English.",
            "status": "COMPLETELY DIFFERENT - Multiple files have different questions!"
        }
    }

def print_comprehensive_analysis():
    """Print detailed analysis of question mismatches"""
    atlassian = get_atlassian_requirements()
    other_discrepancies = get_other_voice_ai_discrepancies()
    
    print("🔍 COMPREHENSIVE VOICE AI QUESTION ANALYSIS")
    print("="*80)
    
    print("\n📋 BANQUET SERVER QUESTION COMPARISON")
    print("-"*50)
    
    # Experience Questions
    print("\n1️⃣ EXPERIENCE QUESTIONS:")
    for key, data in atlassian["banquet_server"]["experience_questions"].items():
        status_icon = "✅" if "EXACT MATCH" in data["status"] else "❌"
        print(f"   {status_icon} {key}:")
        print(f"      Atlassian: {data['atlassian_exact']}")
        print(f"      Voice AI:  {data['current_voice_ai']}")
        print(f"      Status:    {data['status']}")
        print()
    
    # Knowledge Questions
    print("2️⃣ KNOWLEDGE QUESTIONS:")
    for key, data in atlassian["banquet_server"]["knowledge_questions"].items():
        status_icon = "✅" if "EXACT MATCH" in data["status"] else "❌"
        print(f"   {status_icon} {key}:")
        print(f"      Question: {data['current_voice_ai']}")
        print(f"      Status:   {data['status']}")
        print()
    
    # English Questions
    print("3️⃣ ENGLISH COMMUNICATION QUESTIONS:")
    for key, data in atlassian["banquet_server"]["english_questions"].items():
        status_icon = "✅" if "EXACT MATCH" in data["status"] else "❌"
        print(f"   {status_icon} {key}:")
        print(f"      Question: {data['current_voice_ai']}")
        print(f"      Status:   {data['status']}")
        print()
    
    # Other Discrepancies
    print("4️⃣ CRITICAL DISCOVERY - MULTIPLE QUESTION VERSIONS:")
    print("❌ Found COMPLETELY DIFFERENT questions in generate_complete_audio_set.py:")
    for question, text in other_discrepancies["generate_complete_audio_set.py"].items():
        if question != "status":
            print(f"   • {question}: {text}")
    print()
    
    print("🚨 CRITICAL ISSUES IDENTIFIED:")
    print("-"*40)
    print("❌ experience_1: Missing 'or food runner' in current voice AI")
    print("❌ experience_2: Missing 'events' as timeframe option")
    print("❌ MULTIPLE FILES: Different scripts exist with completely different questions!")
    print("❌ INCONSISTENCY: Voice AI may be using wrong question set")
    print()
    
    print("✅ AREAS WORKING CORRECTLY:")
    print("-"*40)
    print("✅ knowledge_setup, knowledge_wine, knowledge_clearing, knowledge_scenario: EXACT MATCH")
    print("✅ english_greeting, english_complaint: EXACT MATCH") 
    print("✅ experience_3: EXACT MATCH")
    print()
    
    print("🔧 REQUIRED FIXES:")
    print("-"*40)
    print("1. Update experience_1 to include 'or food runner'")
    print("2. Update experience_2 to include 'events' as timeframe option")  
    print("3. Ensure ONLY ONE consistent set of questions across all files")
    print("4. Verify voice AI is using the correct audio_scripts.json")
    print("5. Remove/consolidate conflicting question definitions")

if __name__ == "__main__":
    print_comprehensive_analysis()
