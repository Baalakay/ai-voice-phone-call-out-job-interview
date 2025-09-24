#!/usr/bin/env python3
"""
Complete LLM Comparison Script
Handles both running comparisons and extracting results to CSV
"""

import json
import boto3
import time
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMComparisonProcessor:
    """Complete LLM comparison processor that runs comparisons and generates CSV output."""
    
    def __init__(self):
        self.bucket_name = 'innovativesol-gravywork-assets-dev'
        self.s3_client = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        
        # Candidate responses for consistent CSV generation
        self.candidate_responses = {
            'bartender': {
                "experience_1": "I worked at Houston's restaurants and McDonald's.",
                "experience_2": "I worked uh last year at McDonald's and This year I worked at uh Houston's.", 
                "experience_3": "Serve drinks to customers, to start new liquor. And take money from patrons.",
                "knowledge_glassware_1": "Low ball",
                "knowledge_glassware_2": "Highball", 
                "knowledge_margarita": "Lime and Triple set and tequila.",
                "knowledge_old_fashioned": "Bourbon and bitters. And lemon",
                "knowledge_tools": "A shaker or strainer.",
                "knowledge_service": "Yes I would, uh, pour their drink out when they're not looking."
            },
            'host': {
                "experience_1": "I worked at um. Um, Whataburger is a host for 3 years.",
                "experience_2": "I worked uh the last 3 years, almost 3 years, um, up until this month, so really like 2 months and uh sorry, 2 years and 8 months.",
                "experience_3": "Uh, greeting and, uh, greeting guests, feeding them, um, signing tables to servers, answering phone calls, um, handling to go orders.",
                "knowledge_pos": "I've used a reservation system but not one of those 3.",
                "knowledge_seating": "Typically flip a coin.",
                "knowledge_phone": "Um, party size, the name, uh, you know, dates and times, uh, get their phone number, and then, you know, special take, um, see if there are any special requests.",
                "knowledge_reservation": "I tell them to um. Screw off, basically. It's not my job.",
                "knowledge_walkin": "Yeah. I would seat 5 at a time."
            }
        }
    
    def find_sample_assessments(self) -> Dict[str, str]:
        """Find one completed assessment for each role."""
        try:
            # List all assessment directories
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='assessments/',
                Delimiter='/'
            )
            
            assessment_dirs = []
            for prefix in response.get('CommonPrefixes', []):
                assessment_id = prefix['Prefix'].split('/')[-2]
                if assessment_id and '_' in assessment_id:
                    assessment_dirs.append(assessment_id)
            
            # Find one assessment per role
            roles = ['bartender', 'host', 'banquet_server']
            samples = {}
            
            for assessment_id in assessment_dirs:
                # Extract role from assessment ID
                parts = assessment_id.split('_')
                if len(parts) >= 1:
                    if parts[0] == 'banquet' and len(parts) > 1 and parts[1] == 'server':
                        role = 'banquet_server'
                    else:
                        role = parts[0].lower()
                    
                    if role in roles and role not in samples:
                        # Verify this assessment has analysis results
                        try:
                            self.s3_client.head_object(
                                Bucket=self.bucket_name,
                                Key=f'assessments/{assessment_id}/analysis_results.json'
                            )
                            samples[role] = assessment_id
                            logger.info(f"✅ Found sample for {role}: {assessment_id}")
                        except:
                            continue
            
            return samples
            
        except Exception as e:
            logger.error(f"Error finding sample assessments: {str(e)}")
            return {}
    
    def run_llm_comparison(self, assessment_id: str, skill_type: str) -> Dict[str, Any]:
        """Run LLM comparison for a specific assessment."""
        try:
            logger.info(f"🔄 Processing {skill_type} assessment: {assessment_id}")
            
            # Invoke the LLM comparison processor
            payload = {
                'assessment_id': assessment_id,
                'skill_type': skill_type
            }
            
            response = self.lambda_client.invoke(
                FunctionName='gravywork-vscode-llm-comparison-processor',
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            result = json.loads(response['Payload'].read().decode('utf-8'))
            
            if result.get('success'):
                logger.info(f"✅ Completed {skill_type} comparison")
                return result
            else:
                logger.error(f"❌ Failed {skill_type} comparison: {result.get('error', 'Unknown error')}")
                return {'success': False, 'error': result.get('error', 'Unknown error')}
                
        except Exception as e:
            logger.error(f"Error running comparison for {assessment_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def load_comparison_results(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Load LLM comparison results from S3."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f'assessments/{assessment_id}/llm_comparison_results.json'
            )
            return json.loads(response['Body'].read().decode('utf-8'))
        except Exception as e:
            logger.warning(f"Could not load comparison results for {assessment_id}: {str(e)}")
            return None
    
    def clean_score(self, score_str) -> str:
        """Extract numeric score from various formats."""
        if isinstance(score_str, (int, float)):
            return str(int(score_str))
        
        score_str = str(score_str)
        if '/' in score_str:
            return score_str.split('/')[0]
        return score_str
    
    def clean_level(self, level_str) -> str:
        """Clean level string to remove emojis and formatting."""
        level_str = str(level_str)
        # Remove emoji characters
        level_str = level_str.replace('🔴', '').replace('🟡', '').replace('🟢', '')
        # Clean up common level names
        level_str = level_str.replace('_', ' ').strip()
        
        level_mapping = {
            'red flag': 'Red Flag',
            'acceptable': 'Acceptable',
            'ideal': 'Ideal',
            'no response': 'No Response'
        }
        
        return level_mapping.get(level_str.lower(), level_str.title())
    
    def generate_csv_output(self, results: Dict[str, Any], output_file: str = 'output/llm_comparison_complete.csv'):
        """Generate comprehensive CSV output from comparison results."""
        csv_rows = []
        headers = [
            'Assessment Type', 'Question', 'Candidate Response',
            'Claude Sonnet 4 Score', 'Claude Sonnet 4 Reasoning',
            'Nova Micro Score', 'Nova Micro Reasoning',
            'Nova Pro Score', 'Nova Pro Reasoning'
        ]
        
        # Process each assessment
        for skill_type, assessment_results in results.items():
            if not assessment_results.get('success'):
                continue
                
            assessment_type = skill_type.replace('_', ' ').title()
            responses = self.candidate_responses.get(skill_type, {})
            
            # Get LLM results
            llm_results = assessment_results.get('results', {})
            
            for question_key in sorted(responses.keys()):
                question_name = question_key.replace('_', ' ').title()
                response = responses[question_key]
                
                # Extract data from each LLM
                claude_data = llm_results.get('claude-sonnet-4', {}).get('analysis', {}).get('question_details', {}).get(question_key, {})
                nova_micro_data = llm_results.get('nova-micro', {}).get('analysis', {}).get('question_details', {}).get(question_key, {})
                nova_pro_data = llm_results.get('nova-pro', {}).get('analysis', {}).get('question_details', {}).get(question_key, {})
                
                # Clean and extract scores and reasoning
                claude_score = self.clean_score(claude_data.get('score', 'N/A'))
                claude_reasoning = claude_data.get('reasoning', 'N/A')
                
                nova_micro_score = self.clean_score(nova_micro_data.get('score', 'N/A'))
                nova_micro_reasoning = nova_micro_data.get('reasoning', 'N/A')
                
                nova_pro_score = self.clean_score(nova_pro_data.get('score', 'N/A'))
                nova_pro_reasoning = nova_pro_data.get('reasoning', 'N/A')
                
                csv_rows.append([
                    assessment_type, question_name, f'"{response}"',
                    claude_score, claude_reasoning,
                    nova_micro_score, nova_micro_reasoning,
                    nova_pro_score, nova_pro_reasoning
                ])
        
        # Write CSV file
        import os
        os.makedirs('output', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Write header
            f.write(','.join(headers) + '\n')
            
            # Write data rows
            for row in csv_rows:
                # Escape quotes and commas in CSV
                escaped_row = []
                for cell in row:
                    cell_str = str(cell)
                    if '"' in cell_str and not (cell_str.startswith('"') and cell_str.endswith('"')):
                        cell_str = cell_str.replace('"', '""')
                    if ',' in cell_str and not (cell_str.startswith('"') and cell_str.endswith('"')):
                        cell_str = f'"{cell_str}"'
                    escaped_row.append(cell_str)
                f.write(','.join(escaped_row) + '\n')
        
        logger.info(f"✅ CSV output written to {output_file}")
        logger.info(f"📊 Total questions analyzed: {len(csv_rows)}")
        return output_file
    
    def generate_performance_metrics_csv(self, results: Dict[str, Any], output_file: str = 'output/llm_performance_metrics_complete.csv'):
        """Generate performance metrics CSV."""
        csv_rows = []
        headers = [
            'Model', 'Assessment Type', 'Processing Time (seconds)', 'Input Tokens', 
            'Output Tokens', 'Total Tokens', 'Accuracy Score', 'Cost Per Assessment'
        ]
        
        # Pricing data (per 1M tokens)
        pricing = {
            'claude-sonnet-4': {'input': 15.00, 'output': 75.00},
            'nova-micro': {'input': 0.35, 'output': 1.40},
            'nova-pro': {'input': 0.80, 'output': 3.20}
        }
        
        for skill_type, assessment_results in results.items():
            if not assessment_results.get('success'):
                continue
                
            assessment_type = skill_type.replace('_', ' ').title()
            llm_results = assessment_results.get('results', {})
            
            for llm_name in ['claude-sonnet-4', 'nova-micro', 'nova-pro']:
                if llm_name not in llm_results:
                    continue
                    
                metrics = llm_results[llm_name].get('metrics', {})
                
                processing_time = metrics.get('llm_processing_time_seconds', 0)
                input_tokens = metrics.get('llm_total_input_tokens', 0)
                output_tokens = metrics.get('llm_total_output_tokens', 0)
                total_tokens = metrics.get('llm_total_tokens', 0)
                accuracy = metrics.get('llm_total_accuracy', 0)
                
                # Calculate cost
                input_cost = (input_tokens / 1_000_000) * pricing[llm_name]['input']
                output_cost = (output_tokens / 1_000_000) * pricing[llm_name]['output']
                total_cost = input_cost + output_cost
                
                csv_rows.append([
                    llm_name.title().replace('-', ' '),
                    assessment_type,
                    f"{processing_time:.2f}",
                    f"{input_tokens:,}",
                    f"{output_tokens:,}",
                    f"{total_tokens:,}",
                    f"{accuracy:.3f}",
                    f"${total_cost:.4f}"
                ])
        
        # Write CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            f.write(','.join(headers) + '\n')
            for row in csv_rows:
                f.write(','.join(row) + '\n')
        
        logger.info(f"✅ Performance metrics written to {output_file}")
        return output_file
    
    def run_complete_analysis(self, use_existing_results: bool = True):
        """Run complete LLM comparison and generate all outputs."""
        print("🚀 Starting Complete LLM Comparison Analysis")
        print("=" * 60)
        
        # Step 1: Load existing results if available
        if use_existing_results and os.path.exists('llm_comparison_results.json'):
            print("📁 Loading existing comparison results...")
            try:
                with open('llm_comparison_results.json', 'r') as f:
                    existing_data = json.load(f)
                
                # Convert to expected format
                all_results = {}
                for assessment_type in ['bartender', 'host']:  # Focus on the two we have data for
                    if assessment_type in existing_data:
                        all_results[assessment_type] = existing_data[assessment_type]
                        
                        # Show metrics summary
                        if 'results' in existing_data[assessment_type]:
                            print(f"\n📊 {assessment_type.upper()} RESULTS:")
                            for llm_name, llm_data in existing_data[assessment_type]['results'].items():
                                metrics = llm_data.get('metrics', {})
                                time_sec = metrics.get('llm_processing_time_seconds', 0)
                                tokens = metrics.get('llm_total_tokens', 0)
                                accuracy = metrics.get('llm_total_accuracy', 0)
                                print(f"   {llm_name}: {time_sec:.2f}s, {tokens:,} tokens, {accuracy:.3f} accuracy")
                
                print(f"✅ Loaded existing results for {len(all_results)} assessments")
                
            except Exception as e:
                print(f"❌ Error loading existing results: {e}")
                use_existing_results = False
        
        if not use_existing_results or not all_results:
            # Step 1: Find sample assessments
            print("🔍 Finding sample assessments...")
            samples = self.find_sample_assessments()
            
            if not samples:
                print("❌ No sample assessments found")
                return
            
            print(f"✅ Found {len(samples)} sample assessments:")
            for role, assessment_id in samples.items():
                print(f"   {role}: {assessment_id}")
            
            # Step 2: Run comparisons
            print("\n🔄 Running LLM comparisons...")
            all_results = {}
            
            for skill_type, assessment_id in samples.items():
                result = self.run_llm_comparison(assessment_id, skill_type)
                if result.get('success'):
                    all_results[skill_type] = result
                    
                    # Show metrics summary
                    if 'results' in result:
                        print(f"\n📊 {skill_type.upper()} RESULTS:")
                        for llm_name, llm_data in result['results'].items():
                            metrics = llm_data.get('metrics', {})
                            time_sec = metrics.get('llm_processing_time_seconds', 0)
                            tokens = metrics.get('llm_total_tokens', 0)
                            accuracy = metrics.get('llm_total_accuracy', 0)
                            print(f"   {llm_name}: {time_sec:.2f}s, {tokens:,} tokens, {accuracy:.3f} accuracy")
            
            if not all_results:
                print("❌ No successful comparisons completed")
                return
        
        # Step 3: Generate CSV outputs
        print("\n📋 Generating CSV outputs...")
        
        # Detailed scoring comparison
        scoring_csv = self.generate_csv_output(all_results)
        
        # Performance metrics
        metrics_csv = self.generate_performance_metrics_csv(all_results)
        
        # Step 4: Save raw results
        results_file = 'llm_comparison_complete_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        print(f"✅ Raw results saved to {results_file}")
        
        # Step 5: Summary
        print("\n" + "=" * 60)
        print("🎉 Complete LLM Comparison Analysis Finished!")
        print("\n📁 Generated Files:")
        print(f"   • {scoring_csv} - Detailed question-by-question scoring")
        print(f"   • {metrics_csv} - Performance and cost metrics")
        print(f"   • {results_file} - Raw comparison results")
        
        return {
            'scoring_csv': scoring_csv,
            'metrics_csv': metrics_csv,
            'results_file': results_file,
            'total_assessments': len(all_results)
        }

def main():
    """Main execution function."""
    processor = LLMComparisonProcessor()
    results = processor.run_complete_analysis()
    
    if results:
        print(f"\n✅ Analysis complete! Processed {results['total_assessments']} assessments.")
    else:
        print("\n❌ Analysis failed or no data processed.")

if __name__ == "__main__":
    main()
