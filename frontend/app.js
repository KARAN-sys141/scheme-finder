"use strict";

const SCHEME_NAMES = {
  pmkisan: "PM-KISAN",
  pmjay: "Ayushman Bharat PM-JAY",
  vahli_dikri: "Vahli Dikri Yojana",
  ma_yojana: "MA Yojana",
};
const SCHEME_ICONS = { pmkisan: "🌾", pmjay: "🏥", vahli_dikri: "👧", ma_yojana: "💜" };
const SCHEME_ORDER = ["pmkisan", "pmjay", "vahli_dikri", "ma_yojana"];
const LANG_CODES = { en: "en-IN", hi: "hi-IN", gu: "gu-IN", hinglish: "en-IN" };

const I18N = {
  en: {
    sub: "Check government schemes in your language",
    placeholder: "Type your question...",
    send: "Send", newChat: "New chat", theme: "Change theme", mic: "Speak your question",
    thinking: ["Checking the scheme documents...", "Reading the rules...", "Preparing a simple answer..."],
    error: "Sorry, something went wrong. Please try again.",
    busy: "The assistant is busy right now. Please try again in a minute.",
    sources: "Sources", fb: "Was this helpful?", thanks: "Thanks for your feedback",
    copy: "Copy", copied: "Copied",
    disclaimer: "Information only. Please confirm on the official portal or at your nearest government office.",
    welcomeTitle: "Namaste! 👋",
    welcomeText: "Ask me about government schemes. You can write in English, Hindi, Gujarati or Hinglish.",
    pick: "TAP A SCHEME TO START",
    verdict: { likely_eligible: "Likely eligible", not_eligible: "Not eligible", check_portal: "Check on official portal", need_info: "More info needed" },
    cards: {
      pmkisan: { tag: "Income support for farmers", q: "How much money does a farmer get under PM-KISAN?" },
      pmjay: { tag: "Free hospital cover", q: "I am 72 years old. Can I get an Ayushman card?" },
      vahli_dikri: { tag: "Support for girl children", q: "What does Vahli Dikri Yojana give to a girl child?" },
      ma_yojana: { tag: "Gujarat health cover", q: "How much health cover does MA Yojana give per family?" },
    },
  },
  hi: {
    sub: "सरकारी योजनाओं की जानकारी, आपकी भाषा में",
    placeholder: "अपना सवाल लिखें...",
    send: "भेजें", newChat: "नई चैट", theme: "थीम बदलें", mic: "बोलकर सवाल पूछें",
    thinking: ["योजना के दस्तावेज़ देख रहा हूँ...", "नियम पढ़ रहा हूँ...", "आसान जवाब तैयार कर रहा हूँ..."],
    error: "माफ़ कीजिए, कुछ गड़बड़ हो गई। कृपया दोबारा कोशिश करें।",
    busy: "सहायक अभी व्यस्त है। कृपया एक मिनट बाद फिर कोशिश करें।",
    sources: "स्रोत", fb: "क्या यह जवाब मददगार था?", thanks: "आपकी राय के लिए धन्यवाद",
    copy: "कॉपी", copied: "कॉपी हो गया",
    disclaimer: "यह सिर्फ़ जानकारी है। कृपया आधिकारिक पोर्टल या नज़दीकी सरकारी कार्यालय में पुष्टि करें।",
    welcomeTitle: "नमस्ते! 👋",
    welcomeText: "सरकारी योजनाओं के बारे में पूछिए। आप हिंदी, अंग्रेज़ी, गुजराती या Hinglish में लिख सकते हैं।",
    pick: "शुरू करने के लिए योजना चुनें",
    verdict: { likely_eligible: "संभवतः पात्र", not_eligible: "पात्र नहीं", check_portal: "आधिकारिक पोर्टल पर जाँचें", need_info: "और जानकारी चाहिए" },
    cards: {
      pmkisan: { tag: "किसानों को आय सहायता", q: "पीएम किसान योजना में कितने रुपये मिलते हैं?" },
      pmjay: { tag: "मुफ़्त अस्पताल कवर", q: "मेरी उम्र 72 साल है, क्या मुझे आयुष्मान कार्ड मिल सकता है?" },
      vahli_dikri: { tag: "बेटियों के लिए सहायता", q: "वहली दीकरी योजना में बेटी को क्या मिलता है?" },
      ma_yojana: { tag: "गुजरात का स्वास्थ्य कवर", q: "MA योजना में एक परिवार को कितना हेल्थ कवर मिलता है?" },
    },
  },
  gu: {
    sub: "સરકારી યોજનાઓની માહિતી, તમારી ભાષામાં",
    placeholder: "તમારો પ્રશ્ન લખો...",
    send: "મોકલો", newChat: "નવી ચેટ", theme: "થીમ બદલો", mic: "બોલીને પ્રશ્ન પૂછો",
    thinking: ["યોજનાના દસ્તાવેજો જોઈ રહ્યો છું...", "નિયમો વાંચી રહ્યો છું...", "સરળ જવાબ તૈયાર કરી રહ્યો છું..."],
    error: "માફ કરશો, કંઈક ખોટું થયું. કૃપા કરીને ફરી પ્રયાસ કરો.",
    busy: "સહાયક હાલ વ્યસ્ત છે. કૃપા કરીને એક મિનિટ પછી ફરી પ્રયાસ કરો.",
    sources: "સ્ત્રોત", fb: "શું આ જવાબ ઉપયોગી હતો?", thanks: "તમારા પ્રતિભાવ બદલ આભાર",
    copy: "કૉપિ", copied: "કૉપિ થયું",
    disclaimer: "આ ફક્ત માહિતી છે. કૃપા કરીને સત્તાવાર પોર્ટલ અથવા નજીકની સરકારી કચેરીમાં ખાતરી કરો.",
    welcomeTitle: "નમસ્તે! 👋",
    welcomeText: "સરકારી યોજનાઓ વિશે પૂછો. તમે ગુજરાતી, હિન્દી, અંગ્રેજી કે Hinglish માં લખી શકો છો.",
    pick: "શરૂ કરવા માટે યોજના પસંદ કરો",
    verdict: { likely_eligible: "સંભવતઃ પાત્ર", not_eligible: "પાત્ર નથી", check_portal: "સત્તાવાર પોર્ટલ પર ચકાસો", need_info: "વધુ માહિતી જોઈએ" },
    cards: {
      pmkisan: { tag: "ખેડૂતોને આવક સહાય", q: "PM-KISAN યોજનામાં કેટલા રૂપિયા મળે છે?" },
      pmjay: { tag: "મફત હોસ્પિટલ કવર", q: "મારી ઉંમર 72 વર્ષ છે, શું મને આયુષ્માન કાર્ડ મળી શકે?" },
      vahli_dikri: { tag: "દીકરીઓ માટે સહાય", q: "વહાલી દીકરી યોજનામાં દીકરીને શું મળે છે?" },
      ma_yojana: { tag: "ગુજરાતનું આરોગ્ય કવર", q: "MA યોજનામાં પરિવારને કેટલું આરોગ્ય કવર મળે છે?" },
    },
  },
  hinglish: {
    sub: "Sarkari yojanaon ki jaankari, aapki bhasha me",
    placeholder: "Apna sawaal likhiye...",
    send: "Bhejo", newChat: "Nayi chat", theme: "Theme badlo", mic: "Bolkar poochho",
    thinking: ["Yojana ke documents dekh raha hoon...", "Rules padh raha hoon...", "Saral jawab bana raha hoon..."],
    error: "Sorry, kuch gadbad ho gayi. Please dobara try kijiye.",
    busy: "Assistant abhi busy hai. Please ek minute baad dobara try kijiye.",
    sources: "Sources", fb: "Kya ye jawab madadgaar tha?", thanks: "Feedback ke liye shukriya",
    copy: "Copy", copied: "Copy ho gaya",
    disclaimer: "Ye sirf jaankari hai. Please official portal ya nazdiki sarkari office me confirm kijiye.",
    welcomeTitle: "Namaste! 👋",
    welcomeText: "Sarkari yojanaon ke baare me poochiye. Aap Hindi, English, Gujarati ya Hinglish me likh sakte hain.",
    pick: "SHURU KARNE KE LIYE YOJANA CHUNO",
    verdict: { likely_eligible: "Shayad eligible", not_eligible: "Eligible nahi", check_portal: "Official portal par check karo", need_info: "Aur jaankari chahiye" },
    cards: {
      pmkisan: { tag: "Kisanon ko income support", q: "PM-KISAN me kitne paise milte hain?" },
      pmjay: { tag: "Free hospital cover", q: "Meri umar 72 saal hai, kya mujhe Ayushman card mil sakta hai?" },
      vahli_dikri: { tag: "Betiyon ke liye madad", q: "Vahli Dikri Yojana me ladki ko kya milta hai?" },
      ma_yojana: { tag: "Gujarat ka health cover", q: "MA Yojana me parivaar ko kitna health cover milta hai?" },
    },
  },
};

