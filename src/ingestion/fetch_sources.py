import os, re, requests
import fitz  # pymupdf
from bs4 import BeautifulSoup

RAW = "data/raw"
HEADERS = {"User-Agent": "Mozilla/5.0"}

PAGES = {
    "pmkisan_page_en": "https://vikaspedia.in/agriculture/policies-and-schemes/crops-related/pradhan-mantri-kisan-samman-nidhi",
    "pmjay_page_en": "https://en.vikaspedia.in/viewcontent/health/nrhm/national-health-mission/ayushman-bharat%E2%80%93pm-jan-arogya-yojana?lgn=en",
    "pmjay_page_hi": "https://en.vikaspedia.in/viewcontent/health/nrhm/national-health-mission/ayushman-bharat%E2%80%93pm-jan-arogya-yojana?lgn=hi",
    "pmjay_page_gu": "https://en.vikaspedia.in/viewcontent/health/nrhm/national-health-mission/ayushman-bharat%E2%80%93pm-jan-arogya-yojana?lgn=gu",
    "vahli_dikri_page_en": "https://en.vikaspedia.in/viewcontent/schemesall/state-specific-schemes/welfare-schemes-of-gujarat/vahli-dikri-yojana?lgn=en",
    "vahli_dikri_page_hi": "https://en.vikaspedia.in/viewcontent/schemesall/state-specific-schemes/welfare-schemes-of-gujarat/vahli-dikri-yojana?lgn=hi",
    "vahli_dikri_page_gu": "https://en.vikaspedia.in/viewcontent/schemesall/state-specific-schemes/welfare-schemes-of-gujarat/vahli-dikri-yojana?lgn=gu",
    "ma_yojana_page_en": "https://www.myscheme.gov.in/schemes/ma",
    "ma_yojana_page_hi": "https://www.myscheme.gov.in/hi/schemes/ma",
}

PDFS = {
    "pmkisan_faq_en": "https://PMkisan.gov.in/Documents/RevisedFAQ.pdf",
    "pmkisan_pib_faq_en": "https://static.pib.gov.in/WriteReadData/specificdocs/documents/2021/nov/doc2021112361.pdf",
}

def clean(text):
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()

def count_script(text):
    deva = len(re.findall(r"[\u0900-\u097F]", text))
    guj = len(re.findall(r"[\u0A80-\u0AFF]", text))
    return deva, guj

os.makedirs(RAW, exist_ok=True)

for name, url in PAGES.items():
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = clean(soup.get_text("\n"))
        path = f"{RAW}/{name}.txt"
        open(path, "w", encoding="utf-8").write(text)
        print("OK  ", name, len(text), "chars  (hindi, gujarati) =", count_script(text))
    except Exception as e:
        print("FAIL", name, e)

for name, url in PDFS.items():
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        pdf_path = f"{RAW}/{name}.pdf"
        open(pdf_path, "wb").write(r.content)
        doc = fitz.open(pdf_path)
        text = clean("\n".join(p.get_text() for p in doc))
        open(f"{RAW}/{name}.txt", "w", encoding="utf-8").write(text)
        print("OK  ", name, len(doc), "pages", len(text), "chars")
    except Exception as e:
        print("FAIL", name, e)