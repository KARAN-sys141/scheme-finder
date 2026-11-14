const I18N = {
  en: {
    sub: "Check government schemes in your language",
    placeholder: "Type your question...", send: "Send", newChat: "New chat",
    thinking: "Checking the scheme documents...",
    error: "Sorry, something went wrong. Please try again.",
    busy: "The assistant is busy right now. Please try again in a minute.",
    sources: "Sources", fb: "Was this helpful?", thanks: "Thanks for your feedback",
    disclaimer: "Information only. Please confirm on the official portal or at your nearest government office.",
    welcome: "Hello! Ask me about PM-KISAN, Ayushman Bharat, Vahli Dikri Yojana or MA Yojana. You can write in English, Hindi, Gujarati or Hinglish.",
    chips: ["How much money does a farmer get under PM-KISAN?", "I am 72 years old. Can I get an Ayushman card?", "What does Vahli Dikri Yojana give to a girl child?"],
  },
  hi: {
    sub: "सरकारी योजनाओं की जानकारी, आपकी भाषा में",
    placeholder: "अपना सवाल लिखें...", send: "भेजें", newChat: "नई चैट",
    thinking: "योजना के दस्तावेज़ देख रहा हूँ...",
    error: "माफ़ कीजिए, कुछ गड़बड़ हो गई। कृपया दोबारा कोशिश करें।",
    busy: "सहायक अभी व्यस्त है। कृपया एक मिनट बाद फिर कोशिश करें।",
    sources: "स्रोत", fb: "क्या यह जवाब मददगार था?", thanks: "आपकी राय के लिए धन्यवाद",
    disclaimer: "यह सिर्फ़ जानकारी है। कृपया आधिकारिक पोर्टल या नज़दीकी सरकारी कार्यालय में पुष्टि करें।",
    welcome: "नमस्ते! आप PM-KISAN, आयुष्मान भारत, वहली दीकरी योजना या MA योजना के बारे में पूछ सकते हैं। आप हिंदी, अंग्रेज़ी, गुजराती या Hinglish में लिख सकते हैं।",
    chips: ["पीएम किसान योजना में कितने रुपये मिलते हैं?", "मेरी उम्र 72 साल है, क्या मुझे आयुष्मान कार्ड मिल सकता है?", "वहली दीकरी योजना में बेटी को क्या मिलता है?"],
  },
  gu: {
    sub: "સરકારી યોજનાઓની માહિતી, તમારી ભાષામાં",
    placeholder: "તમારો પ્રશ્ન લખો...", send: "મોકલો", newChat: "નવી ચેટ",
    thinking: "યોજનાના દસ્તાવેજો જોઈ રહ્યો છું...",
    error: "માફ કરશો, કંઈક ખોટું થયું. કૃપા કરીને ફરી પ્રયાસ કરો.",
    busy: "સહાયક હાલ વ્યસ્ત છે. કૃપા કરીને એક મિનિટ પછી ફરી પ્રયાસ કરો.",
    sources: "સ્ત્રોત", fb: "શું આ જવાબ ઉપયોગી હતો?", thanks: "તમારા પ્રતિભાવ બદલ આભાર",
    disclaimer: "આ ફક્ત માહિતી છે. કૃપા કરીને સત્તાવાર પોર્ટલ અથવા નજીકની સરકારી કચેરીમાં ખાતરી કરો.",
    welcome: "નમસ્તે! તમે PM-KISAN, આયુષ્માન ભારત, વહાલી દીકરી યોજના અથવા MA યોજના વિશે પૂછી શકો છો. તમે ગુજરાતી, હિન્દી, અંગ્રેજી કે Hinglish માં લખી શકો છો.",
    chips: ["PM-KISAN યોજનામાં કેટલા રૂપિયા મળે છે?", "મારી ઉંમર 72 વર્ષ છે, શું મને આયુષ્માન કાર્ડ મળી શકે?", "વહાલી દીકરી યોજનામાં દીકરીને શું મળે છે?"],
  },
  hinglish: {
    sub: "Sarkari yojanaon ki jaankari, aapki bhasha me",
    placeholder: "Apna sawaal likhiye...", send: "Bhejo", newChat: "Nayi chat",
    thinking: "Yojana ke documents dekh raha hoon...",
    error: "Sorry, kuch gadbad ho gayi. Please dobara try kijiye.",
    busy: "Assistant abhi busy hai. Please ek minute baad dobara try kijiye.",
    sources: "Sources", fb: "Kya ye jawab madadgaar tha?", thanks: "Feedback ke liye shukriya",
    disclaimer: "Ye sirf jaankari hai. Please official portal ya nazdiki sarkari office me confirm kijiye.",
    welcome: "Namaste! Aap PM-KISAN, Ayushman Bharat, Vahli Dikri Yojana ya MA Yojana ke baare me pooch sakte hain. Aap Hindi, English, Gujarati ya Hinglish me likh sakte hain.",
    chips: ["PM-KISAN me kitne paise milte hain?", "Meri umar 72 saal hai, kya mujhe Ayushman card mil sakta hai?", "Vahli Dikri Yojana me ladki ko kya milta hai?"],
  },
};

