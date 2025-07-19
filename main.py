import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response, stream_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai
from openai import OpenAI
import google.generativeai as genai
import time
import json as json_module

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)

# Configure AI APIs
openai_api_key = os.getenv('OPENAI_API_KEY')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def validate_api_keys():
    """Validate API keys on startup"""
    api_status = {
        'openai': False,
        'gemini': False
    }
    
    # Check OpenAI API key
    if openai_api_key and openai_api_key != 'your_openai_api_key_here':
        try:
            client = OpenAI(api_key=openai_api_key)
            # Simple API test
            client.models.list()
            api_status['openai'] = True
            logging.info("OpenAI API key validated successfully")
        except Exception as e:
            logging.warning(f"OpenAI API key validation failed: {str(e)}")
    
    # Check Gemini API key
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key and gemini_api_key != 'your_gemini_api_key_here':
        try:
            model = genai.GenerativeModel('gemini-pro')
            # Simple test to validate key
            model.generate_content("Hello", stream=False)
            api_status['gemini'] = True
            logging.info("Gemini API key validated successfully")
        except Exception as e:
            logging.warning(f"Gemini API key validation failed: {str(e)}")
    
    return api_status

def read_file_content(filepath):
    """Read and process uploaded file content"""
    try:
        _, ext = os.path.splitext(filepath.lower())
        
        if ext in ['.txt']:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext in ['.pdf']:
            # For now, return a placeholder - PDF processing would require additional libraries
            return "[PDF file uploaded - content analysis not yet implemented]"
        elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
            return "[Image file uploaded - visual analysis not yet implemented]"
        elif ext in ['.doc', '.docx']:
            return "[Document file uploaded - content analysis not yet implemented]"
        else:
            return "[Unsupported file type]"
    except Exception as e:
        logging.error(f"Error reading file: {str(e)}")
        return "[Error reading file content]"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def save_conversation(user_id, conversation):
    """Save conversation to history file"""
    try:
        history_file = f'data/history_{user_id}.json'
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append({
            'timestamp': datetime.now().isoformat(),
            'conversation': conversation
        })
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
        logging.info(f"Conversation saved for user {user_id}")
    except Exception as e:
        logging.error(f"Error saving conversation: {str(e)}")

def load_conversation_history(user_id):
    """Load conversation history for a user"""
    try:
        history_file = f'data/history_{user_id}.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Error loading conversation history: {str(e)}")
        return []

def get_openai_response(messages):
    """Get response from OpenAI API"""
    try:
        client = OpenAI(api_key=openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True
        )
        return response
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return None

