from src.pipeline import ask

state = {}
for msg in [
    "How much money does a farmer get under PM-KISAN?",
    "क्या मैं किसान योजना के लिए पात्र हूँ?",
    "हाँ, मेरे पास 2 हेक्टेयर ज़मीन है और मैं इनकम टैक्स नहीं भरता",
    "Give me a recipe for dhokla.",
]:
    rec, state = ask(msg, state)
    print("\nUSER:", msg)
    print(f"[{rec['route']}/{rec['kind']}] {rec['latency_s']}s  cited={rec['cited']}  verdicts={rec['verdicts']}")
    print(rec["reply"])