const $ = (id) => document.getElementById(id);
const messages = $("messages");
const input = $("input");
const sendBtn = $("send");
const langSel = $("ui-lang");

let uiLang = localStorage.getItem("ui_lang") || "en";
let sessionId = sessionStorage.getItem("sid") || null;
const t = () => I18N[uiLang];

function applyLang() {
  const s = t();
  document.documentElement.lang = uiLang === "hinglish" ? "hi-Latn" : uiLang;
  $("t-sub").textContent = s.sub;
  $("t-disclaimer").textContent = s.disclaimer;
  $("new-chat").textContent = s.newChat;
  sendBtn.textContent = s.send;
  input.placeholder = s.placeholder;
  langSel.value = uiLang;
  const chips = $("chips");
  chips.replaceChildren();
  s.chips.forEach((q) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = q;
    b.addEventListener("click", () => send(q));
    chips.appendChild(b);
  });
}

function scrollDown() {
  messages.scrollTop = messages.scrollHeight;
}

// Never use innerHTML for model or user text: textContent cannot inject HTML or scripts.
function renderWithCitations(el, text) {
  text.split(/(\[\d+\])/g).forEach((part) => {
    const m = part.match(/^\[(\d+)\]$/);
    if (m) {
      const s = document.createElement("span");
      s.className = "cite";
      s.textContent = m[1];
      el.appendChild(s);
    } else if (part) {
      el.appendChild(document.createTextNode(part));
    }
  });
}

function addUser(text) {
  const d = document.createElement("div");
  d.className = "msg user";
  d.textContent = text;
  messages.appendChild(d);
  scrollDown();
}

function addBot(text, extra) {
  const d = document.createElement("div");
  d.className = "msg bot";
  renderWithCitations(d, text);

  if (extra && extra.sources && extra.sources.length) {
    const det = document.createElement("details");
    det.className = "sources";
    const sum = document.createElement("summary");
    sum.textContent = `${t().sources} (${extra.sources.length})`;
    det.appendChild(sum);
    extra.sources.forEach((s) => {
      const c = document.createElement("div");
      c.className = "source-card";
      const b = document.createElement("b");
      b.textContent = `[${s.n}] ${s.scheme_name} · ${s.section}`;
      const p = document.createElement("div");
      p.textContent = s.snippet;
      const f = document.createElement("small");
      f.textContent = s.file;
      c.append(b, p, f);
      det.appendChild(c);
    });
    d.appendChild(det);
  }

  if (extra && extra.feedback) {
    const fb = document.createElement("div");
    fb.className = "fb";
    const label = document.createElement("span");
    label.textContent = t().fb;
    const up = document.createElement("button");
    up.type = "button";
    up.textContent = "👍";
    const down = document.createElement("button");
    down.type = "button";
    down.textContent = "👎";
    const rate = (rating) => {
      up.disabled = down.disabled = true;
      label.textContent = t().thanks;
      fetch("/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId || "none", rating, ...extra.feedback }),
      }).catch(() => {});
    };
    up.addEventListener("click", () => rate("up"));
    down.addEventListener("click", () => rate("down"));
    fb.append(label, up, down);
    d.appendChild(fb);
  }

  messages.appendChild(d);
  scrollDown();
  return d;
}

function addTyping() {
  const d = document.createElement("div");
  d.className = "msg bot typing";
  d.textContent = t().thinking;
  messages.appendChild(d);
  scrollDown();
  return d;
}

function setBusy(b) {
  sendBtn.disabled = b;
  input.disabled = b;
}

async function send(text) {
  text = (text || "").trim();
  if (!text) return;
  $("chips").replaceChildren();
  addUser(text);
  input.value = "";
  setBusy(true);
  const typing = addTyping();
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 90000);
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId }),
      signal: ctrl.signal,
    });
    typing.remove();
    if (!res.ok) {
      addBot(res.status === 503 ? t().busy : t().error);
      return;
    }
    const data = await res.json();
    sessionId = data.session_id;
    sessionStorage.setItem("sid", sessionId);
    addBot(data.reply, { sources: data.sources, feedback: { message: text, reply: data.reply } });
  } catch (e) {
    typing.remove();
    addBot(t().error);
  } finally {
    clearTimeout(timer);
    setBusy(false);
    input.focus();
  }
}

function newChat() {
  sessionStorage.removeItem("sid");
  sessionId = null;
  messages.replaceChildren();
  addBot(t().welcome);
  applyLang();
}

$("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  send(input.value);
});
$("new-chat").addEventListener("click", newChat);
langSel.addEventListener("change", () => {
  uiLang = langSel.value;
  localStorage.setItem("ui_lang", uiLang);
  applyLang();
});

applyLang();
addBot(t().welcome);