const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } },
  sget(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
  sset(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* ignore */ } },
  sdel(k) { try { sessionStorage.removeItem(k); } catch (e) { /* ignore */ } },
};

const $ = (id) => document.getElementById(id);
const messages = $("messages");
const input = $("input");
const sendBtn = $("send");
const micBtn = $("mic");
const toBottom = $("to-bottom");

const savedLang = store.get("ui_lang");
let uiLang = savedLang && I18N[savedLang] ? savedLang : "en";
let sessionId = store.sget("sid") || null;
let busy = false;
let stick = true;
let welcomeEl = null;
let revealState = null;

const t = () => I18N[uiLang];
const reduceMotion = () => !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
const isTouch = () => !!(window.matchMedia && window.matchMedia("(pointer: coarse)").matches);

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

/* ---------- theme ---------- */
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  store.set("theme", theme);
  $("theme-btn").textContent = theme === "dark" ? "☀️" : "🌙";
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", theme === "dark" ? "#1a1033" : "#efe6ff");
}
function toggleTheme() {
  applyTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
}

/* ---------- language ---------- */
function applyLang() {
  const s = t();
  document.documentElement.lang = uiLang === "hinglish" ? "hi-Latn" : uiLang;
  $("t-sub").textContent = s.sub;
  $("t-disclaimer").textContent = s.disclaimer;
  $("new-chat-label").textContent = s.newChat;
  $("new-chat").setAttribute("aria-label", s.newChat);
  $("theme-btn").setAttribute("aria-label", s.theme);
  micBtn.setAttribute("aria-label", s.mic);
  sendBtn.setAttribute("aria-label", s.send);
  input.placeholder = s.placeholder;
  document.querySelectorAll(".lang-btn").forEach((b) => {
    const on = b.dataset.lang === uiLang;
    b.classList.toggle("active", on);
    b.setAttribute("aria-pressed", on ? "true" : "false");
  });
  if (welcomeEl) {
    welcomeEl.remove();
    welcomeEl = null;
    showWelcome();
  }
}

