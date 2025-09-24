#!/usr/bin/env python3
"""
Compare current audio scripts vs. Atlassian template requirements
"""

import json
import os

def load_current_audio_scripts():
    """Load current audio scripts"""
    try:
        with open('.docs/audio_scripts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_atlassian_template():
    """Load the definitive Atlassian template"""
    try:
        with open('.docs/definitive_audio_recording_template.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def compare_questions():
    """Compare current vs Atlassian questions"""
    current = load_current_audio_scripts()
    atlassian = load_atlassian_template()
    
    print("🔍 CURRENT vs ATLASSIAN TEMPLATE COMPARISON")
    print("="*80)
    
    for role in ['banquet_server', 'bartender', 'host']:
        if role not in atlassian:
            continue
            
        print(f"\n📋 {atlassian[role]['role_name'].upper()}")
        print("-"*60)
        
        current_role = current.get(role, {})
        atlassian_scripts = atlassian[role]['scripts']
        
        for question_key in atlassian[role]['questions_sequence']:
            current_q = current_role.get(question_key, "❌ MISSING")
            atlassian_q = atlassian_scripts[question_key]
            
            if current_q == atlassian_q:
                status = "✅ MATCH"
            elif current_q == "❌ MISSING":
                status = "❌ MISSING"
            else:
                status = "❌ DIFFERENT"
            
            print(f"\n{question_key}:")
            print(f"  Status: {status}")
            print(f"  Atlassian: {atlassian_q}")
            if current_q != "❌ MISSING":
                print(f"  Current:   {current_q}")
    
    print("\n" + "="*80)
    print("🚨 SUMMARY: Current audio files DO NOT match Atlassian template!")
    print("📝 Action Required: Re-record ALL audio files using definitive template")

if __name__ == "__main__":
    compare_questions()
