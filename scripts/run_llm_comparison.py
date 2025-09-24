#!/usr/bin/env python3
"""
Script to run LLM comparison on sample assessments.

Tests Claude Haiku, Nova Micro, and Nova Pro on one assessment per role.
"""

import json
import boto3
import sys
import os
from typing import Dict, Any, List

# Add the functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions'))

from src.functions.llm_comparison_processor import LLMComparisonProcessor


def find_sample_assessments() -> Dict[str, str]:
    """Find one completed assessment for each role."""
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    
    # Role mapping
    roles = ['bartender', 'banquet_server', 'host']
    samples = {}
    
    try:
        # List all assessment directories
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='assessments/',
            Delimiter='/'
        )
        
        assessment_dirs = []
        for prefix in response.get('CommonPrefixes', []):
            assessment_id = prefix['Prefix'].split('/')[-2]
            if assessment_id and '_' in assessment_id:
                assessment_dirs.append(assessment_id)
        
        # Find one assessment per role
        for assessment_id in assessment_dirs:
            # Extract role from assessment ID pattern
            parts = assessment_id.split('_')
            if len(parts) >= 1:
                role = parts[0].lower()
                if role in roles and role not in samples:
                    # Check if this assessment has analysis results
                    try:
                        s3_client.head_object(
                            Bucket=bucket_name,
                            Key=f'assessments/{assessment_id}/analysis_results.json'
                        )
                        samples[role] = assessment_id
                        print(f"✅ Found sample for {role}: {assessment_id}")
                    except s3_client.exceptions.NoSuchKey:
                        continue
            
            # Stop when we have all roles
            if len(samples) == len(roles):
                break
        
        return samples
        
    except Exception as e:
        print(f"❌ Error finding sample assessments: {str(e)}")
        return {}


def run_comparison_for_samples(samples: Dict[str, str]) -> Dict[str, Any]:
    """Run LLM comparison for each sample assessment."""
    processor = LLMComparisonProcessor()
    results = {}
    
    for role, assessment_id in samples.items():
        print(f"\n🔄 Processing {role} assessment: {assessment_id}")
        
        try:
            result = processor.compare_llms_for_assessment(assessment_id, role)
            
            if result['success']:
                results[role] = result
                print(f"✅ Completed {role} comparison")
                
                # Print summary metrics
                for llm_name, llm_result in result['results'].items():
                    if 'metrics' in llm_result:
                        metrics = llm_result['metrics']
                        print(f"   {llm_name}:")
                        print(f"     Processing Time: {metrics.get('llm_processing_time_seconds', 0):.2f}s")
                        print(f"     Input Tokens: {metrics.get('llm_total_input_tokens', 0)}")
                        print(f"     Output Tokens: {metrics.get('llm_total_output_tokens', 0)}")
                        print(f"     Total Tokens: {metrics.get('llm_total_tokens', 0)}")
                        if 'llm_total_accuracy' in metrics:
                            print(f"     Accuracy: {metrics['llm_total_accuracy']:.3f}")
            else:
                print(f"❌ Failed {role} comparison: {result.get('error', 'Unknown error')}")
                results[role] = result
                
        except Exception as e:
            print(f"❌ Exception processing {role}: {str(e)}")
            results[role] = {'success': False, 'error': str(e)}
    
    return results


def generate_summary_report(results: Dict[str, Any]) -> None:
    """Generate a summary report of the comparison results."""
    print("\n" + "="*80)
    print("📊 LLM COMPARISON SUMMARY REPORT")
    print("="*80)
    
    # Aggregate metrics across all roles
    llm_metrics = {
        'claude-sonnet-4': {'total_time': 0, 'total_tokens': 0, 'total_accuracy': 0, 'count': 0},
        'nova-micro': {'total_time': 0, 'total_tokens': 0, 'total_accuracy': 0, 'count': 0},
        'nova-pro': {'total_time': 0, 'total_tokens': 0, 'total_accuracy': 0, 'count': 0}
    }
    
    for role, result in results.items():
        if result.get('success') and 'results' in result:
            print(f"\n📋 {role.upper()} RESULTS:")
            
            for llm_name, llm_result in result['results'].items():
                if 'metrics' in llm_result:
                    metrics = llm_result['metrics']
                    
                    # Update aggregates
                    llm_metrics[llm_name]['total_time'] += metrics.get('llm_processing_time_seconds', 0)
                    llm_metrics[llm_name]['total_tokens'] += metrics.get('llm_total_tokens', 0)
                    llm_metrics[llm_name]['total_accuracy'] += metrics.get('llm_total_accuracy', 0)
                    llm_metrics[llm_name]['count'] += 1
                    
                    print(f"  {llm_name}:")
                    print(f"    Time: {metrics.get('llm_processing_time_seconds', 0):.2f}s")
                    print(f"    Tokens: {metrics.get('llm_total_tokens', 0)}")
                    print(f"    Accuracy: {metrics.get('llm_total_accuracy', 0):.3f}")
                    
                    if 'error' in llm_result:
                        print(f"    Error: {llm_result['error']}")
    
    # Print averages
    print(f"\n📈 AVERAGE PERFORMANCE ACROSS ALL ROLES:")
    print("-" * 50)
    
    for llm_name, data in llm_metrics.items():
        if data['count'] > 0:
            avg_time = data['total_time'] / data['count']
            avg_tokens = data['total_tokens'] / data['count']
            avg_accuracy = data['total_accuracy'] / data['count']
            
            print(f"{llm_name}:")
            print(f"  Average Time: {avg_time:.2f}s")
            print(f"  Average Tokens: {avg_tokens:.0f}")
            print(f"  Average Accuracy: {avg_accuracy:.3f}")
            print()


def main():
    """Main execution function."""
    print("🚀 Starting LLM Comparison for GravyWork Assessment Platform")
    print("="*70)
    
    # Step 1: Find sample assessments
    print("🔍 Finding sample assessments (one per role)...")
    samples = find_sample_assessments()
    
    if not samples:
        print("❌ No sample assessments found. Please ensure you have completed assessments in S3.")
        return 1
    
    print(f"✅ Found {len(samples)} sample assessments:")
    for role, assessment_id in samples.items():
        print(f"   {role}: {assessment_id}")
    
    # Step 2: Run comparisons
    print("\n🔄 Running LLM comparisons...")
    results = run_comparison_for_samples(samples)
    
    # Step 3: Generate report
    generate_summary_report(results)
    
    # Step 4: Save full results
    output_file = 'llm_comparison_results.json'
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Full results saved to: {output_file}")
    except Exception as e:
        print(f"⚠️ Failed to save results file: {str(e)}")
    
    print("\n🎉 LLM Comparison completed!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
