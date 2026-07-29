import json
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Airline Passenger Segmentation",
    page_icon="✈️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a1628 100%);
    min-height: 100vh;
}

/* ── Hide default streamlit elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 3rem 4rem 3rem !important;
    max-width: 1200px;
}

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #e8f4fd !important;
    letter-spacing: -0.02em;
}

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, rgba(14,165,233,0.12) 0%, rgba(99,102,241,0.08) 100%);
    border: 1px solid rgba(14,165,233,0.25);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #e8f4fd;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.03em;
}
.hero-subtitle {
    font-size: 0.9rem;
    color: #64a8d4;
    margin: 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 500;
}
.hero-pipeline {
    display: flex;
    gap: 0.75rem;
    margin-top: 1.25rem;
    flex-wrap: wrap;
}
.pipeline-badge {
    background: rgba(14,165,233,0.1);
    border: 1px solid rgba(14,165,233,0.3);
    color: #7dd3fc;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── Section Headers ── */
.section-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    color: #0ea5e9;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}
.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #e2eeff;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(14,165,233,0.15);
}

/* ── Input Card ── */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(14,165,233,0.15);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* ── Streamlit inputs ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(14,165,233,0.2) !important;
    border-radius: 8px !important;
    color: #e2eeff !important;
}
.stSelectbox > div > div:hover,
.stNumberInput > div > div > input:focus {
    border-color: rgba(14,165,233,0.5) !important;
    box-shadow: 0 0 0 2px rgba(14,165,233,0.1) !important;
}
label {
    color: #94b8d4 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}
.stSlider > div > div > div > div {
    background: #0ea5e9 !important;
}

/* ── Predict Button ── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #3b82f6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2.5rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(14,165,233,0.4) !important;
}

/* ── Result Card ── */
.result-card {
    background: linear-gradient(135deg, rgba(14,165,233,0.08), rgba(99,102,241,0.06));
    border: 1px solid rgba(14,165,233,0.3);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    text-align: center;
}
.result-cluster {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: #0ea5e9;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.result-segment {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #e8f4fd;
    letter-spacing: -0.02em;
}

/* ── Info Cards ── */
.info-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(14,165,233,0.12);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
}
.info-card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: #0ea5e9;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(14,165,233,0.15);
}
.info-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.65rem;
    color: #94b8d4;
    font-size: 0.875rem;
    line-height: 1.5;
}
.info-dot {
    width: 5px;
    height: 5px;
    background: #0ea5e9;
    border-radius: 50%;
    margin-top: 0.45rem;
    flex-shrink: 0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(8,14,28,0.95) !important;
    border-right: 1px solid rgba(14,165,233,0.12) !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {
    color: #64a8d4 !important;
    font-size: 0.85rem !important;
}
section[data-testid="stSidebar"] h3 {
    color: #0ea5e9 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ── Metric ── */
[data-testid="stMetricValue"] {
    color: #e2eeff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #64a8d4 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── Success / Error ── */
.stSuccess, .stAlert {
    background: rgba(14,165,233,0.08) !important;
    border: 1px solid rgba(14,165,233,0.25) !important;
    border-radius: 10px !important;
    color: #7dd3fc !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(14,165,233,0.12) !important;
    margin: 1.5rem 0 !important;
}

/* ── Caption ── */
.stCaption {
    color: rgba(100,168,212,0.5) !important;
    font-size: 0.75rem !important;
    text-align: center !important;
    letter-spacing: 0.05em !important;
}
</style>
""", unsafe_allow_html=True)

# ── Load Model ────────────────────────────────────────────────────────────────

BASE_DIR  = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models"

try:
    scaler  = joblib.load(MODEL_DIR / "scaler.pkl")
    pca     = joblib.load(MODEL_DIR / "pca.pkl")
    kmeans  = joblib.load(MODEL_DIR / "kmeans.pkl")

    with open(MODEL_DIR / "segment_mapping.json") as f:
        segment_mapping = json.load(f)

except Exception as e:
    st.error(f"Gagal memuat model: {e}")
    st.stop()

# ── Segment Info ──────────────────────────────────────────────────────────────

SEGMENT_INFO = {
    "Loyal Satisfied Passenger": {
        "karakteristik": [
            "Tingkat kepuasan tinggi",
            "Loyal customer",
            "Delay rendah",
            "Skor layanan tinggi",
        ],
        "rekomendasi": [
            "Pertahankan kualitas layanan",
            "Berikan loyalty rewards",
            "Personalized promotion",
            "Priority benefits",
        ],
    },
    "Severely Delayed Passenger": {
        "karakteristik": [
            "Delay sangat tinggi",
            "Kepuasan rendah",
            "Sensitif terhadap ketepatan waktu",
        ],
        "rekomendasi": [
            "Kurangi delay operasional",
            "Peningkatan jadwal penerbangan",
            "Realtime notification",
            "Kompensasi pelanggan",
        ],
    },
    "Digitally Frustrated Passenger": {
        "karakteristik": [
            "Pengalaman digital kurang baik",
            "Booking dan boarding menjadi masalah",
            "Kepuasan relatif rendah",
        ],
        "rekomendasi": [
            "Perbaiki aplikasi maskapai",
            "Perbaiki online boarding",
            "Perbaiki online booking",
            "Digital customer support",
        ],
    },
    "Delay Sensitive Passenger": {
        "karakteristik": [
            "Sensitif terhadap delay",
            "Delay mempengaruhi pengalaman",
            "Membutuhkan informasi cepat",
        ],
        "rekomendasi": [
            "Peningkatan komunikasi",
            "Informasi delay transparan",
            "Flexible reschedule",
            "Peningkatan on-time performance",
        ],
    },
}

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ✈️ Segmentasi Penumpang")
    st.markdown("""
### Pipeline
- RobustScaler
- PCA
- K-Means Clustering

### Segmen
1. Loyal Satisfied Passenger
2. Severely Delayed Passenger
3. Digitally Frustrated Passenger
4. Delay Sensitive Passenger
""")

# ── Hero Header ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <div class="hero-title">✈️ Airline Passenger Segmentation</div>
    <div class="hero-subtitle">Sistem Analisis & Segmentasi Penumpang Maskapai</div>
    <div class="hero-pipeline">
        <span class="pipeline-badge">Feature Engineering</span>
        <span class="pipeline-badge">RobustScaler</span>
        <span class="pipeline-badge">PCA</span>
        <span class="pipeline-badge">K-Means Clustering</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Passenger Information ─────────────────────────────────────────────────────

st.markdown('<div class="section-label">Langkah 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Informasi Penumpang</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    age             = st.number_input("Age",                    min_value=18,  max_value=100, value=30)
    gender          = st.selectbox("Gender",                    ["Female", "Male"])
    customer_type   = st.selectbox("Customer Type",             ["Disloyal Customer", "Loyal Customer"])
    travel_type     = st.selectbox("Type of Travel",            ["Business Travel", "Personal Travel"])
    travel_class    = st.selectbox("Class",                     ["Eco", "Eco Plus", "Business"])

with col2:
    flight_distance = st.number_input("Flight Distance (km)",           min_value=0, value=1000)
    departure_delay = st.number_input("Departure Delay (Minutes)",      min_value=0, value=0)
    arrival_delay   = st.number_input("Arrival Delay (Minutes)",        min_value=0, value=0)
    satisfaction    = st.selectbox("Passenger Satisfaction",            ["Neutral/Dissatisfied", "Satisfied"])

# ── Service Ratings ───────────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-label">Langkah 2</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Penilaian Layanan</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    food    = st.slider("🍽️  Food and Drink",       1, 5, 3)
    onboard = st.slider("🛎️  On-board Service",     1, 5, 3)
    legroom = st.slider("💺  Leg Room Service",     1, 5, 3)

with col4:
    checkin             = st.slider("🏷️  Check-in Service",        1, 5, 3)
    online_boarding     = st.slider("📱  Online Boarding",         1, 5, 3)
    ease_online_booking = st.slider("💻  Ease of Online Booking",  1, 5, 3)

# ── Prediction ────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="section-label">Langkah 3</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Prediksi Segmen</div>', unsafe_allow_html=True)

if st.button("🔍  Analisis & Prediksi Segmen"):
    try:
        # Feature engineering
        avg_digital_score = (online_boarding + ease_online_booking) / 2
        total_delay       = departure_delay + arrival_delay

        class_map = {"Eco": 0, "Eco Plus": 1, "Business": 2}

        delay_low    = 1 if 0   < total_delay <= 60  else 0
        delay_medium = 1 if 60  < total_delay <= 180 else 0
        # total_delay > 180 → delay_low=0, delay_medium=0 (kategori "High")

        X = pd.DataFrame([{
            "flight distance":                     flight_distance,
            "food and drink":                      food,
            "on-board service":                    onboard,
            "leg room service":                    legroom,
            "checkin service":                     checkin,
            "arrival delay in minutes":            arrival_delay,
            "avg digital score":                   avg_digital_score,
            "class":                               class_map[travel_class],
            "gender_Male":                         1 if gender == "Male" else 0,
            "customer type_Loyal Customer":        1 if customer_type == "Loyal Customer" else 0,
            "type of travel_Personal Travel":      1 if travel_type == "Personal Travel" else 0,
            "satisfaction_Satisfied":              1 if satisfaction == "Satisfied" else 0,
            "travel distance category_Medium":     1 if 1000 <= flight_distance <= 2500 else 0,
            "age group_Old":                       1 if age > 45 else 0,
            "age group_Young":                     1 if age < 25 else 0,
            "delay category_Low":                  delay_low,
            "delay category_Medium":               delay_medium,
        }])

        if hasattr(scaler, "feature_names_in_"):
            X = X.reindex(columns=scaler.feature_names_in_)

        X_scaled = pd.DataFrame(scaler.transform(X), columns=X.columns)
        X_pca    = pca.transform(X_scaled)
        cluster  = int(kmeans.predict(X_pca)[0])
        segment  = segment_mapping[str(cluster)]

        # ── Result Card ──
        st.markdown(f"""
        <div class="result-card">
            <div class="result-cluster">Cluster {cluster} · Hasil Prediksi</div>
            <div class="result-segment">{segment}</div>
        </div>
        """, unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        m1.metric("Cluster", cluster)
        m2.metric("Segment", segment)

        # ── Radar Chart ──
        fig = go.Figure(go.Scatterpolar(
            r=[food, onboard, checkin, online_boarding, ease_online_booking, legroom],
            theta=["Food", "On-board", "Check-in", "Online Boarding", "Ease Booking", "Leg Room"],
            fill="toself",
            line=dict(color="#0ea5e9", width=2),
            fillcolor="rgba(14,165,233,0.12)",
        ))
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(255,255,255,0.02)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    gridcolor="rgba(14,165,233,0.15)",
                    tickfont=dict(color="#64a8d4", size=10),
                    linecolor="rgba(14,165,233,0.15)",
                ),
                angularaxis=dict(
                    gridcolor="rgba(14,165,233,0.1)",
                    linecolor="rgba(14,165,233,0.2)",
                    tickfont=dict(color="#94b8d4", size=11),
                ),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Segment Detail ──
        info = SEGMENT_INFO[segment]
        c5, c6 = st.columns(2)

        with c5:
            karakteristik_items = "".join(
                f'<div class="info-item"><div class="info-dot"></div><span>{item}</span></div>'
                for item in info["karakteristik"]
            )
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">📌 Karakteristik</div>
                {karakteristik_items}
            </div>
            """, unsafe_allow_html=True)

        with c6:
            rekomendasi_items = "".join(
                f'<div class="info-item"><div class="info-dot"></div><span>{item}</span></div>'
                for item in info["rekomendasi"]
            )
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">💡 Rekomendasi</div>
                {rekomendasi_items}
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Prediction Error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption("Final Project — Airline Passenger Segmentation  ·  K-Means + PCA")