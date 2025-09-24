#!/usr/bin/env python3
"""
Deploy the complete LLM assessment analysis system.
"""
import subprocess
import sys
import time
import json

def run_command(command, description):
    """Run a command and return success status."""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"📄 Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"📄 Error: {e.stderr.strip()}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    checks = [
        ("uv --version", "UV package manager"),
        ("aws sts get-caller-identity", "AWS credentials"),
        ("node --version", "Node.js"),
    ]
    
    for command, description in checks:
        if not run_command(command, f"Checking {description}"):
            return False
    
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    
    commands = [
        ("cd functions && uv sync", "Installing Python dependencies"),
        ("npm install", "Installing Node.js dependencies"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def deploy_infrastructure():
    """Deploy the infrastructure with SST."""
    print("🏗️  Deploying infrastructure...")
    
    # Deploy to development stage
    if not run_command("uv run sst deploy --stage dev", "Deploying SST infrastructure"):
        return False
    
    return True

def upload_assessment_templates():
    """Upload assessment templates to S3."""
    print("📄 Uploading assessment templates...")
    
    command = """
aws s3 cp functions/src/data/assessment_templates.json s3://innovativesol-gravywork-assets-dev/data/assessment_templates.json --content-type application/json
"""
    
    if not run_command(command, "Uploading assessment templates to S3"):
        return False
    
    return True

def test_deployment():
    """Test the deployed system."""
    print("🧪 Testing deployment...")
    
    # Run our simple test
    if not run_command("python scripts/test_assessment_simple.py", "Running assessment template tests"):
        return False
    
    return True

def display_deployment_info():
    """Display information about the deployed system."""
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("="*60)
    
    print("""
📊 DEPLOYED COMPONENTS:

✅ Lambda Functions:
   - ProcessingFunction: Handles Twilio webhooks and call flow
   - AssessmentProcessor: Handles LLM analysis after call completion

✅ Infrastructure:
   - API Gateway: Webhook endpoints for Twilio
   - S3 Bucket: Audio files, assessment data, analysis results
   - IAM Permissions: Transcribe, Bedrock, S3, Lambda access

✅ Assessment Analysis Pipeline:
   - AWS Transcribe: Converts recordings to text
   - Amazon Bedrock: LLM analysis using assessment templates
   - S3 Storage: Results stored as JSON files

📋 NEXT STEPS:

1. Test a complete assessment call:
   - Visit the web UI: https://innovativesol-gravywork-assets-dev.s3.amazonaws.com/index.html
   - Select a role and initiate a call
   - Complete the assessment
   - Check S3 for analysis results in: assessments/{assessment_id}/analysis_results.json

2. Monitor the system:
   - CloudWatch Logs: Check Lambda function logs
   - S3 Console: Monitor assessment data and results
   - API Gateway: Monitor webhook performance

3. Review analysis results:
   - Results include transcripts, LLM evaluation, and recommendations
   - Format: JSON with HIRE/REVIEW/REJECT recommendations
   - Location: s3://innovativesol-gravywork-assets-dev/assessments/

⚠️  IMPORTANT NOTES:

- Transcription takes 30-60 seconds per recording
- LLM analysis adds another 10-30 seconds
- Total processing time: 2-5 minutes after call completion
- Results are stored asynchronously in S3

🔧 TROUBLESHOOTING:

- Check CloudWatch Logs if analysis doesn't complete
- Verify AWS Transcribe permissions if transcription fails
- Ensure Bedrock access is enabled in your AWS account
""")

def main():
    """Main deployment function."""
    print("🚀 Starting LLM Assessment System Deployment\n")
    
    steps = [
        (check_prerequisites, "Prerequisites Check"),
        (install_dependencies, "Dependencies Installation"),
        (deploy_infrastructure, "Infrastructure Deployment"),
        (upload_assessment_templates, "Assessment Templates Upload"),
        (test_deployment, "Deployment Testing"),
    ]
    
    for step_func, step_name in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            print(f"\n❌ Deployment failed at: {step_name}")
            return 1
        print(f"✅ {step_name} completed")
    
    display_deployment_info()
    return 0

if __name__ == "__main__":
    exit(main())
