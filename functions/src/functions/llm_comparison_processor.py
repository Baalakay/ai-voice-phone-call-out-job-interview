"""
LLM Comparison Processor for GravyWork Assessment Platform

Compares performance of multiple LLMs (Claude Haiku, Nova Micro, Nova Pro)
using the same assessment data and collects comprehensive metrics.
"""

import json
import time
import boto3
import logging
from typing import Dict, Any, List, Optional

# Handle scipy import gracefully
try:
    from scipy.stats import pearsonr
except ImportError:
    # Fallback correlation calculation if scipy not available
    def pearsonr(x, y):
        import math
        n = len(x)
        if n < 2:
            return 0.0, 1.0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x2 = sum(xi*xi for xi in x)
        sum_y2 = sum(yi*yi for yi in y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        
        numerator = n*sum_xy - sum_x*sum_y
        denominator = math.sqrt((n*sum_x2 - sum_x*sum_x) * (n*sum_y2 - sum_y*sum_y))
        
        if denominator == 0:
            return 0.0, 1.0
        
        correlation = numerator / denominator
        return correlation, 0.0  # p-value not calculated

# Import our existing modules
from ..config.llm_config import get_llm_config, create_inference_config
from .bedrock_service import BedrockService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LLMComparisonProcessor:
    """Processes assessments with multiple LLMs and compares performance."""
    
    def __init__(self):
        """Initialize the comparison processor."""
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'innovativesol-gravywork-assets-dev'
        
        # LLM configurations for comparison
        self.llm_configs = {
            "claude-sonnet-4": get_llm_config("claude-sonnet-4"),
            "nova-micro": get_llm_config("nova-micro"), 
            "nova-pro": get_llm_config("nova-pro")
        }
        
        # Initialize Bedrock services
        self.bedrock_services = {}
        for name, config in self.llm_configs.items():
            self.bedrock_services[name] = BedrockService(config)
    
    def compare_llms_for_assessment(self, assessment_id: str, skill_type: str) -> Dict[str, Any]:
        """
        Process the same assessment with all three LLMs and collect metrics.
        
        Args:
            assessment_id: The assessment ID to process
            skill_type: The skill type (bartender, banquet_server, host)
            
        Returns:
            Dict containing results and metrics for all LLMs
        """
        logger.info(f"Starting LLM comparison for assessment {assessment_id}, skill {skill_type}")
        
        try:
            # Load the existing transcripts for this assessment
            transcripts = self._load_assessment_transcripts(assessment_id)
            if not transcripts:
                return {
                    'success': False,
                    'error': f'No transcripts found for assessment {assessment_id}'
                }
            
            # Load the assessment prompt
            prompt = self._build_assessment_prompt(transcripts, skill_type)
            
            # Process with each LLM
            results = {}
            for llm_name in self.llm_configs.keys():
                logger.info(f"Processing with {llm_name}")
                
                start_time = time.time()
                llm_result = self._analyze_with_llm(llm_name, prompt)
                processing_time = time.time() - start_time
                
                if llm_result['success']:
                    results[llm_name] = {
                        'analysis': llm_result['analysis'],
                        'metrics': {
                            'llm_processing_time_seconds': processing_time,
                            'llm_total_input_tokens': llm_result['usage']['inputTokens'],
                            'llm_total_output_tokens': llm_result['usage']['outputTokens'],
                            'llm_total_tokens': llm_result['usage']['totalTokens']
                        }
                    }
                else:
                    results[llm_name] = {
                        'error': llm_result['error'],
                        'metrics': {
                            'llm_processing_time_seconds': processing_time,
                            'llm_total_input_tokens': 0,
                            'llm_total_output_tokens': 0,
                            'llm_total_tokens': 0
                        }
                    }
            
            # Calculate accuracy metrics using Claude Sonnet 4 as baseline
            if 'claude-sonnet-4' in results and results['claude-sonnet-4'].get('analysis'):
                baseline = results['claude-sonnet-4']['analysis']
                
                for llm_name in ['nova-micro', 'nova-pro']:
                    if llm_name in results and results[llm_name].get('analysis'):
                        accuracy_metrics = self._calculate_accuracy_metrics(
                            baseline, results[llm_name]['analysis']
                        )
                        results[llm_name]['metrics'].update(accuracy_metrics)
                
                # Claude Sonnet 4 gets perfect accuracy against itself
                results['claude-sonnet-4']['metrics']['llm_total_accuracy'] = 1.0
                results['claude-sonnet-4']['metrics']['score_correlation'] = 1.0
                results['claude-sonnet-4']['metrics']['recommendation_accuracy'] = 1.0
            
            # Save comparison results
            self._save_comparison_results(assessment_id, skill_type, results)
            
            return {
                'success': True,
                'assessment_id': assessment_id,
                'skill_type': skill_type,
                'results': results,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"LLM comparison failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_assessment_transcripts(self, assessment_id: str) -> Optional[Dict[str, str]]:
        """Load existing transcripts for an assessment."""
        try:
            # Try to load from existing analysis results
            key = f"assessments/{assessment_id}/analysis_results.json"
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            
            return data.get('transcripts', {})
            
        except Exception as e:
            logger.error(f"Failed to load transcripts for {assessment_id}: {str(e)}")
            return None
    
    def _build_assessment_prompt(self, transcripts: Dict[str, str], skill_type: str) -> str:
        """Build the assessment prompt - reuse existing logic."""
        # Import the existing prompt building logic
        from .assessment_processor_simple import build_assessment_prompt_simple
        return build_assessment_prompt_simple(transcripts, skill_type)
    
    def _analyze_with_llm(self, llm_name: str, prompt: str) -> Dict[str, Any]:
        """Analyze with a specific LLM using Converse API."""
        try:
            bedrock_service = self.bedrock_services[llm_name]
            
            messages = [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]
            
            # Use Converse API for proper token counting
            response = bedrock_service.invoke_converse_api(messages)
            
            # Extract the response content
            analysis_text = response['output']['message']['content'][0]['text']
            
            # Extract usage metrics
            usage = response.get('usage', {})
            
            # Try to parse as JSON
            try:
                analysis_json = json.loads(analysis_text)
                
                # Format the analysis using existing logic
                from .assessment_processor_simple import format_analysis_for_humans
                formatted_analysis = format_analysis_for_humans(analysis_json, llm_name.split('-')[0])
                
                return {
                    'success': True,
                    'analysis': formatted_analysis,
                    'usage': usage,
                    'raw_response': analysis_text
                }
                
            except json.JSONDecodeError:
                # Return structured response if JSON parsing fails
                return {
                    'success': True,
                    'analysis': {
                        'overall_recommendation': 'REVIEW',
                        'overall_reasoning': 'Analysis completed but response format needs review',
                        'raw_analysis': analysis_text
                    },
                    'usage': usage,
                    'raw_response': analysis_text
                }
                
        except Exception as e:
            logger.error(f"LLM analysis failed for {llm_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'usage': {'inputTokens': 0, 'outputTokens': 0, 'totalTokens': 0}
            }
    
    def _calculate_accuracy_metrics(self, baseline: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, float]:
        """Calculate accuracy metrics between baseline and comparison analysis."""
        try:
            metrics = {}
            
            # 1. Recommendation accuracy (PASS/REVIEW/FAIL match)
            baseline_rec = baseline.get('overall_recommendation', 'REVIEW')
            comparison_rec = comparison.get('overall_recommendation', 'REVIEW')
            metrics['recommendation_accuracy'] = 1.0 if baseline_rec == comparison_rec else 0.0
            
            # 2. Score correlation for individual questions
            baseline_scores = []
            comparison_scores = []
            
            # Extract question scores from both analyses
            baseline_questions = baseline.get('question_details', {})
            comparison_questions = comparison.get('question_details', {})
            
            for question_key in baseline_questions.keys():
                if question_key in comparison_questions:
                    baseline_score = baseline_questions[question_key].get('score', 5)
                    comparison_score = comparison_questions[question_key].get('score', 5)
                    baseline_scores.append(baseline_score)
                    comparison_scores.append(comparison_score)
            
            # Calculate Pearson correlation if we have enough data points
            if len(baseline_scores) >= 2:
                correlation, _ = pearsonr(baseline_scores, comparison_scores)
                metrics['score_correlation'] = max(0.0, correlation)  # Ensure non-negative
            else:
                metrics['score_correlation'] = 0.0
            
            # 3. Category score accuracy (within 1 point tolerance)
            category_matches = 0
            total_categories = 0
            
            baseline_categories = baseline.get('category_breakdown', {})
            comparison_categories = comparison.get('category_breakdown', {})
            
            for category in baseline_categories.keys():
                if category in comparison_categories:
                    baseline_avg = baseline_categories[category].get('average_score', 5)
                    comparison_avg = comparison_categories[category].get('average_score', 5)
                    
                    # Consider it a match if within 1 point
                    if abs(baseline_avg - comparison_avg) <= 1.0:
                        category_matches += 1
                    total_categories += 1
            
            metrics['category_accuracy'] = category_matches / total_categories if total_categories > 0 else 0.0
            
            # 4. Overall accuracy (weighted average)
            metrics['llm_total_accuracy'] = (
                metrics['recommendation_accuracy'] * 0.4 +
                metrics['score_correlation'] * 0.4 +
                metrics['category_accuracy'] * 0.2
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate accuracy metrics: {str(e)}")
            return {
                'llm_total_accuracy': 0.0,
                'recommendation_accuracy': 0.0,
                'score_correlation': 0.0,
                'category_accuracy': 0.0
            }
    
    def _save_comparison_results(self, assessment_id: str, skill_type: str, results: Dict[str, Any]) -> None:
        """Save comparison results to S3."""
        try:
            key = f"assessments/{assessment_id}/llm_comparison_results.json"
            
            comparison_data = {
                'assessment_id': assessment_id,
                'skill_type': skill_type,
                'timestamp': time.time(),
                'results': results
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(comparison_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Saved LLM comparison results to {key}")
            
        except Exception as e:
            logger.error(f"Failed to save comparison results: {str(e)}")


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Lambda handler for LLM comparison processing."""
    try:
        processor = LLMComparisonProcessor()
        
        # Extract parameters from event
        assessment_id = event.get('assessment_id')
        skill_type = event.get('skill_type')
        
        if not assessment_id or not skill_type:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing assessment_id or skill_type'
                })
            }
        
        # Process comparison
        result = processor.compare_llms_for_assessment(assessment_id, skill_type)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
