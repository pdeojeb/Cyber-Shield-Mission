import streamlit as st
from datetime import datetime
import json
import os

use_transformers = False
try:
    from transformers import pipeline
    toxic_pipe = pipeline("text-classification", model="unitary/toxic-bert", return_all_scores=True)
    use_transformers = True
except Exception:
    toxic_pipe = None
    use_transformers = False

TOXIC_KEYWORDS = {
    "insult": ["stupid", "idiot", "dumb", "ugly", "trash"],
    "threat": ["kill", "destroy", "beat", "hurt", "die"],
    "harass": ["shut up", "shutup", "go away"]
}

EVIDENCE_DIR = "evidence"
BLOCKS_FILE = "blocked_senders.json"
if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)

def rule_based_check(text):
    text_low = text.lower()
    hits = []
    for cat, words in TOXIC_KEYWORDS.items():
        for w in words:
            if w in text_low:
                hits.append({"category": cat, "word": w})
    score = min(1.0, 0.2 * len(hits))
    return {"score": score, "hits": hits}

def detect_toxicity(text):
    if use_transformers and toxic_pipe:
        try:
            out = toxic_pipe(text)
            items = out[0]
            labels = [{"label": d["label"].lower(), "score": float(d["score"])} for d in items]
            toks = ["toxic", "insult", "threat", "obscene", "identity_hate", "severe_toxic"]
            best = max([lbl["score"] for lbl in labels if lbl["label"] in toks]+[0])
            return {"score": float(best), "labels": labels, "source": "transformer"}
        except Exception:
            return {**rule_based_check(text), "labels": [], "source": "rule"}
    return {**rule_based_check(text), "labels": [], "source": "rule"}

def save_evidence(sender, receiver, message, detection):
    timestamp = datetime.utcnow().isoformat() + "Z"
    filename = os.path.join(EVIDENCE_DIR, f"evidence_{int(datetime.utcnow().timestamp())}.json")
    payload = {"timestamp": timestamp,"sender": sender,"receiver": receiver,"message": message,"detection": detection}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return filename

def load_blocked():
    if os.path.exists(BLOCKS_FILE):
        with open(BLOCKS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_blocked(block_list):
    with open(BLOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(block_list, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Cyber Shield Junior", page_icon="🛡️")
st.title("🛡️ Cyber Shield Junior — anti-cyberbullying demo")
st.markdown("""
Detect harmful messages and take actions:
- Warn user
- Block sender
- Save evidence
- Suggested calm replies
""")

with st.expander("Demo messages"):
    st.write("Examples:")
    st.write("- 'You're so stupid and ugly.'")
    st.write("- 'If you come to school tomorrow, I'll hurt you.'")
    st.write("- 'I don't like you, go away.'")

sender = st.text_input("Sender", "user123")
receiver = st.text_input("Receiver", "me")
message = st.text_area("Message text", height=120)

if st.button("Analyze"):
    if not message.strip():
        st.warning("Enter a message.")
    else:
        detection = detect_toxicity(message)
        score = detection.get("score",0)
        st.write(f"Source: **{detection.get('source')}**, Score: **{score:.2f}**")
        if detection.get("labels"):
            st.write("Labels:")
            for lbl in detection["labels"]:
                st.write(f"- {lbl['label']}: {lbl['score']:.2f}")
        if score>=0.6:
            st.markdown("### ⚠️ Severe bullying detected")
            col1,col2,col3=st.columns(3)
            if col1.button("Save evidence"):
                path = save_evidence(sender, receiver, message, detection)
                st.success(f"Evidence saved: {path}")
            if col2.button("Block sender"):
                blocked = load_blocked()
                if sender not in blocked:
                    blocked.append(sender)
                    save_blocked(blocked)
                st.success(f"Blocked {sender}")
        elif score>=0.25:
            st.markdown("### ⚠️ Possible bullying")
            col1,col2=st.columns(2)
            if col1.button("Save evidence"):
                path = save_evidence(sender, receiver, message, detection)
                st.success(f"Evidence saved: {path}")
            if col2.button("Block sender"):
                blocked = load_blocked()
                if sender not in blocked:
                    blocked.append(sender)
                    save_blocked(blocked)
                st.success(f"Blocked {sender}")
        else:
            st.success("Message seems safe.")
        st.markdown("#### Suggested replies")
        suggestions = [
            "I don’t want to argue. Please stop.",
            "Please don’t talk to me like that.",
            "I’m leaving the chat. If you continue, I’ll save evidence.",
            "If you’re upset, let’s talk later calmly."
        ]
        for i,s in enumerate(suggestions):
            if st.button(f"Reply {i+1}"):
                st.code(s)

st.markdown("---")
st.subheader("Blocked senders")
blocked = load_blocked()
if blocked:
    st.write(", ".join(blocked))
    if st.button("Clear list"):
        save_blocked([])
        st.success("Cleared blocked list.")
else:
    st.info("No blocked senders yet.")
