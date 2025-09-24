"""
Simplified, Self-Contained Assessment Processor

No complex imports - everything needed is included directly.
"""
import json
import logging
import boto3
import time
import requests
import os
from datetime import datetime
from typing import Dict, Any, Optional
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assessment templates embedded directly (no imports needed)
ASSESSMENT_TEMPLATES = {
    "banquet_server": {
        "name": "Banquet Server / Food Runner",
        "scoring_categories": {
            "baseline": {
                "name": "Baseline Criteria",
                "questions": ["english_greeting", "english_complaint"],
                "description": "Basic English customer service ability and polite, helpful tone"
            },
            "experience": {
                "name": "Experience & Responsibilities", 
                "questions": ["experience_1", "experience_2", "experience_3"],
                "description": "Credibility check for relevant work experience and responsibilities"
            },
            "knowledge": {
                "name": "Knowledge Checks",
                "questions": ["knowledge_setup", "knowledge_wine", "knowledge_clearing", "knowledge_scenario"],
                "description": "Technical knowledge of banquet service procedures"
            }
        },
        "experience_criteria": {
            "core_duties": [
                "Set up / break down event space (linens, flatware, buffet stations)",
                "Serve food and beverages (deliver plated meals, pour/refill wine/water)",
                "Follow course sequence (appetizer/salad → entrée → dessert)",
                "Clear and reset tables (pre-bussing, full resets)",
                "Guest interaction (greet guests, handle requests)",
                "Team communication (work with captains, kitchen, bartenders)"
            ],
            "minimum_duties": 3,
            "evaluation": {
                "pass": "Credible workplace/timeframe + ≥2 duties",
                "review": "Vague workplace, no timeframe, or only 1 duty",
                "fail": "No workplace/timeframe, no relevant duties"
            }
        },
        "knowledge_checks": {
            "place_setting": {
                "question": "How do you know if a place setting is correct? Describe it.",
                "ideal": "Forks on left (salad fork outside, entrée fork inside), knife and spoon on right, napkin folded, bread plate with butter knife above forks, wine glass at tip of knife, water glass above/right, all aligned evenly",
                "acceptable": "Mentions multiple correct placements (e.g., fork left, knife right, glasses on right)",
                "red_flag": "Vague/incorrect (e.g., \"just put forks and plates\")",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "wine_service": {
                "question": "When pouring wine, which side do you approach from, and why?",
                "ideal": "From the right, because glasses are on the right and beverages are served from the right",
                "acceptable": "From the right",
                "red_flag": "From the left / Doesn't matter",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "clearing": {
                "question": "From which side do you clear plates?",
                "ideal": "From the right, to avoid reaching across guests",
                "acceptable": "Usually from the right",
                "red_flag": "From the left",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "guest_scenario": {
                "question": "If a guest says they are vegetarian but their entrée has meat, what do you do?",
                "ideal": "Apologize, notify captain/chef, offer an alternative, ensure guest satisfaction",
                "acceptable": "Tell the chef and replace it",
                "red_flag": "Ignore them, Tell them to eat it",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            }
        },
        "english_communication": {
            "greeting": {
                "question": "How would you greet a guest when they arrive at your table?",
                "ideal": "Good evening, welcome! May I start you with water or a drink?",
                "acceptable": "Hello, how are you today?",
                "red_flag": "One-word reply (Hi) / non-English",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "complaint": {
                "question": "If a guest says their food is cold, what do you do?",
                "ideal": "I'm so sorry about that. I'll take it back and have it fixed right away",
                "acceptable": "I'll bring it back to the kitchen",
                "red_flag": "Not my problem, Just eat it",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            }
        }
    },
    "bartender": {
        "name": "Bartender",
        "scoring_categories": {
            "baseline": {
                "name": "Baseline Criteria",
                "questions": ["knowledge_service"],
                "description": "English fluency and responsible alcohol service judgment"
            },
            "experience": {
                "name": "Experience & Responsibilities", 
                "questions": ["experience_1", "experience_2", "experience_3"],
                "description": "Credibility check for relevant bartending experience and responsibilities"
            },
            "knowledge": {
                "name": "Knowledge Checks",
                "questions": ["knowledge_glassware_1", "knowledge_glassware_2", "knowledge_margarita", "knowledge_old_fashioned", "knowledge_tools"],
                "description": "Technical knowledge of bartending skills, glassware, recipes, and tools"
            }
        },
        "experience_criteria": {
            "core_duties": [
                "Preparing and serving drinks (cocktails, beer, wine, non-alcoholic)",
                "Setting up and maintaining the bar (stocking, cleaning, organizing tools/glassware)",
                "Taking and processing orders, handling payments",
                "Guest engagement (recommendations, answering drink/menu questions)",
                "Responsible alcohol service (checking IDs, cutting off intoxicated guests)",
                "Coordinating with servers and barbacks"
            ],
            "minimum_duties": 3,
            "evaluation": {
                "pass": "≥1 credible workplace + timeframe and ≥3 duties",
                "review": "Only 2 duties OR vague",
                "fail": "No workplace/timeframe OR irrelevant duties"
            }
        },
        "knowledge_checks": {
            "glassware_1": {
                "question": "In what glass would you typically serve a Cosmopolitan?",
                "ideal": "Martini glass or cocktail glass",
                "acceptable": "Cocktail glass or martini-style glass",
                "red_flag": "Wrong glass (rocks, highball, etc.) or vague answer",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "glassware_2": {
                "question": "In what glass would you typically serve an Old Fashioned?",
                "ideal": "Lowball glass, rocks glass, or old fashioned glass",
                "acceptable": "Short glass, rocks glass, or whiskey glass",
                "red_flag": "Wrong glass (martini, highball, etc.) or vague answer",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "margarita": {
                "question": "What are the basic ingredients in a Margarita?",
                "ideal": "Tequila, triple sec/orange liqueur, lime juice, salt rim",
                "acceptable": "Tequila, lime, triple sec",
                "red_flag": "Leaves out tequila or nonsense recipe",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "old_fashioned": {
                "question": "What are the basics of an Old Fashioned?",
                "ideal": "Whiskey/bourbon, bitters, sugar, orange garnish",
                "acceptable": "Whiskey, bitters, sugar",
                "red_flag": "Misses whiskey or invents ingredients",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "tools": {
                "question": "What tools would you use to shake and strain a cocktail?",
                "ideal": "Shaker tin, strainer (Hawthorne/fine mesh), jigger",
                "acceptable": "Shaker and strainer",
                "red_flag": "Doesn't know tools / says just pour it",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "responsible_service": {
                "question": "If a guest is overly intoxicated, how do you handle it?",
                "ideal": "Politely cut them off, offer water, suggest food, offer taxi/ride",
                "acceptable": "Stop serving and give water",
                "red_flag": "Keep serving / ignores issue",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            }
        }
    },
    "host": {
        "name": "Host",
        "scoring_categories": {
            "baseline": {
                "name": "Baseline Criteria",
                "questions": ["knowledge_phone", "knowledge_reservation"],
                "description": "English fluency and professional customer service demonstrated through phone etiquette and guest interaction"
            },
            "experience": {
                "name": "Experience & Responsibilities", 
                "questions": ["experience_1", "experience_2", "experience_3"],
                "description": "Credibility check for relevant host experience and responsibilities"
            },
            "knowledge": {
                "name": "Knowledge Checks",
                "questions": ["knowledge_pos", "knowledge_seating", "knowledge_walkin"],
                "description": "Technical knowledge of host duties, POS systems, and guest management"
            }
        },
        "experience_criteria": {
            "core_duties": [
                "Greeting and seating guests",
                "Managing reservations and waitlists (POS/reservation system)",
                "Assigning tables based on server sections / bandwidth",
                "Answering phone calls, taking guest info",
                "Handling to-go orders over the phone",
                "Managing special requests (large parties, celebrations)",
                "Resolving discrepancies (lost reservations, unexpected party sizes)"
            ],
            "minimum_duties": 3,
            "evaluation": {
                "pass": "≥1 credible workplace + timeframe + ≥3 duties",
                "review": "Only 2 duties OR vague",
                "fail": "No workplace/timeframe OR irrelevant duties"
            }
        },
        "knowledge_checks": {
            "pos": {
                "question": "Have you used a reservation system like Toast, OpenTable, or Resy? How do you use it?",
                "ideal": "Create/update reservations, check guest notes, manage table flow, update waitlist",
                "acceptable": "Yes, I enter guest info and track tables",
                "red_flag": "No, never used it (unless strong other experience)",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "seating": {
                "question": "When assigning tables, how do you decide where to seat guests?",
                "ideal": "Balance server sections, spread tables based on bandwidth, consider guest preferences",
                "acceptable": "Seat them where there's an open table, but try to spread evenly",
                "red_flag": "Seat randomly / First table I see",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "phone": {
                "question": "What information should you collect when a guest calls to make a reservation?",
                "ideal": "Name, party size, time/date, phone number, special notes (allergies, celebrations)",
                "acceptable": "Name, time, party size",
                "red_flag": "Doesn't know what to ask",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "reservation": {
                "question": "How would you handle a guest who arrives saying they have a reservation, but you don't see it in the system?",
                "ideal": "Apologize, try to accommodate (find a table, offer waitlist priority), communicate clearly",
                "acceptable": "Tell them I'll try to fit them in",
                "red_flag": "Tell them to leave / Not my problem",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            },
            "walkin": {
                "question": "How do you handle a walk-in group of 10 guests?",
                "ideal": "Check if space can be rearranged, note wait time, split into sections if needed, flag servers for support",
                "acceptable": "Tell them the wait time, try to seat them together",
                "red_flag": "Seat them anywhere without checking / Refuse without explanation",
                "scoring": {
                    "ideal": 10,
                    "acceptable": 7,
                    "red_flag": 3,
                    "no_response": 0
                }
            }
        }
    }
}

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Simplified Lambda handler for assessment processing.
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
        
        # Process the assessment
        result = process_assessment_simple(assessment_id, skill_type)
        
        if result['success']:
            logger.info(f"Assessment analysis completed successfully for {assessment_id}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'assessment_id': assessment_id,
                    'skill_type': skill_type,
                    'recommendation': result.get('recommendation', 'REVIEW'),
                    'analysis_completed_at': result.get('analyzed_at'),
                    'results_location': f's3://innovativesol-gravywork-assets-dev/assessments/{assessment_id}/analysis_results.json'
                })
            }
        else:
            logger.error(f"Assessment analysis failed for {assessment_id}: {result['error']}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'assessment_id': assessment_id,
                    'error': result['error']
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

def process_assessment_simple(assessment_id: str, skill_type: str) -> Dict[str, Any]:
    """
    Process assessment with simplified approach - no complex imports.
    """
    try:
        logger.info(f"Processing assessment {assessment_id} for {skill_type}")
        
        # Initialize AWS clients
        s3_client = boto3.client('s3')
        transcribe_client = boto3.client('transcribe')
        bedrock_client = boto3.client('bedrock-runtime')
        
        bucket_name = 'innovativesol-gravywork-assets-dev'
        
        # Get Twilio credentials from environment
        twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        
        if not twilio_account_sid or not twilio_auth_token:
            return {
                'success': False,
                'error': 'Twilio credentials not found in environment variables'
            }
        
        # Step 1: Get assessment state
        state = get_assessment_state_simple(s3_client, bucket_name, assessment_id, skill_type)
        if not state or not state.get('responses'):
            return {
                'success': False,
                'error': f'No assessment data found for {assessment_id}'
            }
        
        # Step 2: Transcribe recordings
        transcripts = transcribe_recordings_simple(
            s3_client, transcribe_client, bucket_name, assessment_id, state['responses'],
            twilio_account_sid, twilio_auth_token
        )
        
        if not transcripts:
            return {
                'success': False,
                'error': 'No transcripts generated'
            }
        
        # Step 3: Analyze with LLM
        analysis = analyze_with_llm_simple(bedrock_client, transcripts, skill_type)
        
        if not analysis['success']:
            return {
                'success': False,
                'error': f'LLM analysis failed: {analysis["error"]}'
            }
        
        # Step 4: Save results
        result = {
            'success': True,
            'assessment_id': assessment_id,
            'skill_type': skill_type,
            'analyzed_at': datetime.utcnow().isoformat(),
            'transcripts': transcripts,
            'llm_analysis': analysis['analysis'],
            'recommendation': analysis['analysis'].get('overall_recommendation', 'REVIEW'),
            'metadata': {
                'total_questions': len(transcripts),
                'transcription_service': 'AWS Transcribe',
                'llm_service': 'Amazon Bedrock Claude'
            }
        }
        
        # Save to S3
        save_results_simple(s3_client, bucket_name, assessment_id, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Assessment processing failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def get_assessment_state_simple(s3_client, bucket_name: str, assessment_id: str, skill_type: str) -> Optional[Dict[str, Any]]:
    """Get assessment state from S3."""
    try:
        key = f'assessments/{assessment_id}/state.json'
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        state = json.loads(response['Body'].read())
        return state
    except Exception as e:
        logger.error(f"Failed to get assessment state: {str(e)}")
        return None

def transcribe_recordings_simple(s3_client, transcribe_client, bucket_name: str, assessment_id: str, responses: Dict[str, Any], twilio_account_sid: str, twilio_auth_token: str) -> Dict[str, str]:
    """Transcribe recordings using AWS Transcribe."""
    transcripts = {}
    
    for question_key, response in responses.items():
        if 'recording_url' in response:
            logger.info(f"Transcribing {question_key}")
            
            try:
                # Download recording from Twilio with authentication
                recording_url = response['recording_url']
                auth = HTTPBasicAuth(twilio_account_sid, twilio_auth_token)
                audio_response = requests.get(recording_url, auth=auth, stream=True)
                audio_response.raise_for_status()
                
                # Upload to S3
                s3_key = f"assessments/{assessment_id}/recordings/{question_key}.mp3"
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=audio_response.content,
                    ContentType='audio/mpeg'
                )
                
                # Check for existing completed transcription jobs first
                existing_job = find_existing_transcription_job(
                    transcribe_client, assessment_id, question_key
                )
                
                if existing_job:
                    logger.info(f"Using existing transcription job: {existing_job}")
                    transcript = wait_for_transcription_simple(
                        transcribe_client, existing_job, s3_client, bucket_name
                    )
                else:
                    # Start new transcription job
                    job_name = f"assessment-{assessment_id}-{question_key}-{int(time.time())}"
                    media_uri = f"s3://{bucket_name}/{s3_key}"
                    
                    transcribe_client.start_transcription_job(
                        TranscriptionJobName=job_name,
                        Media={'MediaFileUri': media_uri},
                        MediaFormat='mp3',
                        LanguageCode='en-US',
                        OutputBucketName=bucket_name,
                        OutputKey=f"assessments/{assessment_id}/transcripts/"
                    )
                    
                    # Wait for completion (simplified polling)
                    transcript = wait_for_transcription_simple(transcribe_client, job_name, s3_client, bucket_name)
                
                if transcript:
                    transcripts[question_key] = transcript
                    logger.info(f"Successfully transcribed {question_key}: {transcript[:50]}...")
                else:
                    logger.error(f"Failed to transcribe {question_key}")
                    transcripts[question_key] = "[TRANSCRIPTION_FAILED]"
                    
            except Exception as e:
                logger.error(f"Error transcribing {question_key}: {str(e)}")
                transcripts[question_key] = "[TRANSCRIPTION_ERROR]"
    
    return transcripts

def find_existing_transcription_job(transcribe_client, assessment_id: str, question_key: str) -> Optional[str]:
    """Find existing completed transcription job for this assessment and question."""
    try:
        # List transcription jobs that match our pattern exactly
        response = transcribe_client.list_transcription_jobs(
            Status='COMPLETED',
            JobNameContains=f"{assessment_id}-{question_key}-"
        )
        
        jobs = response.get('TranscriptionJobSummaries', [])
        if jobs:
            # Return the most recent job
            latest_job = max(jobs, key=lambda x: x['CreationTime'])
            logger.info(f"Found existing transcription job: {latest_job['TranscriptionJobName']}")
            return latest_job['TranscriptionJobName']
            
    except Exception as e:
        logger.info(f"No existing transcription job found for {question_key}: {str(e)}")
    
    return None

def wait_for_transcription_simple(transcribe_client, job_name: str, s3_client, bucket_name: str, max_wait: int = 300) -> Optional[str]:
    """Wait for transcription job to complete."""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            
            if status == 'COMPLETED':
                # Get transcript from S3
                transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                # Extract S3 key from URI (remove bucket name)
                s3_key = transcript_uri.split('amazonaws.com/')[-1].split('/', 1)[-1]
                
                transcript_response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                transcript_data = json.loads(transcript_response['Body'].read())
                
                return transcript_data['results']['transcripts'][0]['transcript'].strip()
                
            elif status == 'FAILED':
                logger.error(f"Transcription job failed: {job_name}")
                return None
                
            # Wait before checking again
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Error checking transcription job: {str(e)}")
            return None
    
    logger.error(f"Transcription job timed out: {job_name}")
    return None

def format_analysis_for_humans(analysis_json: Dict[str, Any], skill_type: str) -> Dict[str, Any]:
    """Format LLM analysis into a human-readable structure."""
    try:
        # Get category information
        criteria = ASSESSMENT_TEMPLATES.get(skill_type, {})
        scoring_categories = criteria.get('scoring_categories', {})
        
        # Build human-readable structure
        formatted = {
            'overall_assessment': {
                'recommendation': analysis_json.get('overall_assessment', {}).get('recommendation', 'REVIEW'),
                'reasoning': analysis_json.get('overall_assessment', {}).get('reasoning', 'Analysis completed'),
                'categories_above_70_percent': analysis_json.get('overall_assessment', {}).get('categories_above_70_percent', 0)
            },
            'category_breakdown': {},
            'question_details': {},
            'summary': analysis_json.get('summary', {})
        }
        
        # Process category scores
        category_scores = analysis_json.get('category_scores', {})
        for category_key, category_info in scoring_categories.items():
            category_name = category_info['name']
            category_data = category_scores.get(category_key, {})
            
            formatted['category_breakdown'][category_name] = {
                'average_score': f"{category_data.get('average_score', 0):.1f}/10",
                'percentage': f"{category_data.get('percentage', 0):.0f}%",
                'status': '✅ PASS' if category_data.get('percentage', 0) >= 70 else '❌ BELOW 70%',
                'questions_included': category_data.get('questions', [])
            }
        
        # Process individual question scores
        question_scores = analysis_json.get('question_scores', {})
        for question_key, question_data in question_scores.items():
            score = question_data.get('score', 0)
            level = question_data.get('level', 'unknown')
            reasoning = question_data.get('reasoning', 'No reasoning provided')
            
            # Format score with emoji
            score_emoji = '🟢' if score >= 8 else '🟡' if score >= 6 else '🔴'
            level_formatted = level.replace('_', ' ').title()
            
            formatted['question_details'][question_key] = {
                'score': f"{score}/10",
                'level': f"{score_emoji} {level_formatted}",
                'reasoning': reasoning
            }
        
        return formatted
        
    except Exception as e:
        logger.error(f"Error formatting analysis: {str(e)}")
        # Return original if formatting fails
        return analysis_json

def analyze_with_llm_simple(bedrock_client, transcripts: Dict[str, str], skill_type: str) -> Dict[str, Any]:
    """Analyze transcripts with Bedrock using self-contained LLM logic."""
    try:
        # Build prompt
        prompt = build_assessment_prompt_simple(transcripts, skill_type)
        
        # Use Converse API directly without external dependencies
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Claude Sonnet 3
        
        messages = [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]
        
        # Direct Converse API call
        inference_config = {
            "maxTokens": 4000,
            "temperature": 0.3,
            "topP": 0.9
        }
        
        response = bedrock_client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inference_config
        )
        
        # Extract response from Converse API format
        analysis_text = response['output']['message']['content'][0]['text']
        usage = response.get('usage', {})
        
        # Try to parse as JSON - handle both raw JSON and markdown-wrapped JSON
        try:
            # First try direct JSON parsing
            analysis_json = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\n(.*?)\n```', analysis_text, re.DOTALL)
            if json_match:
                try:
                    analysis_json = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    analysis_json = None
            else:
                analysis_json = None
        
        if analysis_json:
            # Format the analysis in a human-readable structure
            formatted_analysis = format_analysis_for_humans(analysis_json, skill_type)
            
            return {
                'success': True,
                'analysis': formatted_analysis,
                'usage': usage
            }
        else:
            # Return structured response if JSON parsing fails
            return {
                'success': True,
                'analysis': {
                    'overall_recommendation': 'REVIEW',
                    'overall_reasoning': 'Analysis completed but response format needs review',
                    'raw_analysis': analysis_text
                },
                'usage': usage
            }
            
    except Exception as e:
        logger.error(f"Bedrock analysis failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def build_assessment_prompt_simple(transcripts: Dict[str, str], skill_type: str) -> str:
    """Build assessment prompt."""
    criteria = ASSESSMENT_TEMPLATES.get(skill_type, {})
    role_name = criteria.get('name', skill_type.title())
    
    prompt = f"""You are evaluating a {role_name} skills assessment using a detailed 0-10 scoring system.

SCORING CATEGORIES:
"""
    
    # Add scoring categories info
    scoring_categories = criteria.get('scoring_categories', {})
    for category_key, category_info in scoring_categories.items():
        prompt += f"""
{category_info['name']}:
- Questions: {', '.join(category_info['questions'])}
- Description: {category_info['description']}
"""
    
    prompt += "\nCANDIDATE RESPONSES:\n"
    
    # Add responses organized by category
    for category_key, category_info in scoring_categories.items():
        category_name = category_info['name']
        category_questions = category_info['questions']
        
        prompt += f"\n{category_name.upper()}:\n"
        
        for question_key in category_questions:
            if question_key in transcripts:
                # Find the question details
                question_details = None
                
                # Look in knowledge_checks
                knowledge_checks = criteria.get('knowledge_checks', {})
                for check_key, check_data in knowledge_checks.items():
                    if question_key.endswith(check_key) or check_key in question_key:
                        question_details = check_data
                        break
                
                # Look in english_communication
                english_comm = criteria.get('english_communication', {})
                for comm_key, comm_data in english_comm.items():
                    if question_key.endswith(comm_key) or comm_key in question_key:
                        question_details = comm_data
                        break
                
                if question_details:
                    scoring = question_details.get('scoring', {})
                    prompt += f"""
QUESTION_ID: {question_key}
Question: {question_details['question']}
Candidate Response: "{transcripts[question_key]}"
Scoring Criteria:
- Ideal ({scoring.get('ideal', 10)} points): {question_details['ideal']}
- Acceptable ({scoring.get('acceptable', 7)} points): {question_details['acceptable']} (Note: Answers are acceptable if they contain the key concepts/tools mentioned, even if worded differently or in different order)
- Red Flag ({scoring.get('red_flag', 3)} points): {question_details['red_flag']}
- No Response ({scoring.get('no_response', 0)} points): No meaningful answer

IMPORTANT: When scoring this question, use the QUESTION_ID "{question_key}" in your response.
"""
                else:
                    # Experience questions - provide scoring criteria
                    prompt += f"""
QUESTION_ID: {question_key}
Question: {question_key.replace('_', ' ').title()}
Candidate Response: "{transcripts[question_key]}"
Scoring Criteria:
- Ideal (10 points): Detailed, credible experience with specific examples
- Acceptable (7 points): Some relevant experience mentioned
- Red Flag (3 points): Vague, unclear, or irrelevant experience
- No Response (0 points): No meaningful answer provided

IMPORTANT: When scoring this question, use the QUESTION_ID "{question_key}" in your response.

"""
    
    # Add experience criteria if available
    experience_criteria = criteria.get('experience_criteria', {})
    if experience_criteria:
        prompt += f"""
EXPERIENCE EVALUATION CRITERIA:
Core Duties (must mention at least {experience_criteria.get('minimum_duties', 3)}):
"""
        for duty in experience_criteria.get('core_duties', []):
            prompt += f"- {duty}\n"
        
        evaluation = experience_criteria.get('evaluation', {})
        prompt += f"""
Experience Scoring Guidelines:
- Pass (7-10 points): {evaluation.get('pass', 'Credible experience')}
- Review (4-6 points): {evaluation.get('review', 'Some concerns')}
- Fail (0-3 points): {evaluation.get('fail', 'No relevant experience')}
"""
    
    prompt += """
SCORING INSTRUCTIONS:
Provide detailed 0-10 scoring for each question and category averages.

CRITICAL: Respond with ONLY the JSON object below. Do not wrap in markdown code blocks or add any other text. Return the raw JSON structure only:

{
  "question_scores": {
    "question_key": {
      "score": 0-10,
      "level": "ideal|acceptable|red_flag|no_response", 
      "reasoning": "specific explanation for this score"
    }
  },
  "category_scores": {
    "baseline": {
      "average_score": 0.0,
      "percentage": 0.0,
      "questions": ["list of questions in this category"]
    },
    "experience": {
      "average_score": 0.0,
      "percentage": 0.0, 
      "questions": ["list of questions in this category"]
    },
    "knowledge": {
      "average_score": 0.0,
      "percentage": 0.0,
      "questions": ["list of questions in this category"]
    }
  },
  "overall_assessment": {
    "recommendation": "PASS|REVIEW|FAIL",
    "reasoning": "Overall assessment explanation based on 70% threshold rules",
    "categories_above_70_percent": 0-3
  },
  "summary": {
    "strengths": ["specific strengths identified"],
    "areas_for_improvement": ["specific concerns or gaps"]
  }
}

PASS/REVIEW/FAIL CRITERIA:
- PASS: 70% or higher across ALL three categories
- REVIEW: 70% or higher across TWO of three categories  
- FAIL: 70% or higher in only ONE or ZERO categories

EVALUATION GUIDELINES:
- Focus on substance over exact wording
- If candidate mentions the key concepts/tools/ingredients, consider it acceptable even if phrased differently
- Be flexible with order and minor variations in responses
- Only mark as "Red Flag" if the candidate clearly lacks knowledge or gives wrong information
- Mark as "No Response" ONLY if there is literally no answer or completely unintelligible response
- If there is ANY response (even a bad one), classify it as "red_flag", NOT "no_response"

CRITICAL: MATCH RESPONSES TO CORRECT QUESTION_IDs
- Each question has a unique QUESTION_ID. You MUST match the candidate's response to the correct QUESTION_ID.
- Do NOT mix up responses between different questions.
- Use the QUESTION_ID exactly as provided in each section above.

YOU MUST PROVIDE SCORES FOR ALL QUESTIONS INCLUDING: {', '.join(transcripts.keys())}

Score each question 0-10 based on criteria, calculate category averages, then determine final recommendation.

IMPORTANT: Return ONLY the JSON object. No markdown formatting, no code blocks, no additional text.
"""
    
    return prompt

def save_results_simple(s3_client, bucket_name: str, assessment_id: str, results: Dict[str, Any]):
    """Save analysis results to S3 and update global assessment index."""
    try:
        # Save individual assessment results
        s3_key = f"assessments/{assessment_id}/analysis_results.json"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(results, indent=2),
            ContentType='application/json'
        )
        
        logger.info(f"Saved analysis results to s3://{bucket_name}/{s3_key}")
        
        # Update global assessment index
        update_global_assessment_index(s3_client, bucket_name, assessment_id, results)
        
    except Exception as e:
        logger.error(f"Failed to save analysis results: {str(e)}")

def update_global_assessment_index(s3_client, bucket_name: str, assessment_id: str, results: Dict[str, Any]):
    """Update the global assessment index file with this new assessment."""
    try:
        index_key = "assessments_index.json"
        
        # Try to get existing index
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=index_key)
            existing_index = json.loads(response['Body'].read().decode('utf-8'))
        except s3_client.exceptions.NoSuchKey:
            # Create new index if it doesn't exist
            existing_index = {
                "assessments": [],
                "last_updated": None,
                "total_count": 0
            }
        except Exception as e:
            logger.warning(f"Error reading existing index, creating new one: {str(e)}")
            existing_index = {
                "assessments": [],
                "last_updated": None,
                "total_count": 0
            }
        
        # Parse assessment ID for metadata
        parts = assessment_id.split('_')
        if len(parts) >= 4:
            # Handle roles like "banquet_server" (2 parts)
            role = '_'.join(parts[:-3])  # Everything except last 3 parts
            date = parts[-3]
            time = parts[-2]
        else:
            # Fallback for simple roles
            role = parts[0] if len(parts) > 0 else 'unknown'
            date = parts[1] if len(parts) > 1 else 'unknown'
            time = parts[2] if len(parts) > 2 else 'unknown'
        
        # Get status from results
        status = 'unknown'
        if results.get('llm_analysis', {}).get('overall_assessment', {}).get('recommendation'):
            status = results['llm_analysis']['overall_assessment']['recommendation'].lower()
        elif results.get('llm_analysis', {}).get('overall_recommendation'):
            status = results['llm_analysis']['overall_recommendation'].lower()
        elif results.get('recommendation'):
            status = results['recommendation'].lower()
        
        # Create assessment entry
        assessment_entry = {
            "id": assessment_id,
            "role": role.replace('_', ' '),
            "date": date,
            "time": time,
            "status": status,
            "analyzed_at": results.get('analyzed_at', datetime.utcnow().isoformat()),
            "file_path": f"assessments/{assessment_id}/analysis_results.json"
        }
        
        # Remove any existing entry with same ID (in case of reprocessing)
        existing_index["assessments"] = [
            a for a in existing_index["assessments"] 
            if a.get("id") != assessment_id
        ]
        
        # Add new entry
        existing_index["assessments"].append(assessment_entry)
        
        # Update metadata
        existing_index["last_updated"] = datetime.utcnow().isoformat()
        existing_index["total_count"] = len(existing_index["assessments"])
        
        # Sort by analyzed_at (newest first)
        existing_index["assessments"].sort(
            key=lambda x: x.get("analyzed_at", ""), 
            reverse=True
        )
        
        # Save updated index
        s3_client.put_object(
            Bucket=bucket_name,
            Key=index_key,
            Body=json.dumps(existing_index, indent=2),
            ContentType='application/json'
        )
        
        logger.info(f"✅ SUCCESSFULLY updated global assessment index with {assessment_id}")
        
    except Exception as e:
        logger.error(f"❌ FAILED to update global assessment index: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Don't fail the main process if index update fails
