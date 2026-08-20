import re


EMOTION_KEYWORDS = {
    "anxious": [
        "anxious", "anxiety", "nervous", "worried", "scared",
        "fear", "panic", "stress", "stressed", "ghabrahat",
        "ghabra raha", "dar", "darr", "tension", "pareshan"
    ],
    "sad": [
        "sad", "unhappy", "cry", "crying", "hurt", "upset",
        "depressed", "lonely", "udaas", "dukhi", "akela",
        "akela feel", "low"
    ],
    "happy": [
        "happy", "great", "good", "excited", "amazing",
        "wonderful", "khush", "badiya", "accha", "acha"
    ],
    "frustrated": [
        "frustrated", "angry", "annoyed", "irritated",
        "hate", "gussa", "pareshan"
    ],
    "confident": [
        "confident", "confidence", "ready", "comfortable",
        "sure", "proud", "believe"
    ],
    "calm": [
        "calm", "relaxed", "peaceful", "fine", "okay",
        "theek", "shant", "relax"
    ],
}


POSITIVE_WORDS = {
    "happy", "good", "great", "amazing", "excellent",
    "love", "like", "excited", "confident", "proud",
    "peaceful", "calm", "badiya", "khush", "accha", "acha"
}

NEGATIVE_WORDS = {
    "sad", "bad", "hate", "worried", "nervous", "anxious",
    "scared", "stress", "stressed", "angry", "frustrated",
    "lonely", "hurt", "upset", "depressed", "dukhi",
    "udaas", "darr", "ghabrahat", "pareshan"
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def analyze_sentiment(text: str) -> dict:
    """
    Lightweight SaraSense sentiment/emotion analysis.

    This is a communication/wellbeing signal only.
    It is NOT a medical diagnosis.
    """

    if not text or not text.strip():
        return {
            "sentiment": "neutral",
            "emotion": "neutral",
            "intensity": 0,
            "confidence": 0.0,
            "suggested_action": "continue_conversation",
            "is_diagnostic": False,
        }

    normalized = _normalize(text)

    words = set(re.findall(r"[a-zA-Z]+", normalized))

    positive_count = len(words.intersection(POSITIVE_WORDS))
    negative_count = len(words.intersection(NEGATIVE_WORDS))

    emotion_scores = {}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            if " " in keyword:
                if keyword in normalized:
                    score += 2
            elif keyword in words:
                score += 1

        emotion_scores[emotion] = score

    best_emotion = max(
        emotion_scores,
        key=emotion_scores.get
    )

    best_score = emotion_scores[best_emotion]

    if best_score == 0:
        emotion = "neutral"
    else:
        emotion = best_emotion

    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    total_signal = positive_count + negative_count + best_score

    intensity = min(
        100,
        max(
            10,
            total_signal * 12
        )
    )

    confidence = min(
        0.95,
        0.50 + (best_score * 0.08)
    )

    if emotion in {"anxious", "sad", "lonely"}:
        suggested_action = "gentle_support"
    elif emotion == "confident":
        suggested_action = "encourage_progress"
    elif emotion == "frustrated":
        suggested_action = "calm_and_support"
    elif emotion in {"happy", "calm"}:
        suggested_action = "continue_conversation"
    else:
        suggested_action = "continue_conversation"

    return {
        "sentiment": sentiment,
        "emotion": emotion,
        "intensity": intensity,
        "confidence": round(confidence, 2),
        "suggested_action": suggested_action,
        "is_diagnostic": False,
    }