def get_gemini_response(messages):
    """Get response from Google Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Convert messages to Gemini format
        prompt = ""
        for message in messages:
            role = "Human" if message['role'] == 'user' else "Assistant"
            prompt += f"{role}: {message['content']}\n"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Gemini API error: {str(e)}")
        return None

@app.route('/')
def index():
    """Main chat room"""
    if 'user_id' not in session:
        session['user_id'] = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return render_template('room.html')

@app.route('/history')
def history():
    """View conversation history"""
    if 'user_id' not in session:
        # Create a user session instead of redirecting
        session['user_id'] = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    user_history = load_conversation_history(session['user_id'])
    return render_template('history.html', history=user_history)

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Handle streaming chat responses"""
    try:
        data = request.json
        message = data.get('message')
        ai_provider = data.get('ai_provider', 'openai')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get conversation history from session
        if 'conversation' not in session:
            session['conversation'] = []
        
        # Add user message to conversation
        session['conversation'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        def generate_response():
            try:
                if ai_provider == 'openai':
                    response = get_openai_response(session['conversation'])
                    if response:
                        ai_response = ""
                        for chunk in response:
                            if chunk.choices[0].delta.content:
                                content = chunk.choices[0].delta.content
                                ai_response += content
                                yield f"data: {json_module.dumps({'content': content, 'type': 'chunk'})}\n\n"
                        
                        # Add complete response to conversation
                        session['conversation'].append({
                            'role': 'assistant',
                            'content': ai_response,
                            'timestamp': datetime.now().isoformat(),
                            'provider': 'OpenAI'
                        })
                        
                        # Save conversation
                        save_conversation(session['user_id'], session['conversation'])
                        
                        yield f"data: {json_module.dumps({'type': 'done', 'provider': 'OpenAI'})}\n\n"
                    else:
                        yield f"data: {json_module.dumps({'type': 'error', 'message': 'OpenAI API error'})}\n\n"
                        
                elif ai_provider == 'gemini':
                    response = get_gemini_response(session['conversation'])
                    if response:
                        # For Gemini, we don't have streaming, so send the complete response
                        yield f"data: {json_module.dumps({'content': response, 'type': 'complete'})}\n\n"
                        
                        session['conversation'].append({
                            'role': 'assistant',
                            'content': response,
                            'timestamp': datetime.now().isoformat(),
                            'provider': 'Gemini'
                        })
                        
                        save_conversation(session['user_id'], session['conversation'])
                        
                        yield f"data: {json_module.dumps({'type': 'done', 'provider': 'Gemini'})}\n\n"
                    else:
                        yield f"data: {json_module.dumps({'type': 'error', 'message': 'Gemini API error'})}\n\n"
                        
            except Exception as e:
                logging.error(f"Streaming error: {str(e)}")
                yield f"data: {json_module.dumps({'type': 'error', 'message': 'Internal server error'})}\n\n"
        
        return Response(
            generate_response(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        logging.error(f"Chat stream error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message')
        ai_provider = data.get('ai_provider', 'openai')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get conversation history from session
        if 'conversation' not in session:
            session['conversation'] = []
        
        # Add user message to conversation
        session['conversation'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get AI response based on provider
        if ai_provider == 'openai':
            response = get_openai_response(session['conversation'])
            if response:
                ai_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        ai_response += chunk.choices[0].delta.content
                
                session['conversation'].append({
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat(),
                    'provider': 'OpenAI'
                })
                
                # Save conversation to history
                save_conversation(session['user_id'], session['conversation'])
                
                return jsonify({
                    'response': ai_response,
                    'provider': 'OpenAI'
                })
            else:
                return jsonify({'error': 'OpenAI API error'}), 500
                
        elif ai_provider == 'gemini':
            response = get_gemini_response(session['conversation'])
            if response:
                session['conversation'].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat(),
                    'provider': 'Gemini'
                })
                
                # Save conversation to history
                save_conversation(session['user_id'], session['conversation'])
                
                return jsonify({
                    'response': response,
                    'provider': 'Gemini'
                })
            else:
                return jsonify({'error': 'Gemini API error'}), 500
        
        else:
            return jsonify({'error': 'Invalid AI provider'}), 400
            
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid filename conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read file content
            file_content = read_file_content(filepath)
            
            # Add file upload to conversation if it has content
            if 'conversation' not in session:
                session['conversation'] = []
            
            file_message = f"📎 **File uploaded:** {file.filename}\n\n**Content:**\n{file_content}"
            session['conversation'].append({
                'role': 'user',
                'content': file_message,
                'timestamp': datetime.now().isoformat(),
                'file_upload': True
            })
            
            logging.info(f"File uploaded and processed: {filename}")
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'filename': filename,
                'content_preview': file_content[:200] + "..." if len(file_content) > 200 else file_content
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/clear_conversation', methods=['POST'])
def clear_conversation():
    """Clear current conversation"""
    session.pop('conversation', None)
    return jsonify({'message': 'Conversation cleared'})

@app.route('/api/status')
def api_status():
    """Check API key status"""
    status = validate_api_keys()
    return jsonify({
        'apis': status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    api_status_result = validate_api_keys()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'apis': api_status_result,
        'version': '1.1.0'
    })

if __name__ == '__main__':
    # Validate API keys on startup
    logging.info("Starting AI Room Dashboard...")
    api_status = validate_api_keys()
    
    if not any(api_status.values()):
        logging.warning("No valid API keys found. The application will start but AI features may not work.")
        logging.warning("Please check your .env file and ensure you have valid API keys.")
    else:
        available_apis = [api for api, status in api_status.items() if status]
        logging.info(f"Available APIs: {', '.join(available_apis)}")
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)