import re

DEVA = re.compile(r"[\u0900-\u097F]")
GUJ = re.compile(r"[\u0A80-\u0AFF]")

# Hinglish words that are NOT also common English words ("me", "do", "main" are risky, so main is kept only with >=2 hits rule)
HINGLISH_WORDS = {
    "kya", "hai", "hain", "hoon", "hun", "mujhe", "mere", "meri", "mera", "kitne", "kitna",
    "kitni", "milta", "milti", "milega", "mil", "nahi", "nahin", "aur", "kaise", "kab",
    "kaun", "kaunsi", "kiske", "liye", "wali", "wala", "rehta", "rehti", "chahiye",
    "sakta", "sakti", "bata", "batao", "karo", "kare", "aap", "saal", "achhi", "achha",
    "kuch", "koi", "kaisa", "aaj", "sarkari", "sabse", "badi", "ka", "ki", "ke", "ko",
    "se", "main", "mein", "padosi", "ladki", "paise", "paisa", "rakam", "ilaj", "umar",
}


def detect_language(text: str) -> str:
    deva = len(DEVA.findall(text))
    guj = len(GUJ.findall(text))
    if guj > deva:
        return "gu"
    if deva > 0:
        return "hi"
    words = re.findall(r"[a-z]+", text.lower())
    hits = sum(w in HINGLISH_WORDS for w in words)
    if hits >= 2 or (words and hits / len(words) >= 0.2):
        return "hinglish"
    return "en"