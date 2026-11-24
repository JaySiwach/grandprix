"""Persistent race and championship leaderboards stored as JSON."""
import json
import os
import time
from config.settings import SAVE_FILE


def load_scores():
    if not os.path.exists(SAVE_FILE):
        return []
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                item.setdefault("type", "championship")
            return data
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return []


def _write(records):
    folder = os.path.dirname(SAVE_FILE)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def save_race_result(name, race_name, race_number, position, score, elapsed,
                     correct, wrong, status="finished"):
    records = load_scores()
    records.append({
        "type": "race", "name": name, "race": race_name,
        "race_number": race_number, "position": int(position),
        "score": int(score), "time": round(float(elapsed), 1),
        "correct": int(correct), "wrong": int(wrong), "status": status,
        "date": time.strftime("%Y-%m-%d %H:%M")
    })
    champs = [r for r in records if r.get("type") != "race"][-50:]
    races = [r for r in records if r.get("type") == "race"][-250:]
    try:
        _write(champs + races)
    except OSError:
        pass
    return races


def save_result(name, score, total_time, correct, wrong, race_positions=None):
    records = load_scores()
    records.append({
        "type": "championship", "name": name, "score": int(score),
        "time": round(float(total_time), 1), "correct": int(correct),
        "wrong": int(wrong), "race_positions": list(race_positions or []),
        "date": time.strftime("%Y-%m-%d %H:%M")
    })
    champs = sorted(
        [r for r in records if r.get("type") != "race"],
        key=lambda r: (-r.get("score", 0), r.get("time", 0))
    )[:50]
    races = [r for r in records if r.get("type") == "race"][-250:]
    try:
        _write(champs + races)
    except OSError:
        pass
    return champs