/* ---------- scrolling ---------- */
function nearBottom() {
  return messages.scrollHeight - messages.scrollTop - messages.clientHeight < 120;
}
function scrollDown(force) {
  if (force) stick = true;
  if (stick) messages.scrollTop = messages.scrollHeight;
}
messages.addEventListener("scroll", () => {
  stick = nearBottom();
  toBottom.hidden = stick;
});
toBottom.addEventListener("click", () => {
  stick = true;
  messages.scrollTop = messages.scrollHeight;
  toBottom.hidden = true;
});

/* ---------- welcome ---------- */
function showWelcome() {
  const s = t();
  const hero = el("div", "hero");
  hero.appendChild(el("h2", "hero-title", s.welcomeTitle));
  hero.appendChild(el("p", "hero-sub", s.welcomeText));
  hero.appendChild(el("div", "hero-pick", s.pick));
  const grid = el("div", "cards");
  SCHEME_ORDER.forEach((id) => {
    const c = document.createElement("button");
    c.type = "button";
    c.className = "card";
    c.appendChild(el("div", "card-icon", SCHEME_ICONS[id]));
    c.appendChild(el("div", "card-name", SCHEME_NAMES[id]));
    c.appendChild(el("div", "card-tag", s.cards[id].tag));
    c.addEventListener("click", () => send(t().cards[id].q));
    grid.appendChild(c);
  });
  hero.appendChild(grid);
  messages.appendChild(hero);
  welcomeEl = hero;
}
function clearWelcome() {
  if (welcomeEl) {
    welcomeEl.remove();
    welcomeEl = null;
  }
}

/* ---------- rendering (textContent only, never innerHTML) ---------- */
function renderWithCitations(target, text) {
  text.split(/(\[\d+\])/g).forEach((part) => {
    const m = part.match(/^\[(\d+)\]$/);
    if (m) {
      target.appendChild(el("span", "cite", m[1]));
    } else if (part) {
      target.appendChild(document.createTextNode(part));
    }
  });
}

function makeAvatar() {
  return el("div", "avatar", "✨");
}

function addUser(text) {
  const row = el("div", "row user");
  row.appendChild(el("div", "msg user", text));
  messages.appendChild(row);
  scrollDown(true);
}

