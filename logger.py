import json
import os
from datetime import datetime

LOG_FILE = "complaint_log.json"

def log_complaint(user_input, bot_response):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_complaint": user_input,
        "bot_response": bot_response
    }

    # Load existing logs
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    # Add new entry
    logs.append(log_entry)

    # Save back
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def get_all_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_stats():
    logs = get_all_logs()
    total = len(logs)
    return total