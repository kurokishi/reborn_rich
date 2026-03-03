import streamlit as st
import anthropic
import json
import re
import time
from typing import Optional

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Reborn Rich | Analisis Saham AI",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Courier+Prime:wght@400;700&display=swap');

/* ─ Global ─ */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0705 !important;
    color: #c8a96e;
}
[data-testid="stAppViewContainer"] { background-color: #0a0705 !important; }
[data-testid="stHeader"] { background-color: #0a0705 !important; }
[data-testid="stSidebar"] { background-color: #0d0b07 !important; }
.block-container { max-width: 860px !important; padding-top: 2rem !important; }

/* ─ Typography ─ */
h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif !important; }
p, div, span, label { font-family: 'Courier Prime', monospace !important; }

/* ─ Header ─ */
.rr-header {
    text-align: center;
    padding: 2rem 0 1rem;
    border-bottom: 1px solid #2a2010;
    margin-bottom: 2rem;
}
.rr-eyebrow {
    font-family: 'Courier Prime', monospace !important;
    font-size: 0.65rem;
    letter-spacing: 0.4em;
    color: #5c4a2a;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.rr-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: clamp(2rem, 6vw, 3.5rem);
    color: #d4af37;
    margin: 0;
    text-shadow: 0 0 30px #d4af3755;
    letter-spacing: 0.08em;
}
.rr-subtitle {
    font-size: 0.8rem;
    color: #5c4a2a;
    letter-spacing: 0.2em;
    font-style: italic;
    margin-top: 0.4rem;
}

/* ─ Input ─ */
.stTextArea textarea {
    background-color: #0d0b07 !important;
    color: #e8d5a0 !important;
    border: 1px solid #2a2010 !important;
    border-radius: 4px !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1rem !important;
    caret-color: #d4af37 !important;
}
.stTextArea textarea:focus {
    border-color: #d4af3766 !important;
    box-shadow: 0 0 12px #d4af3720 !important;
}

/* ─ Button ─ */
.stButton > button {
    background: linear-gradient(135deg, #d4af37, #a07d20) !important;
    color: #0a0705 !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Courier Prime', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 0.2em !important;
    font-size: 0.8rem !important;
    padding: 0.6rem 2rem !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 20px #d4af3733 !important;
    transition: all 0.3s !important;
    width: 100% !important;
}
.stButton > button:hover {
    box-shadow: 0 0 30px #d4af3766 !important;
    transform: translateY(-1px) !important;
}

/* ─ Cards ─ */
.rr-card {
    background: #0d0b07;
    border: 1px solid #1e1810;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.rr-card:hover {
    border-color: #d4af3744;
    box-shadow: 0 0 16px #d4af3715;
}
.rr-card-label {
    font-family: 'Courier Prime', monospace !important;
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    color: #5c4a2a;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.rr-card-body {
    font-family: 'Playfair Display', serif !important;
    color: #c8a96e;
    font-size: 0.95rem;
    line-height: 1.75;
}

/* ─ Decision Banner ─ */
.rr-decision-beli {
    border-color: #4ade8044 !important;
    box-shadow: 0 0 40px #4ade8022 !important;
    background: radial-gradient(ellipse at 50% 0%, #4ade8010, #0d0b07 70%) !important;
}
.rr-decision-jual {
    border-color: #f8717144 !important;
    box-shadow: 0 0 40px #f8717122 !important;
    background: radial-gradient(ellipse at 50% 0%, #f8717110, #0d0b07 70%) !important;
}
.rr-decision-tahan {
    border-color: #fbbf2444 !important;
    box-shadow: 0 0 40px #fbbf2422 !important;
    background: radial-gradient(ellipse at 50% 0%, #fbbf2410, #0d0b07 70%) !important;
}
.decision-word-beli  { color: #4ade80; }
.decision-word-jual  { color: #f87171; }
.decision-word-tahan { color: #fbbf24; }

/* ─ Score bar ─ */
.score-container { margin-bottom: 0.75rem; }
.score-label-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
}
.score-label {
    font-family: 'Courier Prime', monospace !important;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #8b7355;
    text-transform: uppercase;
}
.score-value { font-weight: 700; font-family: 'Courier Prime', monospace !important; }
.score-track {
    height: 4px;
    background: #1a1410;
    border-radius: 2px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 2px;
}

/* ─ Quote ─ */
.rr-quote {
    border-left: 2px solid #d4af37;
    padding: 1.2rem 1.2rem 1.2rem 1.5rem;
    background: #0d0b0788;
    border-radius: 0 4px 4px 0;
    margin: 1rem 0;
}
.rr-quote-text {
    color: #d4af37;
    font-family: 'Playfair Display', serif !important;
    font-style: italic;
    font-size: 1rem;
    line-height: 1.8;
}

/* ─ Conviction bar ─ */
.conviction-bar {
    font-family: 'Courier Prime', monospace !important;
    color: #8b7355;
    letter-spacing: 0.15em;
    font-size: 0.8rem;
}

/* ─ Disclaimer ─ */
.rr-disclaimer {
    text-align: center;
    font-size: 0.6rem;
    color: #3d2e15;
    letter-spacing: 0.05em;
    line-height: 1.7;
    padding: 1rem 0;
    font-family: 'Courier Prime', monospace !important;
}

/* ─ Divider ─ */
hr { border-color: #2a2010 !important; }

/* ─ Hide Streamlit branding ─ */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ─ Selectbox & API input ─ */
.stTextInput input {
    background-color: #0d0b07 !important;
    color: #c8a96e !important;
    border: 1px solid #2a2010 !important;
    border-radius: 4px !important;
    font-family: 'Courier Prime', monospace !important;
}
.stTextInput input:focus {
    border-color: #d4af3766 !important;
}
[data-testid="stExpander"] {
    background: #0d0b07 !important;
    border: 1px solid #1e1810 !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Kamu adalah analis saham dengan pola pikir seperti karakter utama drama "Reborn Rich" — seseorang yang memiliki visi jauh ke depan, membaca siklus pasar secara mendalam, dan membuat keputusan investasi yang tegas dan berani.

Gaya analisismu:
1. Visi Makro: Baca kondisi ekonomi global & lokal saat ini — siklus suku bunga, inflasi, geopolitik
2. Oportunis Tajam: Temukan peluang yang BELUM dilihat investor awam — aset undervalued, katalis tersembunyi
3. Manajemen Risiko: Tetap waspada, tahu kapan harus mundur — modal yang dilindungi adalah modal yang bisa bertarung lagi
4. Keputusan Tegas: Jangan ragu-ragu — berikan rekomendasi BELI / TAHAN / JUAL dengan keyakinan dan alasan kuat
5. Timing: Kapan masuk, kapan keluar — momentum dan katalis jangka pendek vs fundamental jangka panjang

Gunakan web search untuk mendapatkan data terkini sebelum memberikan analisis.

Format responsmu HARUS dalam JSON berikut (tanpa markdown backticks, langsung JSON murni):
{
  "keputusan": "BELI" atau "TAHAN" atau "JUAL",
  "conviction": angka 1 sampai 10,
  "ringkasan": "1-2 kalimat executive summary dari perspektif seorang visioner",
  "kondisi_makro": "Analisis kondisi ekonomi makro yang relevan saat ini",
  "peluang_tersembunyi": "Peluang yang belum banyak disadari pasar — katalis asimetris",
  "risiko_utama": "Risiko terbesar yang perlu diwaspadai",
  "strategi_masuk": "Kapan dan bagaimana cara masuk posisi secara ideal",
  "target_harga": "Estimasi target harga atau range dalam 6-12 bulan",
  "filosofi": "Kutipan atau prinsip investasi bergaya Reborn Rich yang relevan dengan situasi ini",
  "skor": {
    "fundamental": angka 1 sampai 10,
    "momentum": angka 1 sampai 10,
    "valuasi": angka 1 sampai 10,
    "katalis": angka 1 sampai 10
  }
}"""

# ── Helper Functions ──────────────────────────────────────────────────────────

def get_api_key() -> Optional[str]:
    """Get API key from Streamlit secrets or session state."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return st.session_state.get("api_key", "")


def score_color(val: int) -> str:
    if val >= 7: return "#d4af37"
    if val >= 5: return "#c8a96e"
    return "#8b7355"


def render_score_bar(label: str, value: int):
    color = score_color(value)
    pct = value * 10
    st.markdown(f"""
    <div class="score-container">
        <div class="score-label-row">
            <span class="score-label">{label}</span>
            <span class="score-value" style="color:{color};">{value}/10</span>
        </div>
        <div class="score-track">
            <div class="score-fill" style="width:{pct}%;background:linear-gradient(90deg,{color}88,{color});box-shadow:0 0 8px {color}66;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def analyze_stock(query: str, api_key: str) -> dict:
    """
    Call Anthropic API with web search tool and handle multi-turn tool use.
    Returns parsed JSON result dict.
    """
    client = anthropic.Anthropic(api_key=api_key)

    user_message = (
        f'Analisis saham / instrumen investasi berikut dengan pola pikir Reborn Rich: "{query}". '
        f'Gunakan web search untuk mendapatkan data terkini: harga saham hari ini, berita terbaru, '
        f'laporan keuangan, kondisi industri, dan sentimen pasar. Berikan analisis komprehensif dalam format JSON.'
    )

    messages = [{"role": "user", "content": user_message}]
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    # Agentic loop — maksimal 5 iterasi untuk handle multi tool-use
    for _ in range(5):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        # Append assistant response ke history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Cari text block
            for block in response.content:
                if block.type == "text" and block.text.strip():
                    raw = block.text.strip()
                    raw = re.sub(r'^```json\s*', '', raw, flags=re.IGNORECASE)
                    raw = re.sub(r'^```\s*', '', raw, flags=re.IGNORECASE)
                    raw = re.sub(r'```\s*$', '', raw)
                    m = re.search(r'\{[\s\S]*\}', raw)
                    if m:
                        return json.loads(m.group(0))
            raise ValueError("Tidak ditemukan JSON dalam respons AI.")

        elif response.stop_reason == "tool_use":
            # Kumpulkan semua tool_result dan lanjutkan
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # Untuk web_search, hasilnya sudah di-handle API — kirim placeholder
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "Search results retrieved successfully.",
                    })
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            raise ValueError(f"Stop reason tidak dikenal: {response.stop_reason}")

    raise ValueError("Melebihi batas iterasi tool use.")


# ── UI ────────────────────────────────────────────────────────────────────────

def render_header():
    st.markdown("""
    <div class="rr-header">
        <div class="rr-eyebrow">◆ SISTEM ANALISIS INVESTASI KELAS CHAEBOL ◆</div>
        <h1 class="rr-title">REBORN RICH</h1>
        <div class="rr-subtitle">"Lihat apa yang belum dilihat orang lain"</div>
    </div>
    """, unsafe_allow_html=True)


def render_api_settings():
    """Tampilkan input API key jika belum ada di secrets."""
    try:
        st.secrets["ANTHROPIC_API_KEY"]
        return  # Sudah ada di secrets, tidak perlu input
    except Exception:
        pass

    with st.expander("⚙ Pengaturan API Key"):
        st.markdown('<p style="color:#8b7355;font-size:0.75rem;">Masukkan Anthropic API Key kamu. Key tidak disimpan secara permanen.</p>', unsafe_allow_html=True)
        key_input = st.text_input(
            "Anthropic API Key",
            value=st.session_state.get("api_key", ""),
            type="password",
            placeholder="sk-ant-...",
            label_visibility="collapsed"
        )
        if key_input:
            st.session_state["api_key"] = key_input
            st.success("✓ API Key tersimpan untuk sesi ini")


def render_result(result: dict):
    keputusan = result.get("keputusan", "TAHAN").upper()
    conviction = result.get("conviction", 5)
    css_class = f"rr-decision-{keputusan.lower()}"
    word_class = f"decision-word-{keputusan.lower()}"

    filled = "▮" * conviction
    empty  = "▯" * (10 - conviction)

    # ── Decision Banner ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="rr-card {css_class}" style="text-align:center;padding:2rem 1.5rem;">
        <div class="rr-card-label">KEPUTUSAN FINAL</div>
        <div class="{word_class}" style="font-family:'Playfair Display',serif;font-size:clamp(2.5rem,8vw,4rem);font-weight:700;letter-spacing:0.1em;">
            {keputusan}
        </div>
        <div class="conviction-bar" style="margin:0.5rem 0 1rem;">
            CONVICTION {conviction}/10 — {filled}{empty}
        </div>
        <div class="rr-card-body" style="font-style:italic;max-width:580px;margin:0 auto;">
            {result.get("ringkasan", "")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2-column cards ───────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="rr-card">
            <div class="rr-card-label" style="color:#6ba3d6;">🌐 KONDISI MAKRO</div>
            <div class="rr-card-body">{result.get("kondisi_makro","")}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="rr-card">
            <div class="rr-card-label" style="color:#f87171;">⚠ RISIKO UTAMA</div>
            <div class="rr-card-body">{result.get("risiko_utama","")}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="rr-card">
            <div class="rr-card-label" style="color:#d4af37;">👁 PELUANG TERSEMBUNYI</div>
            <div class="rr-card-body">{result.get("peluang_tersembunyi","")}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="rr-card">
            <div class="rr-card-label" style="color:#4ade80;">📈 TARGET HARGA</div>
            <div class="rr-card-body">{result.get("target_harga","")}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Strategi Masuk ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="rr-card">
        <div class="rr-card-label">🎯 STRATEGI MASUK</div>
        <div class="rr-card-body">{result.get("strategi_masuk","")}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score Matrix ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="rr-card">
        <div class="rr-card-label">📊 MATRIX PENILAIAN</div>
    """, unsafe_allow_html=True)
    skor = result.get("skor", {})
    render_score_bar("Fundamental", skor.get("fundamental", 5))
    render_score_bar("Momentum Pasar", skor.get("momentum", 5))
    render_score_bar("Valuasi", skor.get("valuasi", 5))
    render_score_bar("Kekuatan Katalis", skor.get("katalis", 5))
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Filosofi Quote ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="rr-quote">
        <div class="rr-card-label">💬 FILOSOFI INVESTASI</div>
        <div class="rr-quote-text">"{result.get("filosofi","")}"</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Disclaimer ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="rr-disclaimer">
        ⚠ Analisis ini bersifat edukatif dan tidak merupakan saran investasi resmi.<br>
        Selalu lakukan riset mandiri dan konsultasikan dengan advisor keuangan profesional.
    </div>
    """, unsafe_allow_html=True)


def render_empty_state():
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#3d2e15;
                font-style:italic;line-height:2.2;font-family:'Playfair Display',serif;font-size:1rem;">
        "Yang membedakan investor biasa dengan yang luar biasa<br>
        bukan seberapa banyak yang mereka tahu —<br>
        tapi seberapa cepat mereka melihat apa yang belum terlihat."
    </div>
    """, unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────

def main():
    render_header()
    render_api_settings()

    # Input area
    st.markdown('<div class="rr-card-label" style="padding:0 0 0.4rem;">TARGET ANALISIS</div>', unsafe_allow_html=True)
    query = st.text_area(
        label="target",
        label_visibility="collapsed",
        placeholder="Contoh: BBCA, Tesla TSLA, Bitcoin, Emas, BREN, saham sektor perbankan Indonesia...",
        height=90,
        key="query_input"
    )

    analyze_btn = st.button("▶  ANALISIS SEKARANG", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if analyze_btn:
        api_key = get_api_key()
        if not api_key:
            st.error("⚠ API Key belum diatur. Buka pengaturan di atas dan masukkan Anthropic API Key kamu.")
            return
        if not query.strip():
            st.warning("Masukkan nama saham atau instrumen investasi terlebih dahulu.")
            return

        phases = [
            "🔍 Memindai pasar global...",
            "📡 Membaca pola tersembunyi...",
            "🧮 Menghitung probabilitas...",
            "⚡ Menyusun keputusan final..."
        ]
        status_placeholder = st.empty()
        for i, phase_text in enumerate(phases):
            status_placeholder.info(phase_text)
            if i < len(phases) - 1:
                time.sleep(0.1)

        try:
            result = analyze_stock(query.strip(), api_key)
            status_placeholder.empty()
            render_result(result)

            # Simpan ke history session
            if "history" not in st.session_state:
                st.session_state["history"] = []
            st.session_state["history"].insert(0, {
                "query": query.strip(),
                "keputusan": result.get("keputusan"),
                "conviction": result.get("conviction"),
                "ringkasan": result.get("ringkasan", "")[:100] + "..."
            })

        except anthropic.AuthenticationError:
            status_placeholder.empty()
            st.error("⚠ API Key tidak valid. Periksa kembali API Key kamu.")
        except json.JSONDecodeError as e:
            status_placeholder.empty()
            st.error(f"⚠ Gagal mem-parse respons AI: {e}")
        except Exception as e:
            status_placeholder.empty()
            st.error(f"⚠ Error: {e}")
    else:
        # History sidebar
        if st.session_state.get("history"):
            with st.sidebar:
                st.markdown('<div class="rr-card-label" style="color:#5c4a2a;">RIWAYAT ANALISIS</div>', unsafe_allow_html=True)
                for item in st.session_state["history"][:10]:
                    keputusan = item["keputusan"]
                    color = "#4ade80" if keputusan == "BELI" else "#f87171" if keputusan == "JUAL" else "#fbbf24"
                    st.markdown(f"""
                    <div class="rr-card" style="margin-bottom:0.5rem;padding:0.75rem 1rem;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <strong style="color:#c8a96e;font-size:0.85rem;">{item['query']}</strong>
                            <span style="color:{color};font-weight:700;font-size:0.75rem;">{keputusan}</span>
                        </div>
                        <div style="color:#5c4a2a;font-size:0.65rem;">Conviction: {item['conviction']}/10</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            render_empty_state()


if __name__ == "__main__":
    main()