function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text);
  }
  return new Promise((resolve, reject) => {
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      ta.remove();
      ok ? resolve() : reject(new Error("copy failed"));
    } catch (e) {
      reject(e);
    }
  });
}

function buildVerdicts(verdicts) {
  const keys = Object.keys(verdicts || {});
  if (!keys.length) return null;
  const wrap = el("div", "verdicts");
  keys.forEach((k) => {
    const st = verdicts[k];
    const row = el("div", "verdict v-" + st);
    row.appendChild(el("span", "vname", SCHEME_NAMES[k] || k));
    row.appendChild(el("span", "vbadge", t().verdict[st] || st));
    wrap.appendChild(row);
  });
  return wrap;
}

function buildSources(list) {
  if (!list || !list.length) return null;
  const det = el("details", "sources");
  det.appendChild(el("summary", "", `${t().sources} (${list.length})`));
  list.forEach((s) => {
    const c = el("div", "source-card");
    c.appendChild(el("b", "", `[${s.n}] ${s.scheme_name} · ${s.section}`));
    c.appendChild(el("div", "", s.snippet));
    c.appendChild(el("small", "", s.file));
    det.appendChild(c);
  });
  return det;
}

function buildActions(text, feedback) {
  const bar = el("div", "actions");
  const copy = el("button", "act-btn", "⧉ " + t().copy);
  copy.type = "button";
  copy.addEventListener("click", () => {
    copyText(text).then(() => {
      copy.textContent = "✓ " + t().copied;
      setTimeout(() => { copy.textContent = "⧉ " + t().copy; }, 1500);
    }).catch(() => {});
  });
  bar.appendChild(copy);

  if (feedback) {
    const label = el("span", "fb-label", t().fb);
    const up = el("button", "act-btn", "👍");
    const down = el("button", "act-btn", "👎");
    up.type = "button";
    down.type = "button";
    const rate = (rating) => {
      up.disabled = true;
      down.disabled = true;
      label.textContent = t().thanks;
      fetch("/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId || "none", rating, message: feedback.message, reply: feedback.reply }),
      }).catch(() => {});
    };
    up.addEventListener("click", () => rate("up"));
    down.addEventListener("click", () => rate("down"));
    bar.append(label, up, down);
  }
  return bar;
}

function stopReveal() {
  if (revealState) {
    clearInterval(revealState.timer);
    const done = revealState.done;
    revealState = null;
    done();
  }
}

function addBot(text, extra, animate) {
  extra = extra || {};
  const row = el("div", "row bot");
  row.appendChild(makeAvatar());
  const bubble = el("div", "msg bot");
  if (extra.kind === "followup") bubble.classList.add("followup");
  const body = el("div", "msg-text");
  bubble.appendChild(body);
  row.appendChild(bubble);
  messages.appendChild(row);
  scrollDown(true);

  let finished = false;
  const finish = () => {
    if (finished) return;
    finished = true;
    body.replaceChildren();
    renderWithCitations(body, text);
    const verdicts = buildVerdicts(extra.verdicts);
    if (verdicts) bubble.appendChild(verdicts);
    const sources = buildSources(extra.sources);
    if (sources) bubble.appendChild(sources);
    if (extra.kind !== "error") bubble.appendChild(buildActions(text, extra.feedback));
    scrollDown();
  };

  if (animate && !reduceMotion()) {
    const tokens = text.split(/(\s+)/);
    let i = 0;
    const timer = setInterval(() => {
      i += 4;
      body.replaceChildren();
      renderWithCitations(body, tokens.slice(0, i).join(""));
      scrollDown();
      if (i >= tokens.length) {
        clearInterval(timer);
        revealState = null;
        finish();
      }
    }, 22);
    revealState = { timer, done: finish };
  } else {
    finish();
  }
}

function addTyping() {
  const row = el("div", "row bot");
  row.appendChild(makeAvatar());
  const bubble = el("div", "msg bot");
  const wrap = el("div", "typing-bubble");
  const dots = el("span", "dots");
  dots.append(el("span"), el("span"), el("span"));
  const label = el("span", "", t().thinking[0]);
  wrap.append(dots, label);
  bubble.appendChild(wrap);
  row.appendChild(bubble);
  messages.appendChild(row);
  scrollDown(true);
  let n = 0;
  const timer = setInterval(() => {
    n = (n + 1) % t().thinking.length;
    label.textContent = t().thinking[n];
  }, 2500);
  return {
    stop() {
      clearInterval(timer);
      row.remove();
    },
  };
}

