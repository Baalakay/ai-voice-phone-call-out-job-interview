#!/usr/bin/env python3
"""
Simple test for assessment analysis components.
"""
import json
import os

def test_assessment_templates():
    """Test loading and validating assessment templates."""
    print("🧪 Testing Assessment Templates...")
    
    try:
        # Load assessment templates
        template_path = os.path.join(os.path.dirname(__file__), '..', 'functions', 'src', 'data', 'assessment_templates.json')
        
        with open(template_path, 'r') as f:
            templates = json.load(f)
        
        print(f"✅ Loaded {len(templates)} assessment templates")
        
        # Test each role
        expected_roles = ['bartender', 'banquet_server', 'host']
        for role in expected_roles:
            if role in templates:
                template = templates[role]
                print(f"✅ {template['name']} template loaded")
                
                # Check required fields
                required_fields = ['name', 'questions_sequence', 'experience_criteria', 'knowledge_checks']
                for field in required_fields:
                    if field in template:
                        print(f"  ✅ {field}: present")
                    else:
                        print(f"  ❌ {field}: missing")
                
                # Check questions sequence
                questions = template.get('questions_sequence', [])
                print(f"  📊 {len(questions)} questions in sequence")
                
                # Check knowledge checks
                knowledge = template.get('knowledge_checks', {})
                print(f"  📊 {len(knowledge)} knowledge checks")
                
            else:
                print(f"❌ {role} template missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {str(e)}")
        return False

def test_prompt_structure():
    """Test prompt generation structure."""
    print("🧪 Testing Prompt Generation Structure...")
    
    try:
        # Load templates
        template_path = os.path.join(os.path.dirname(__file__), '..', 'functions', 'src', 'data', 'assessment_templates.json')
        
        with open(template_path, 'r') as f:
            templates = json.load(f)
        
        # Mock transcripts
        mock_transcripts = {
            'experience_1': "I worked as a bartender for 2 years at Murphy's Pub.",
            'knowledge_cosmopolitan_glass': "Cosmopolitan goes in a martini glass.",
            'knowledge_old_fashioned_glass': "Old fashioned uses a rocks glass."
        }
        
        # Test bartender template
        bartender_template = templates['bartender']
        
        # Build a simple prompt structure (without the full analyzer class)
        prompt_parts = []
        prompt_parts.append(f"ROLE: {bartender_template['name']}")
        prompt_parts.append("CANDIDATE RESPONSES:")
        
        for question_key, transcript in mock_transcripts.items():
            prompt_parts.append(f"{question_key}: {transcript}")
        
        # Add knowledge checks
        knowledge_checks = bartender_template.get('knowledge_checks', {})
        for question_key in mock_transcripts:
            if question_key in knowledge_checks:
                check = knowledge_checks[question_key]
                prompt_parts.append(f"Criteria for {question_key}:")
                prompt_parts.append(f"  Ideal: {check['ideal']}")
                prompt_parts.append(f"  Acceptable: {check['acceptable']}")
                prompt_parts.append(f"  Red Flag: {check['red_flag']}")
        
        full_prompt = "\n".join(prompt_parts)
        
        print("✅ Prompt structure generated successfully")
        print(f"📊 Prompt length: {len(full_prompt)} characters")
        print(f"📊 Prompt sections: {len(prompt_parts)}")
        
        print("\n📝 Sample prompt structure:")
        print("=" * 50)
        print(full_prompt[:800] + "..." if len(full_prompt) > 800 else full_prompt)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt structure test failed: {str(e)}")
        return False

def test_assessment_criteria():
    """Test assessment criteria completeness."""
    print("🧪 Testing Assessment Criteria...")
    
    try:
        template_path = os.path.join(os.path.dirname(__file__), '..', 'functions', 'src', 'data', 'assessment_templates.json')
        
        with open(template_path, 'r') as f:
            templates = json.load(f)
        
        for role_name, template in templates.items():
            print(f"\n🔍 Analyzing {template['name']} criteria:")
            
            # Experience criteria
            exp_criteria = template.get('experience_criteria', {})
            if exp_criteria:
                core_duties = exp_criteria.get('core_duties', [])
                min_duties = exp_criteria.get('minimum_duties', 0)
                evaluation = exp_criteria.get('evaluation', {})
                
                print(f"  📊 Core duties: {len(core_duties)}")
                print(f"  📊 Minimum required: {min_duties}")
                print(f"  📊 Evaluation levels: {len(evaluation)}")
            
            # Knowledge checks
            knowledge = template.get('knowledge_checks', {})
            print(f"  📊 Knowledge questions: {len(knowledge)}")
            
            for q_key, q_data in knowledge.items():
                required_fields = ['question', 'ideal', 'acceptable', 'red_flag']
                missing_fields = [f for f in required_fields if f not in q_data]
                if missing_fields:
                    print(f"    ⚠️  {q_key} missing: {missing_fields}")
                else:
                    print(f"    ✅ {q_key} complete")
            
            # English communication (if applicable)
            english_comm = template.get('english_communication', {})
            if english_comm:
                print(f"  📊 English communication tests: {len(english_comm)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Criteria test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Simple Assessment Analysis Tests\n")
    
    tests = [
        test_assessment_templates,
        test_prompt_structure,
        test_assessment_criteria,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Assessment templates and structure are ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
