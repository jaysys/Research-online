# OpenAI Python Example

## Files

- `app.py`: minimal OpenAI API example
- `requirements.txt`: Python dependencies
- `.env`: environment variable file
- `.env.example`: environment variable template

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 app.py
```

Edit `.env` and replace `YOUR_OPENAI_API_KEY` with your real key before running.
