# 🧠 Smart Scheduler – AI Meeting Assistant

Smart Scheduler is a voice-enabled AI assistant that automates meeting scheduling using natural conversation. It integrates seamlessly with Google Calendar and supports local LLM-based function calling for intelligent date/time understanding and conflict resolution.

---

## 🚀 Features

- 🎙️ Voice-controlled meeting scheduling
- 💬 Natural conversation with multi-turn memory
- 🧠 LLM-powered function calling (Gemma 2B via Ollama)
- 📅 Conflict-free time slot detection
- 🔗 Google Calendar API integration (OAuth 2.0)
- 🌐 Timezone-aware scheduling logic
- 🔊 Text-to-speech (TTS) + Speech-to-text (STT) integration

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart-scheduler.git
cd smart-scheduler
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv myenv
```

- **Linux / MacOS**:
  ```bash
  source myenv/bin/activate
  ```

- **Windows**:
  ```bash
  .\myenv\Scripts\activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Google Calendar API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Calendar API** for your project.
3. Go to **APIs & Services → Credentials → Create Credentials** → OAuth client ID:
   - Application type: **Desktop App**
4. Download the `credentials.json` file.
5. Place the file inside your `calendar/` folder in the project.

### ⚠️ First-Time Authentication

On your first run, a browser will prompt you to log in and approve calendar access. After this, a `token.json` file will be created for future access.

---

## 🧠 Running the Assistant

Start the assistant using:

```bash
python agent.py
```

Then speak your commands naturally:

```
"Schedule a meeting on June 17th from 3 PM to 4 PM"
"Do I have any meetings tomorrow?"
"Show my upcoming events this week"
```

---

## 💬 Example Prompts

- "Schedule a meeting tomorrow at 3 PM"
- "Add an event for 'Design Review' on June 20th from 2 to 3 PM"
- "Do I have any events next Tuesday?"
- "Book a meeting on Friday morning"

---

## ⚙️ Configuration Options

You can configure:

- ✅ Timezone preferences
- ✅ Default meeting duration
- ✅ Working hours range
- ✅ Voice parameters

Edit these in your config script or `agent.py`.

---

## 🛡️ Security Considerations

> ❗ **Never commit credentials to version control.**

Add the following to your `.gitignore`:

```gitignore
myenv/
token.json
credentials.json
```

If you accidentally committed credentials:

1. Revoke the OAuth token in Google Cloud Console
2. Generate a new OAuth Client ID
3. Clean the Git history using [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

## 🔊 Voice & Audio Setup

### On Windows

```bash
pip install pipwin
pipwin install pyaudio
```

### On Linux

```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

---

## 🗃️ Git Setup (Optional)

```bash
git init
git add .
git commit -m "Initial commit"

# After creating repo on GitHub:
git remote add origin https://github.com/yourusername/smart-scheduler.git
git branch -M main
git push -u origin main
```

---

## 🧪 LLM Models Supported

- [x] Gemma 2B (via Ollama)
- [x] LLaMA 3 (optional fallback)
- [ ] OpenAI / Claude (future option)

Ollama server must be running before launching the app:

```bash
ollama run gemma:2b-instruct-q4_0
```

---

## 🏁 Roadmap

- [x] Basic voice-driven calendar integration
- [x] LLM-powered event intent extraction
- [x] Conflict checking
- [ ] Add participant/invite support
- [ ] Extend support for task reminders
- [ ] Web app / UI integration

---

## 🙌 Acknowledgements

- Hugging Face Transformers
- Google Calendar API
- Whisper (STT)
- Pyttsx3 (TTS)
- Ollama (for local LLM serving)

---

## 👨‍💻 Author

**Rhythm Gupta**  
📧 rhythmguptakrishna@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/rhythm-gupta-520077253)  
💻 [GitHub](https://github.com/rhythmic-code)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.