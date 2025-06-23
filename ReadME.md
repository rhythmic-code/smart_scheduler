# Smart Scheduler - AI Meeting Assistant

Automatically schedule meetings using voice commands with Google Calendar integration.

## Features
- Voice-controlled meeting scheduling
- Natural conversation flow
- Conflict-free time slot detection
- Google Calendar integration
- Timezone-aware scheduling

## Setup Instructions

1. **Clone repository**:
   ```bash
   git clone https://github.com/yourusername/smart-scheduler.git
   cd smart-scheduler
Install dependencies:

bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
.\myenv\Scripts\activate  # Windows
pip install -r requirements.txt
Google Calendar Setup:

Enable Google Calendar API at Google Cloud Console

Create OAuth 2.0 credentials (Desktop app type)

Download credentials.json and place in project root

First Run:

bash
python main.py
Authenticate with Google when prompted

Speak naturally to schedule meetings!

Usage Examples
"Schedule a meeting tomorrow at 3pm"

"I need a 1-hour meeting on Friday"

"Book a meeting sometime next week in the morning"

Configuration
Edit config.py to customize:

Working hours

Timezone settings

Speech recognition parameters

text

#### Step 5: Initialize Git Repository
```bash
# Initialize repository
git init

# Add files
git add .
git commit -m "Initial commit of Smart Scheduler project"

# Create GitHub repository (through web interface)
# Then link to remote
git remote add origin https://github.com/yourusername/smart-scheduler.git
git branch -M main
git push -u origin main
Security Considerations
Never commit credentials:

Double-check that credentials.json and token.json are in .gitignore

Verify with: git status before committing

Revoke leaked credentials:
If credentials are accidentally committed:

Immediately revoke them in Google Cloud Console

Rotate credentials using "Create new OAuth client ID"

Purge history with BFG Repo-Cleaner

Post-Installation Notes for Users
On first run, the application will:

Open a browser for Google authentication

Save token.json for future sessions

Request calendar access permissions

For Windows audio issues:

bash
pip install pipwin
pipwin install pyaudio
For Linux audio setup:

bash
sudo apt-get install portaudio19-dev python3-pyaudio
This setup ensures your project is:

Properly version controlled

Secure from credential leaks

Easy for others to install and use

Well-documented for future development