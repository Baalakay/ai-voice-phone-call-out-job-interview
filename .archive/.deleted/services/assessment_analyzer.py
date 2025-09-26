"""
LLM-based Assessment Analysis Service
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import boto3
import os

import sys
import os

# Ensure proper import path for Lambda
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from .transcribe_service import create_transcribe_service
    from ..config.llm_config import get_llm_config
except ImportError:
    # Fallback for Lambda and testing environment
    try:
        from services.transcribe_service import create_transcribe_service
        from config.llm_config import get_llm_config
    except ImportError:
        try:
            from transcribe_service import create_transcribe_service
            from config.llm_config import get_llm_config
        except ImportError:
            # Final fallback - direct module names
            import services.transcribe_service as ts
            import config.llm_config as llm
            create_transcribe_service = ts.create_transcribe_service
            get_llm_config = llm.get_llm_config

logger = logging.getLogger(__name__)

class AssessmentAnalyzer:
    """Service for analyzing assessment transcripts using LLM."""
    
    def __init__(self):
        self.transcribe_service = create_transcribe_service()
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', 'innovativesol-gravywork-assets-dev')
        self.llm_config = get_llm_config()
    
    def analyze_complete_assessment(self, assessment_id: str, skill_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a completed assessment using transcription + LLM evaluation.
        
        Args:
            assessment_id: Assessment identifier
            skill_type: Role type (bartender, banquet_server, host)
            state: Assessment state with responses
            
        Returns:
            Complete assessment analysis results
        """
        try:
            logger.info(f"Starting assessment analysis for {assessment_id} ({skill_type})")
            
            # Step 1: Transcribe all recordings
            transcripts = self.transcribe_service.batch_transcribe_assessment(
                assessment_id, skill_type, state.get('responses', {})
            )
            
            if not transcripts:
                return {
                    'success': False,
                    'error': 'No transcripts generated',
                    'assessment_id': assessment_id
                }
            
            # Step 2: Load assessment criteria
            assessment_templates = self._load_assessment_templates()
            if skill_type not in assessment_templates:
                return {
                    'success': False,
                    'error': f'No template found for skill type: {skill_type}',
                    'assessment_id': assessment_id
                }
            
            criteria = assessment_templates[skill_type]
            
            # Step 3: Generate LLM assessment prompt
            prompt = self._build_assessment_prompt(transcripts, criteria, skill_type)
            
            # Step 4: Send to LLM for analysis
            llm_result = self._analyze_with_bedrock(prompt)
            
            if not llm_result['success']:
                return {
                    'success': False,
                    'error': f'LLM analysis failed: {llm_result["error"]}',
                    'assessment_id': assessment_id
                }
            
            # Step 5: Parse and structure results
            analysis_result = {
                'success': True,
                'assessment_id': assessment_id,
                'skill_type': skill_type,
                'analyzed_at': datetime.utcnow().isoformat(),
                'transcripts': transcripts,
                'llm_analysis': llm_result['analysis'],
                'metadata': {
                    'total_questions': len(transcripts),
                    'transcription_service': 'AWS Transcribe',
                    'llm_service': 'Amazon Bedrock Claude',
                    'assessment_template_version': criteria.get('version', '1.0')
                }
            }
            
            # Step 6: Save results to S3
            self._save_analysis_results(assessment_id, analysis_result)
            
            logger.info(f"Assessment analysis completed for {assessment_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Assessment analysis failed for {assessment_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'assessment_id': assessment_id
            }
    
    def _load_assessment_templates(self) -> Dict[str, Any]:
        """Load assessment templates from data file."""
        try:
            # Try to load from S3 first, then fallback to local file
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key='data/assessment_templates.json'
                )
                return json.loads(response['Body'].read())
            except:
                # Fallback to local file
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                templates_path = os.path.join(current_dir, '..', 'data', 'assessment_templates.json')
                
                with open(templates_path, 'r') as f:
                    return json.load(f)
                    
        except Exception as e:
            logger.error(f"Failed to load assessment templates: {str(e)}")
            return {}
    
    def _build_assessment_prompt(self, transcripts: Dict[str, str], criteria: Dict[str, Any], skill_type: str) -> str:
        """Build comprehensive assessment prompt for LLM."""
        
        role_name = criteria.get('name', skill_type.title())
        
        prompt = f"""You are an expert hospitality industry interviewer evaluating a {role_name} skills assessment.

ROLE: {role_name}
ASSESSMENT CRITERIA:
{json.dumps(criteria, indent=2)}

CANDIDATE RESPONSES:
"""
        
        # Add experience questions
        experience_responses = []
        for i in range(1, 4):  # experience_1, experience_2, experience_3
            question_key = f'experience_{i}'
            if question_key in transcripts:
                experience_responses.append(transcripts[question_key])
        
        if experience_responses:
            prompt += f"""
EXPERIENCE EVALUATION:
The candidate was asked to describe their relevant work experience. Here are their responses:

"""
            for i, response in enumerate(experience_responses, 1):
                prompt += f"Experience Response {i}: \"{response}\"\n\n"
            
            prompt += f"""
Experience Criteria:
- Core Duties: {criteria.get('experience_criteria', {}).get('core_duties', [])}
- Minimum Duties Required: {criteria.get('experience_criteria', {}).get('minimum_duties', 2)}
- Evaluation Standards: {criteria.get('experience_criteria', {}).get('evaluation', {})}

"""
        
        # Add knowledge checks
        knowledge_checks = criteria.get('knowledge_checks', {})
        if knowledge_checks:
            prompt += "KNOWLEDGE EVALUATION:\n\n"
            
            for question_key, check_criteria in knowledge_checks.items():
                if question_key in transcripts:
                    prompt += f"""Question: {check_criteria['question']}
Candidate Response: \"{transcripts[question_key]}\"

Evaluation Criteria:
- Ideal Answer: {check_criteria['ideal']}
- Acceptable Answer: {check_criteria['acceptable']}
- Red Flags: {check_criteria['red_flag']}

"""
        
        # Add English communication (if applicable)
        english_comm = criteria.get('english_communication', {})
        if english_comm:
            prompt += "ENGLISH COMMUNICATION EVALUATION:\n\n"
            
            for comm_type, comm_criteria in english_comm.items():
                question_key = f'english_{comm_type}'
                if question_key in transcripts:
                    prompt += f"""Question: {comm_criteria['question']}
Candidate Response: \"{transcripts[question_key]}\"

Evaluation Criteria:
- Ideal Response: {comm_criteria['ideal']}
- Acceptable Response: {comm_criteria['acceptable']}
- Red Flags: {comm_criteria['red_flag']}

"""
        
        # Assessment instructions
        prompt += """
ASSESSMENT INSTRUCTIONS:

1. EXPERIENCE EVALUATION:
   - Count how many core duties the candidate mentioned
   - Assess if they provided credible workplace/timeframe details
   - Rate as PASS/REVIEW/FAIL based on experience criteria

2. KNOWLEDGE EVALUATION:
   - For each knowledge question, evaluate the response against ideal/acceptable/red_flag criteria
   - Rate each as PASS/REVIEW/FAIL

3. ENGLISH COMMUNICATION EVALUATION (if applicable):
   - Assess clarity, professionalism, and appropriateness of responses
   - Rate each as PASS/REVIEW/FAIL

4. OVERALL RECOMMENDATION:
   - HIRE: Strong candidate, meets most criteria
   - REVIEW: Mixed results, needs human evaluation
   - REJECT: Does not meet minimum requirements

RESPONSE FORMAT:
Provide your assessment as a JSON object with this structure:

{
  "overall_recommendation": "HIRE|REVIEW|REJECT",
  "overall_reasoning": "Brief explanation of overall decision",
  "experience_assessment": {
    "rating": "PASS|REVIEW|FAIL",
    "core_duties_mentioned": ["list of duties mentioned"],
    "core_duties_count": number,
    "credible_details": true|false,
    "reasoning": "explanation"
  },
  "knowledge_assessments": {
    "question_key": {
      "rating": "PASS|REVIEW|FAIL",
      "reasoning": "explanation"
    }
  },
  "english_communication": {
    "question_key": {
      "rating": "PASS|REVIEW|FAIL",
      "reasoning": "explanation"
    }
  },
  "strengths": ["list of candidate strengths"],
  "concerns": ["list of concerns or weaknesses"],
  "recommended_next_steps": "what should happen next"
}

Begin your assessment:"""
        
        return prompt
    
    def _analyze_with_bedrock(self, prompt: str) -> Dict[str, Any]:
        """Send prompt to Bedrock for LLM analysis."""
        try:
            # Prepare request for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.1,  # Low temperature for consistent evaluation
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.llm_config.model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            # Try to parse as JSON
            try:
                analysis_json = json.loads(analysis_text)
                return {
                    'success': True,
                    'analysis': analysis_json,
                    'raw_response': analysis_text
                }
            except json.JSONDecodeError:
                # Return raw text if JSON parsing fails
                return {
                    'success': True,
                    'analysis': {'raw_analysis': analysis_text},
                    'raw_response': analysis_text
                }
                
        except Exception as e:
            logger.error(f"Bedrock analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_analysis_results(self, assessment_id: str, results: Dict[str, Any]) -> None:
        """Save analysis results to S3."""
        try:
            s3_key = f"assessments/{assessment_id}/analysis_results.json"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(results, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Saved analysis results to s3://{self.bucket_name}/{s3_key}")
            
        except Exception as e:
            logger.error(f"Failed to save analysis results: {str(e)}")
    
    def get_analysis_results(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis results from S3."""
        try:
            s3_key = f"assessments/{assessment_id}/analysis_results.json"
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return json.loads(response['Body'].read())
            
        except Exception as e:
            logger.error(f"Failed to retrieve analysis results for {assessment_id}: {str(e)}")
            return None


def create_assessment_analyzer() -> AssessmentAnalyzer:
    """Factory function to create AssessmentAnalyzer instance."""
    return AssessmentAnalyzer()
