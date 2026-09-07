# AIRI - Artificial Intelligence Response Interface

A secure starter conversational AI web application built with Python, Flask, SQLite, HTML, CSS and JavaScript.

## Features

- AI chat using the OpenAI Responses API
- Anonymous browser session conversations
- SQLite chat history
- New Chat / Clear Chat
- Input validation and 4000-character message limit
- Rate limiting
- Parameterized SQL queries
- Environment-based API key configuration
- Responsive dark web interface

## Project Structure

```text
AIRI/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── database/
│   └── airi.db              # created automatically at runtime
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Requirements

- Python 3.10+
- An OpenAI API key with API access/billing configured as required by your account

## Local Setup

### 1. Clone

```bash
git clone https://github.com/abinash-off/AIRI.git
cd AIRI
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your real values:

```text
OPENAI_API_KEY=your_real_api_key
FLASK_SECRET_KEY=your_long_random_secret
OPENAI_MODEL=gpt-5.5
```

Never commit `.env` or your API key to GitHub.

### 5. Run

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Security Notes

This repository is a development starter, not a production deployment. Before exposing it to the internet, add authentication, CSRF protection, secure cookie settings, HTTPS, production WSGI serving, stronger authorization and audit logging.

Do not use Flask's debug server for production.

## Architecture

```text
Browser
   │
   ▼
HTML / CSS / JavaScript
   │
   ▼
Flask API
   ├── Rate limiting
   ├── Input validation
   ├── Session management
   └── SQLite history
   │
   ▼
OpenAI Responses API
   │
   ▼
AIRI response
```

## License

Educational project. Add your preferred license before distributing the project publicly.
