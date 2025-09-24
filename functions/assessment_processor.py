"""
Assessment Processing Lambda Function

Handles post-call assessment analysis using transcription and LLM evaluation.
"""
import json
import logging
from typing import Dict, Any

import sys
import os

# Add the src directory to the path for Lambda execution
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.services.assessment_analyzer import create_assessment_analyzer
from src.functions.webhook_simple import get_assessment_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for processing completed assessments.
    
    Expected event format:
    {
        "assessment_id": "uuid",
        "skill_type": "bartender|banquet_server|host"
    }
    """
    try:
        logger.info(f"Assessment processing started: {json.dumps(event)}")
        
        # Extract parameters
        assessment_id = event.get('assessment_id')
        skill_type = event.get('skill_type')
        
        if not assessment_id or not skill_type:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameters: assessment_id and skill_type'
                })
            }
        
        # Get assessment state
        state = get_assessment_state(assessment_id, skill_type)
        if not state or not state.get('responses'):
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'success': False,
                    'error': f'No assessment data found for {assessment_id}'
                })
            }
        
        # Create analyzer and process assessment
        analyzer = create_assessment_analyzer()
        analysis_result = analyzer.analyze_complete_assessment(
            assessment_id, skill_type, state
        )
        
        if analysis_result['success']:
            logger.info(f"Assessment analysis completed successfully for {assessment_id}")
            
            # Extract key results for response
            llm_analysis = analysis_result.get('llm_analysis', {})
            overall_recommendation = llm_analysis.get('overall_recommendation', 'REVIEW')
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'assessment_id': assessment_id,
                    'skill_type': skill_type,
                    'recommendation': overall_recommendation,
                    'analysis_completed_at': analysis_result['analyzed_at'],
                    'transcripts_count': len(analysis_result.get('transcripts', {})),
                    'results_location': f's3://innovativesol-gravywork-assets-dev/assessments/{assessment_id}/analysis_results.json'
                })
            }
        else:
            logger.error(f"Assessment analysis failed for {assessment_id}: {analysis_result['error']}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'assessment_id': assessment_id,
                    'error': analysis_result['error']
                })
            }
            
    except Exception as e:
        logger.error(f"Assessment processing error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


def handle_assessment_completion(assessment_id: str, skill_type: str) -> Dict[str, Any]:
    """
    Convenience function to trigger assessment analysis.
    Can be called from other Lambda functions.
    """
    event = {
        'assessment_id': assessment_id,
        'skill_type': skill_type
    }
    
    return lambda_handler(event, None)
