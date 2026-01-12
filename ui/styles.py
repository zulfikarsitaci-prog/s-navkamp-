import database.users as users

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

/* =====================================================
   1. GENEL SIKIŞTIRMA (HAFİF – ESTETİK KORUNUR)
===================================================== */
.main .block-container {
    padding-top: 0.8rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

div.stMarkdown {
    margin-bottom: 0px !important;
}

h3 {
    margin-top: 0px !important;
    padding-top: 0px !important;
    font-size: 1.2rem !important;
}

/* =====================================================
   2. ÜST MENÜ (OKUNURLUK AYARI – GÖRSEL AYNI)
===================================================== */

/* Radyo yuvarlaklarını gizle */
div[role="radiogroup"] label div:first-child {
    display: none !important;
}

/* Menü kapsayıcı */
div[role="radiogroup"] {
    flex-direction: row !important;
    overflow-x: auto !important;
    gap: 8px !important;               /* 10 → 8 */
    padding: 5px 0 8px 0 !important;
    border-bottom: 2px solid #FFD700;
    margin-bottom: 8px !important;
    -webkit-overflow-scrolling: touch;
}

/* Menü kapsül */
div[role="radiogroup"] label {
    background-color: #1e293b !important;
    border: 2px solid #FFD700 !important;
    border-radius: 12px !important;
    padding: 9px 18px !important;      /* 10 20 → 9 18 */
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

/* Menü yazısı */
div[role="radiogroup"] label p {
    color: #FFD700 !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;     /* 1.1 → 1.05 */
    letter-spacing: 0.3px !important;  /* 0.5 → 0.3 */
    margin: 0 !important;
}

/* Seçili menü */
div[role="radiogroup"] label[data-checked="true"] {
    background-color: #FFD700 !important;
    border-color: #ffffff !important;
    transform: scale(1.04);
}

div[role="radiogroup"] label[data-checked="true"] p {
    color: #0f172a !important;
}

/* =====================================================
   3. ANKET ŞIKLARI (MESAFE AZALTILDI – GÖRSEL AYNI)
===================================================== */

div.poll-marker + div .stButton {
    margin-top: -14px !important;   /* -22 → -14 */
    margin-bottom: -4px !important;
    padding: 0 !important;
    width: 100% !important;
}

div.poll-marker + div .stButton button {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 10px 14px !important;  /* 12 15 → 10 14 */
    background: rgba(30, 41, 59, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    color: #e2e8f0 !important;
    border-radius: 4px !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}

div.poll-marker + div .stButton button:hover {
    background: rgba(255, 215, 0, 0.2) !important;
    border-left: 4px solid #FFD700 !important;
    color: white !important;
}

/* =====================================================
   4. GÖNDERİLER ARASI MESAFE (KART BOZULMADAN)
===================================================== */

.post-card {
    background: rgba(30, 41, 59, 0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 8px !important; /* 15 → 8 */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.post-header {
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 8px;
    margin-bottom: 8px;
}

/* =====================================================
   5. DİĞER CSS (AYNEN KORUNDU)
===================================================== */

.post-content {
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.4;
    white-space: pre-wrap;
    margin-bottom: 10px;
}

.poll-bar-bg {
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
    margin-bottom: 3px;
    height: 28px;
    line-height: 28px;
    position:relative;
}

.poll-bar-fill {
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
}

.poll-text {
    position: relative;
    z-index: 2;
    padding: 0 10px;
    font-size: 0.8rem;
    color: white;
    display: flex;
    justify-content: space-between;
    font-weight: 600;
}

/* GENEL BUTON */
div.stButton > button {
    background-color: transparent !important;
    border: none !important;
    color: #94a3b8 !important;
    font-size: 1.1rem !important;
    padding: 0.2rem 0.5rem !important;
}

div.stButton > button:hover {
    color: #FFD700 !important;
    transform: scale(1.1);
}
</style>
"""