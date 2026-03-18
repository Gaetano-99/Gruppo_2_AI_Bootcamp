# ============================================================================
# Federico360 — Pagina di Login
# Università Federico II di Napoli
# ============================================================================

import sys
import os
import base64
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from werkzeug.security import check_password_hash

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db
from views.accessibilita import dialog_accessibilita, get_css_accessibilita


# ---------------------------------------------------------------------------
# *** PERCORSI IMMAGINI ***
# ---------------------------------------------------------------------------
_ASSETS_DIR   = Path(__file__).parent / "assets"
LOGO_PATH     = _ASSETS_DIR / "Gruppo_2_AI_Bootcamp\views\logo\LOGO_FEDERICO.png"   # <- CAMBIA QUI se necessario
SIGILLO_PATH  = _ASSETS_DIR / "Gruppo_2_AI_Bootcamp\views\logo\LOGO_FEDERICO.png"            # <- CAMBIA QUI se necessario

_LOGO_B64_EMBEDDED    = ""   # fallback: lascia vuoto o incolla il base64
_SIGILLO_B64_EMBEDDED = ""

def _img_to_b64(path: Path, fallback_b64: str) -> str:
    try:
        if path.exists():
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return fallback_b64


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #eaecf3;
    --navy:      #1a2340;
    --navy-mid:  #2c3a5e;
    --gold:      #f0a500;
    --white:     #ffffff;
    --muted:     #7a849a;
    --border:    #d4d9e5;
    --input-bg:  #f5f6fa;
}

/* Reset Streamlit */
#MainMenu, footer, header        { visibility: hidden; }
[data-testid="stDecoration"]     { display: none !important; }
[data-testid="stToolbar"]        { display: none !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"]  { gap: 0 !important; }
[data-testid="column"]           { padding: 0 !important; }

/* App shell */
.stApp {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
    min-height: 100vh;
}

/* Particelle */
#net {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
}

/* Card */
.f360-card {
    position: relative;
    background: var(--white);
    border-radius: 18px;
    box-shadow: 0 8px 48px rgba(26,35,64,.13);
    border-top: 5px solid #1a2340;
    padding: 80px 44px 36px;
    z-index: 10;
    margin-bottom: 32px;
}

