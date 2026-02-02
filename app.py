from flask import Flask, render_template, request, jsonify
import os
import random
import google.generativeai as genai
import socket
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, TimeoutError

app = Flask(__name__)

# Your API key
API_KEY = "AIzaSyDt5TGZl7Y1yG4x9WhUgeX6kOW_okwEixY"

# Working models - use the ones we know work
WORKING_MODELS = [
    'models/gemini-2.5-flash',
    'models/gemini-flash-latest', 
    'models/gemini-flash-lite-latest',
    'models/gemma-3-4b-it',
]

# Global variables
model = None
API_AVAILABLE = False
SELECTED_MODEL = None

def check_internet_connection(timeout=3):
    """Check if internet connection is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        try:
            requests.get("http://www.google.com", timeout=timeout)
            return True
        except:
            return False

def setup_gemini():
    """Setup Gemini API with timeout"""
    global model, API_AVAILABLE, SELECTED_MODEL
    
    # First check internet
    if not check_internet_connection():
        print("⚠️ No internet connection detected")
        return False
    
    try:
        genai.configure(api_key=API_KEY)
        
        # Try each model
        for model_name in WORKING_MODELS:
            try:
                # Create model (no timeout needed here)
                test_model = genai.GenerativeModel(model_name)
                
                # Quick test with simple generation
                # Note: Gemini API doesn't have request_options in generate_content
                test_response = test_model.generate_content("Hi")
                
                if test_response and test_response.text:
                    model = test_model
                    API_AVAILABLE = True
                    SELECTED_MODEL = model_name
                    print(f"✅ Gemini API ready: {model_name}")
                    return True
                    
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower():
                    print(f"⛔ {model_name}: Quota exceeded")
                elif "429" in error_msg:
                    print(f"⛔ {model_name}: Rate limited")
                else:
                    print(f"⚠️ {model_name}: {error_msg[:80]}")
                continue
        
        print("⚠️ All models failed, using demo mode")
        return False
        
    except Exception as e:
        print(f"❌ API setup failed: {e}")
        return False

# Setup Gemini on startup
print("🔍 Checking internet and setting up Gemini...")
if setup_gemini():
    print("✅ AI setup completed")
else:
    print("⚠️ Running in demo mode")

# Mock responses
MOCK_RESPONSES = [
    "Hello! I'm your AI assistant. How can I help you today?",
    "I'm here to assist you with your questions. What would you like to know?",
    "Welcome! I'm ready to help. Ask me anything.",
    "Hi there! I can answer questions and help with information.",
]

def get_ai_response_with_timeout(question, timeout=20):
    """Get AI response with timeout protection"""
    # Fast internet check
    if not check_internet_connection(timeout=2):
        return random.choice(MOCK_RESPONSES), True, "offline"
    
    if not API_AVAILABLE or not model:
        return random.choice(MOCK_RESPONSES), True, "demo"
    
    try:
        # Use ThreadPoolExecutor for timeout control
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                lambda: model.generate_content(question)
            )
            response = future.result(timeout=timeout)
            return response.text, False, SELECTED_MODEL
            
    except TimeoutError:
        print(f"⏱️ AI response timeout after {timeout}s")
        return "I'm taking too long to respond. Please try again or check your connection.", True, "timeout"
    except Exception as e:
        error_msg = str(e)
        print(f"❌ AI error: {error_msg[:100]}")
        
        if "quota" in error_msg.lower() or "429" in error_msg:
            return "The AI service is currently at capacity. Please try again later.", True, "quota"
        elif "invalid" in error_msg.lower():
            return "AI service unavailable. Running in demo mode.", True, "invalid"
        else:
            return random.choice(MOCK_RESPONSES), True, "error"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint with proper timeout handling"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'success': False, 'error': 'Empty question'}), 400
        
        # Get response with timeout
        response, is_mock, status = get_ai_response_with_timeout(question, timeout=20)
        
        return jsonify({
            'success': True,
            'question': question,
            'response': response,
            'is_mock': is_mock,
            'status': status
        })
        
    except Exception as e:
        print(f"🚨 Server error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error',
            'response': "Sorry, I encountered a technical issue. Please try again."
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Check API and internet status"""
    internet_ok = check_internet_connection()
    return jsonify({
        'success': True,
        'internet': internet_ok,
        'api_available': API_AVAILABLE and internet_ok,
        'model': SELECTED_MODEL if (API_AVAILABLE and internet_ok) else 'demo',
        'status': 'online' if (API_AVAILABLE and internet_ok) else 'demo'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting AI Chat Assistant on http://localhost:{port}")
    print(f"🌐 Internet: {'✅ Connected' if check_internet_connection() else '❌ Offline'}")
    print(f"🤖 AI Status: {'✅ Ready' if API_AVAILABLE else '⚠️ Demo Mode'}")
    if API_AVAILABLE:
        print(f"📊 Using model: {SELECTED_MODEL}")
    app.run(debug=True, port=port, host='0.0.0.0')