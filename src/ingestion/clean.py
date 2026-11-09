import re

FOOTER_STARTS = ["Something went wrong", "कुछ गलत हो गया"]
FOOTER_END = "24303714"  # last line of the MyScheme footer (phone number)

NOISE_LINES = {
    "uploaded image", "ok", "cancel", "sign out", "quick links", "about us",
    "contact us", "screen reader", "accessibility statement", "disclaimer",
    "terms & conditions", "dashboard", "useful links", "get in touch",
    "connect on social media",
}


def remove_footer(text: str) -> str:
    out, skipping = [], False
    for line in text.split("\n"):
        if not skipping and any(m in line for m in FOOTER_STARTS):
            skipping = True
        if skipping:
            if FOOTER_END in line:
                skipping = False
            continue
        out.append(line)
    return "\n".join(out)


def clean_text(text: str) -> str:
    text = text.replace("\r", "").replace("\u00a0", " ")
    text = remove_footer(text)

    # MA Yojana page: bullets are glued together, put each on its own line
    text = re.sub(r"(?<=\S)(Any member\(s\)|Class-3 and Class-4|Senior Citizens with)", r"\n\1", text)

    lines = []
    for line in text.split("\n"):
        s = re.sub(r"[ \t]+", " ", line.replace("Uploaded Image", "")).strip()
        if s.lower() in NOISE_LINES:
            continue
        lines.append(s)

    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()