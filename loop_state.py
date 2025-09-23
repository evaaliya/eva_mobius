def detect_emotional_loop(state: LoopState, window=6):
    recent = [m for m in state.history if m.role == "user"][-window:]
    text = " ".join(m.text.lower() for m in recent)
    patterns = {
        "self-blame": any(w in text for w in ["я дура", "ненавижу себя", "бесит меня", "я слабая"]),
        "fear": any(w in text for w in ["страшно", "боюсь", "тревога", "паника"]),
        "resolve": any(w in text for w in ["я смогу", "я знаю", "я сделаю", "я иду"]),
    }
    return patterns

def reflect(state: LoopState, user_text: str, assistant_text: str):
    loops = detect_emotional_loop(state)
    insights = []
    if loops["self-blame"]:
        insights.append("Наметилась петля самокритики; в следующем витке перейти к мягкой переформулировке самоценности.")
        # bias next s slightly toward inner-support
        state.energy = min(1.0, state.energy + 0.1)
    if loops["resolve"]:
        insights.append("Рост решимости; можно усилить стратегическую конкретику на следующем витке.")
        # encourage outer-structure next time
        state.energy = max(0.3, state.energy - 0.05)

    if insights:
        store(state, "meta", " | ".join(insights), tags=["reflection"])
