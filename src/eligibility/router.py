ALIASES = {
    "pmkisan": [
        "pm-kisan", "pm kisan", "pmkisan", "kisan samman", "kisan", "kisaan", "farmer", "kheti",
        "पीएम किसान", "पीएम-किसान", "किसान", "खेती", "ખેડૂત", "ખેતી", "કિસાન",
    ],
    "pmjay": [
        "ayushman", "pm-jay", "pmjay", "jan arogya", "vay vandana", "vaya vandana",
        "आयुष्मान", "वय वंदना", "આયુષ્માન", "વય વંદના",
    ],
    "vahli_dikri": [
        "vahli", "vahali", "vhali", "dikri", "dikari", "daughter", "beti", "ladki",
        "वहली", "वहाली", "दीकरी", "बेटी", "लड़की", "વહાલી", "દીકરી",
    ],
    "ma_yojana": [
        "ma yojana", "maa yojana", "amrutum", "amrutam", "ma vatsalya", "maa vatsalya",
        "ma योजना", "मा योजना", "अमृतम", "મા યોજના", "અમૃતમ",
    ],
}

HEALTH_WORDS = [
    "health insurance", "insurance", "ilaj", "hospital", "medical", "swasthya",
    "इलाज", "अस्पताल", "स्वास्थ्य", "બીમારી", "સારવાર", "હોસ્પિટલ", "આરોગ્ય",
]


def detect_schemes(text):
    t = text.lower()
    found = [s for s, words in ALIASES.items() if any(w in t for w in words)]
    if not found and any(w in t for w in HEALTH_WORDS):
        found = ["pmjay", "ma_yojana"]
    return found