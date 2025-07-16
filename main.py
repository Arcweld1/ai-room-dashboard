import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai
from openai import OpenAI
import google.generativeai as genai

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
        return redirect(url_for('index'))
    
    user_history = load_conversation_history(session['user_id'])
    return render_template('history.html', history=user_history)

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
            'content': message
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
                    'content': ai_response
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
                    'content': response
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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logging.info(f"File uploaded: {filename}")
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename
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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)