/* Input labels */
.stTextInput label {
    font-size: .78rem !important;
    font-weight: 600 !important;
    letter-spacing: .06em !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
}
.stTextInput input {
    background: var(--input-bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 11px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .95rem !important;
    color: var(--navy) !important;
    transition: border-color .18s, box-shadow .18s;
}
.stTextInput input:focus {
    border-color: var(--navy-mid) !important;
    box-shadow: 0 0 0 3px rgba(44,58,94,.12) !important;
    background: var(--white) !important;
}

/* Bottone */
.stButton > button {
    background: var(--navy) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: background .2s, transform .15s !important;
}
.stButton > button:hover {
    background: var(--navy-mid) !important;
    transform: translateY(-1px) !important;
}

/* Demo box */
.demo-box {
    background: #f8fafc;
    border: 1px dashed var(--border);
    border-radius: 10px;
    padding: 13px 16px;
    font-size: .82rem;
    color: var(--muted);
    margin-top: 18px;
    line-height: 1.75;
}
.demo-box strong { color: var(--navy); }
.demo-box code   { color: #2e7d32; background: #e8f5e9; border-radius: 4px; padding: 1px 5px; }

/* Bottone accessibilità */
.btn-accessibilita .stButton {
    display: flex !important;
    justify-content: flex-end !important;
}
.btn-accessibilita button {
    background: transparent !important;
    color: var(--muted) !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 4px 8px !important;
    font-size: .85rem !important;
    font-weight: 400 !important;
    width: auto !important;
    min-width: 0 !important;
    box-shadow: none !important;
    transition: color .2s !important;
}
.btn-accessibilita button:hover {
    background: transparent !important;
    color: var(--navy) !important;
    transform: none !important;
    text-decoration: underline !important;
}

/* Footer */
.f360-footer {
    background: rgba(26,35,64,0.97);
    padding: 16px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 9999;
}
</style>
"""
#st.image("views\logo\LOGO_FEDERICO.png",width=420)             #png da qui

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def _esegui_login(email: str, password: str) -> tuple:
    if not email or not password:
        return None, "Inserisci email e password."

    risultati = db.trova_tutti("users", {"email": email.strip().lower()})
    if not risultati:
        return None, "Credenziali non corrette."

    utente = risultati[0]

    if utente.get("stato") == "sospeso":
        return None, "Account sospeso. Contatta l'amministratore."

    if not check_password_hash(utente["password_hash"], password):
        return None, "Password errata."

    db.aggiorna(
        "users",
        {"id": utente["id"]},
        {"last_login": datetime.now(timezone.utc).isoformat()},
    )
    return utente, None


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
def mostra_login():
    st.markdown(_CSS, unsafe_allow_html=True)
    # Inietta override accessibilita (se selezionata)
    _css_acc = get_css_accessibilita()
    if _css_acc:
        st.markdown(_css_acc, unsafe_allow_html=True)

    logo_b64    = _img_to_b64(LOGO_PATH,    _LOGO_B64_EMBEDDED)
    sigillo_b64 = _img_to_b64(SIGILLO_PATH, _SIGILLO_B64_EMBEDDED)
    logo_src    = f"data:image/png;base64,{LOGO_PATH }"    if logo_b64    else ""
    sigillo_src = f"data:image/png;base64,{sigillo_b64}" if sigillo_b64 else ""

    # ── Canvas particelle (sfondo fisso) ──────────────────────────────────
    st.markdown(f"""
<canvas id="net"></canvas>
<script>
(function(){{
  const cv=document.getElementById('net');
  if(!cv)return;
  const ctx=cv.getContext('2d');
  let W,H,pts=[];
  const N=70,MAX_D=140,NAVY='rgba(26,35,64,';
  function resize(){{W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}}
  resize();window.addEventListener('resize',resize);
  for(let i=0;i<N;i++)pts.push({{
    x:Math.random()*W,y:Math.random()*H,
    vx:(Math.random()-.5)*.45,vy:(Math.random()-.5)*.45,r:Math.random()*2+1.5
  }});
  function draw(){{
    ctx.clearRect(0,0,W,H);
    pts.forEach(p=>{{
      p.x+=p.vx;p.y+=p.vy;
      if(p.x<0||p.x>W)p.vx*=-1;
      if(p.y<0||p.y>H)p.vy*=-1;
      ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=NAVY+'0.35)';ctx.fill();
    }});
    for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){{
      const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y;
      const d=Math.sqrt(dx*dx+dy*dy);
      if(d<MAX_D){{ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);
        ctx.lineTo(pts[j].x,pts[j].y);
        ctx.strokeStyle=NAVY+(1-d/MAX_D)*0.15+')';ctx.lineWidth=.7;ctx.stroke();}}
    }}
    requestAnimationFrame(draw);
  }}
  draw();
}})();
</script>
""", unsafe_allow_html=True)


    # ── Colonne: tutto centrato ───────────────────────────────────────────
    _, col, _ = st.columns([1, 1.4, 1])
    with col:


        # Sigillo animato centrato — galleggia a metà sul bordo superiore della card
        st.markdown(f"""
<div style="display:flex;justify-content:center;margin-bottom:-65px;
            position:relative;z-index:20;">
  <canvas id="sigCanvas" width="130" height="130"
          style="filter:drop-shadow(0 4px 14px rgba(26,35,64,.25));"></canvas>
