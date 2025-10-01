# Cyber-Shield-Mission[README.md](https://github.com/user-attachments/files/22630313/README.md)
# Cyber Shield Junior — demo prototype

Simple Streamlit demo that detects potential cyberbullying messages and offers actions: save evidence, block sender, suggested calm replies.

## How to run

1. Create virtual env (recommended):
```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the app:
```bash
streamlit run app.py
```

If you can't install `torch`/`transformers`, remove them from `requirements.txt`. The app will still work using the simple rule-based fallback.

## What is included
- `app.py` — Streamlit demo
- `evidence/` — folder where evidence JSON files are saved at runtime

## Notes for hackathon
- This is a minimal MVP. For production we must add authentication, secure storage, human review for flagged messages, privacy policy, and consider local laws.
