# AI Chat Assistant 🤖

A simple Flask web application that uses Google's Gemini AI to answer questions in real-time.

## 📋 Features
- **AI Integration**: Google Gemini AI for intelligent responses
- **Modern UI**: Clean interface with dark/light theme toggle
- **Markdown Support**: Renders AI responses with formatting
- **Fallback Mode**: Works offline with mock responses
- **Error Handling**: Graceful degradation on API failures
- **Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation
```bash
# 1. Clone repository
git clone https://github.com/SahilGupta99/ai-chat-app.git
cd ai-chat-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API key (optional, for demo mode skip this)
# On Windows (CMD):
set GEMINI_API_KEY=your_api_key_here

# On Mac/Linux:
export GEMINI_API_KEY=your_api_key_here

# 4. Run the application
python app.py