</div>
<script>
(function(){{
  const img=new Image();
  const cv=document.getElementById('sigCanvas');
  if(!cv)return;
  const ctx=cv.getContext('2d');
  const W=130,H=130;
  let startT=null;
  const DUR=2400,DELAY=400;
  function easeOut(t){{return 1-Math.pow(1-t,3);}}
  function draw(ts){{
    if(!startT)startT=ts;
    const elapsed=ts-startT;
    if(elapsed<DELAY){{ctx.clearRect(0,0,W,H);ctx.drawImage(img,0,0,W,H);requestAnimationFrame(draw);return;}}
    const raw=Math.min((elapsed-DELAY)/DUR,1);
    const eased=easeOut(raw);
    const angle=eased*Math.PI*4;
    const scaleX=Math.cos(angle);
    ctx.clearRect(0,0,W,H);
    ctx.save();ctx.translate(W/2,H/2);ctx.scale(scaleX,1);
    ctx.drawImage(img,-W/2,-H/2,W,H);
    ctx.restore();
    if(raw<1)requestAnimationFrame(draw);
  }}
  img.onload=function(){{requestAnimationFrame(draw);}};
  img.src="{sigillo_src}";
}})();
</script>
""", unsafe_allow_html=True)

        # ── Card (contiene i widget Streamlit) ────────────────────────────
        col1,col2,col3 = st.columns([1,4,1])
        with col2:
            st.image("views\logo\LOGO_FEDERICO.png",width=1200)            #png da qui

        # Bottone accessibilità sotto il logo (allineato a destra)
        _acc_spacer, _acc_col = st.columns([4, 1])
        with _acc_col:
            if st.button(icon="♿", label="Accessibilità", key="btn_accessibilita", help="Impostazioni di accessibilità"):
                dialog_accessibilita()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Errore login
        if st.session_state.get("_login_errore"):
            st.markdown(
                f'<div style="background:#fff0f2;border-left:4px solid #c0392b;'
                f'border-radius:8px;padding:11px 15px;color:#7d1a2a;font-size:.88rem;'
                f'margin-bottom:14px;">⚠️ {st.session_state["_login_errore"]}</div>',
                unsafe_allow_html=True,
            )

        email = st.text_input(
            "Email istituzionale",
            placeholder="Inserisci la mail",
            key="login_email",
        )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            key="login_password",
        )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        accetta_termini = st.checkbox(
            "Accetto i [Termini e Condizioni](http://localhost:8502/pages/termini_e_condizioni.html) e la [Privacy Policy](http://localhost:8502/pages/privacy_policy.html)",
            key="accetta_termini",
        )

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        if st.button("Accedi", use_container_width=True):
            if not accetta_termini:
                st.session_state["_login_errore"] = "Devi accettare i Termini e Condizioni per accedere."
                st.rerun()
            utente, errore = _esegui_login(email, password)
            if errore:
                st.session_state["_login_errore"] = errore
                st.rerun()
            else:
                st.session_state.is_logged_in    = True
                st.session_state.current_user_id = utente["id"]
                st.session_state.user_role       = utente["ruolo"].capitalize()
                st.session_state.chat_history    = []
                st.session_state.user = {
                    "user_id":            utente["id"],
                    "nome":               utente["nome"],
                    "cognome":            utente["cognome"],
                    "email":              utente["email"],
                    "ruolo":              utente["ruolo"],
                    "matricola":          utente.get("matricola_studente") or utente.get("matricola_docente"),
                    "corso_di_laurea_id": utente.get("corso_di_laurea_id"),
                    "anno_corso":         utente.get("anno_corso"),
                    "dipartimento":       utente.get("dipartimento"),
                }
                st.session_state.pop("_login_errore", None)
                st.rerun()

        st.markdown("""
<div style="text-align:center;margin-top:14px;">
  <a href="http://localhost:8502/index.html" target="_top" style="font-size:.85rem;color:#7a849a;text-decoration:none;">← Torna indietro</a>
</div>
<div class="demo-box">
  <strong>Account demo disponibili:</strong><br>
  👩‍🎓 Studente: <code>studente@studenti.unina.it</code><br>
  👩‍🎓 Studente: <code>g.bianchi@studenti.unina.it</code><br>
  👨‍🏫 Docente: &nbsp;<code>docente@unina.it</code><br>
  🔑 Password: <code>test1234</code>
</div>
""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # chiude f360-card

    # ── Spazio prima del footer ───────────────────────────────────────────
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown("""
<div class="f360-footer">
  <div style="font-size:.77rem;color:rgba(255,255,255,.35);">
    &copy; 2026 <strong style="color:#ffffff;">Federico<span style="color:#f0a500;">360</span></strong>
    &mdash; Università degli Studi di Napoli Federico II
  </div>
  <div style="display:flex;gap:22px;flex-wrap:wrap;">
    <a href="#" style="text-decoration:none;color:rgba(255,255,255,.45);font-size:.79rem;">Aiuto</a>
    <a href="http://localhost:8502/pages/termini_e_condizioni.html" target="_blank" style="text-decoration:none;color:rgba(255,255,255,.45);font-size:.79rem;">Termini e Condizioni</a>
        <a href="http://localhost:8502/pages/privacy_policy.html" target="_blank" style="text-decoration:none;color:rgba(255,255,255,.45);font-size:.79rem;">Privacy Policy</a>
    <a href="#" style="text-decoration:none;color:rgba(255,255,255,.45);font-size:.79rem;">Accessibilità</a>
      </div>
</div>
""", unsafe_allow_html=True)