/* ---------- confetti ---------- */
function burst() {
  if (reduceMotion()) return;
  const fx = $("fx");
  const colors = ["#c4b5fd", "#a78bfa", "#8b5cf6", "#7c3aed", "#f0abfc", "#ffffff"];
  for (let i = 0; i < 36; i++) {
    const p = el("span", "confetti");
    p.style.left = Math.random() * 100 + "vw";
    p.style.background = colors[i % colors.length];
    p.style.setProperty("--dx", Math.random() * 160 - 80 + "px");
    p.style.setProperty("--rot", Math.random() * 720 - 360 + "deg");
    p.style.animationDelay = Math.random() * 0.4 + "s";
    p.style.animationDuration = 1.4 + Math.random() * 1.1 + "s";
    fx.appendChild(p);
    setTimeout(() => p.remove(), 3300);
  }
}

/* ---------- composer ---------- */
function autoGrow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 140) + "px";
}
function updateCounter() {
  const n = input.value.length;
  $("counter").textContent = n > 400 ? n + "/500" : "";
}
function updateSend() {
  sendBtn.disabled = busy || !input.value.trim();
}

async function send(text) {
  text = (text || "").trim();
  if (!text || busy) return;
  stopReveal();
  clearWelcome();
  addUser(text);
  input.value = "";
  autoGrow();
  updateCounter();
  busy = true;
  updateSend();
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
    typing.stop();
    if (!res.ok) {
      addBot(res.status === 503 ? t().busy : t().error, { kind: "error" }, false);
      return;
    }
    const data = await res.json();
    sessionId = data.session_id;
    store.sset("sid", sessionId);
    addBot(
      data.reply,
      {
        kind: data.kind,
        sources: data.sources || [],
        verdicts: data.verdicts || {},
        feedback: { message: text, reply: data.reply },
      },
      true
    );
    if (data.kind === "verdict" && Object.values(data.verdicts || {}).indexOf("likely_eligible") !== -1) {
      burst();
    }
  } catch (e) {
    typing.stop();
    addBot(t().error, { kind: "error" }, false);
  } finally {
    clearTimeout(timer);
    busy = false;
    updateSend();
    if (!isTouch()) input.focus();
  }
}

function newChat() {
  stopReveal();
  store.sdel("sid");
  sessionId = null;
  messages.replaceChildren();
  welcomeEl = null;
  stick = true;
  toBottom.hidden = true;
  showWelcome();
  input.value = "";
  autoGrow();
  updateCounter();
  updateSend();
}

/* ---------- voice input (only where the browser supports it) ---------- */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognizer = null;
let listening = false;
if (SR) {
  micBtn.hidden = false;
  micBtn.addEventListener("click", () => {
    try {
      if (listening && recognizer) {
        recognizer.stop();
        return;
      }
      recognizer = new SR();
      recognizer.lang = LANG_CODES[uiLang];
      recognizer.interimResults = false;
      recognizer.maxAlternatives = 1;
      recognizer.onstart = () => { listening = true; micBtn.classList.add("on"); };
      recognizer.onend = () => { listening = false; micBtn.classList.remove("on"); };
      recognizer.onerror = () => { listening = false; micBtn.classList.remove("on"); };
      recognizer.onresult = (e) => {
        const spoken = e.results[0][0].transcript;
        input.value = (input.value + " " + spoken).trim().slice(0, 500);
        autoGrow();
        updateCounter();
        updateSend();
        input.focus();
      };
      recognizer.start();
    } catch (err) {
      listening = false;
      micBtn.classList.remove("on");
    }
  });
}

/* ---------- events ---------- */
$("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  send(input.value);
});
input.addEventListener("input", () => {
  autoGrow();
  updateCounter();
  updateSend();
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    send(input.value);
  }
});
$("new-chat").addEventListener("click", newChat);
$("theme-btn").addEventListener("click", toggleTheme);
$("lang-bar").addEventListener("click", (e) => {
  const b = e.target.closest(".lang-btn");
  if (!b || !I18N[b.dataset.lang]) return;
  uiLang = b.dataset.lang;
  store.set("ui_lang", uiLang);
  applyLang();
});

/* ---------- start ---------- */
applyTheme(document.documentElement.getAttribute("data-theme") || "dark");
showWelcome();
applyLang();
updateSend();