#!/usr/bin/env python3
"""
Generate final summary of recording requirements
"""

def print_recording_summary():
    print("🎙️ ELEVENLABS RE-RECORDING REQUIREMENTS SUMMARY")
    print("="*80)
    
    print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
    print("-"*40)
    print("❌ BANQUET SERVER: knowledge_scenario question NOT being asked in voice calls")
    print("❌ BARTENDER: Missing split glassware questions (cosmopolitan vs old fashioned)")
    print("❌ ALL ROLES: experience_2 has extra guidance text not in Atlassian template")
    print("❌ BARTENDER & HOST: experience_3 has different wording")
    
    print("\n📋 FILES REQUIRING RE-RECORDING:")
    print("-"*40)
    
    files_to_rerecord = [
        # Banquet Server
        ("banquet_server/experience_2.mp3", "Remove extra guidance text"),
        ("banquet_server/knowledge_scenario.mp3", "CRITICAL - This question is not being asked!"),
        
        # Bartender  
        ("bartender/experience_2.mp3", "Remove extra guidance text"),
        ("bartender/experience_3.mp3", "Change 'in that job' to just 'responsibilities'"),
        ("bartender/knowledge_cosmopolitan_glass.mp3", "NEW FILE - Split from combined question"),
        ("bartender/knowledge_old_fashioned_glass.mp3", "NEW FILE - Split from combined question"),
        
        # Host
        ("host/experience_2.mp3", "Remove extra guidance text"),
        ("host/experience_3.mp3", "Change 'in that job' to just 'responsibilities'"),
    ]
    
    for filename, reason in files_to_rerecord:
        print(f"  📄 {filename:35} | {reason}")
    
    print(f"\n📊 RECORDING STATISTICS:")
    print("-"*40)
    print(f"Total files needing re-recording: {len(files_to_rerecord)}")
    print(f"New files needed: 2 (bartender glassware split)")
    print(f"Modified files: {len(files_to_rerecord) - 2}")
    
    print("\n✅ DEFINITIVE TEMPLATE LOCATION:")
    print("-"*40)
    print("📂 .docs/definitive_audio_recording_template.json")
    print("🌐 Source: https://gravywork.atlassian.net/wiki/spaces/GWIS/pages/931069961/Skill+Assessment+Templates")
    
    print("\n🎯 NEXT STEPS:")
    print("-"*40)
    print("1. Use .docs/definitive_audio_recording_template.json for ElevenLabs")
    print("2. Re-record the 8 files listed above")
    print("3. Upload to S3 with exact filename structure")
    print("4. Test new assessment to verify knowledge_scenario is asked")
    print("5. Update system to use new question sequence for bartender glassware")

if __name__ == "__main__":
    print_recording_summary()
