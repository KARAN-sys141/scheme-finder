from src.eligibility.graph import chat_turn


def run(title, turns):
    print("\n" + "#" * 70)
    print(title)
    state = {}
    for msg in turns:
        print("\nUSER:", msg)
        state = chat_turn(state, msg)
        print(f"BOT [{state['kind']}]:\n{state['reply']}")
        print("   profile so far:", state.get("profile"))
        print("   verdicts:", {r["scheme_id"]: r["status"] for r in state.get("results", [])})


run("A) Hindi, PM-KISAN (follow-up, then verdict)", [
    "क्या मैं किसान योजना के लिए पात्र हूँ?",
    "हाँ, मेरे पास 2 हेक्टेयर ज़मीन है और मैं इनकम टैक्स नहीं भरता",
])

run("B) Hinglish, health insurance (follow-up, then verdict)", [
    "Mujhe health insurance wali sarkari yojana chahiye, kya mujhe mil sakti hai?",
    "Gujarat, 40 saal, family income 3 lakh hai",
])

run("C) Gujarati, third daughter (direct verdict)", [
    "મારી ત્રીજી દીકરીનો જન્મ 2022 માં થયો છે. શું તેને વહાલી દીકરી યોજનાનો લાભ મળશે?",
])

run("D) No scheme named", [
    "Can I get some government benefit?",
])