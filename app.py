
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="FlightAI — Price Predictor",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CITY-PAIR DISTANCES
# =============================================================================
CITY_DISTANCES = {
    ("Bangalore","Chennai"):290,  ("Chennai","Bangalore"):290,
    ("Bangalore","Delhi"):1740,   ("Delhi","Bangalore"):1740,
    ("Bangalore","Hyderabad"):500,("Hyderabad","Bangalore"):500,
    ("Bangalore","Kolkata"):1560, ("Kolkata","Bangalore"):1560,
    ("Bangalore","Mumbai"):845,   ("Mumbai","Bangalore"):845,
    ("Chennai","Delhi"):1760,     ("Delhi","Chennai"):1760,
    ("Chennai","Hyderabad"):520,  ("Hyderabad","Chennai"):520,
    ("Chennai","Kolkata"):1360,   ("Kolkata","Chennai"):1360,
    ("Chennai","Mumbai"):1035,    ("Mumbai","Chennai"):1035,
    ("Delhi","Hyderabad"):1250,   ("Hyderabad","Delhi"):1250,
    ("Delhi","Kolkata"):1305,     ("Kolkata","Delhi"):1305,
    ("Delhi","Mumbai"):1150,      ("Mumbai","Delhi"):1150,
    ("Hyderabad","Kolkata"):1185, ("Kolkata","Hyderabad"):1185,
    ("Hyderabad","Mumbai"):620,   ("Mumbai","Hyderabad"):620,
    ("Kolkata","Mumbai"):1660,    ("Mumbai","Kolkata"):1660,
}
AIRLINES = ["AirAsia","Air_India","GO_FIRST","Indigo","SpiceJet","Vistara"]
CITIES   = ["Bangalore","Chennai","Delhi","Hyderabad","Kolkata","Mumbai"]
TIMES    = ["Early_Morning","Morning","Afternoon","Evening","Night","Late_Night"]
STOPS    = {"✈  Non-Stop":"zero","✈✈  1 Stop":"one","✈✈✈  2+ Stops":"two_or_more"}
CLASSES  = ["Economy","Business"]
HOLIDAY  = ["No","Yes"]
RATINGS  = {"Vistara":4.7,"Air_India":4.6,"Indigo":4.5,
             "SpiceJet":4.2,"AirAsia":4.1,"GO_FIRST":4.0}

# =============================================================================
# CSS
# =============================================================================
def css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:#0A0A0A!important;color:#E5E5E5!important;}
.block-container{padding:0 2.5rem 5rem!important;max-width:1200px!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{visibility:hidden!important;height:0!important;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:#0A0A0A;}
::-webkit-scrollbar-thumb{background:#222;border-radius:2px;}
::-webkit-scrollbar-thumb:hover{background:#FACC15;}
[data-testid="stSidebar"]{background:#0F0F0F!important;border-right:1px solid #1C1C1C!important;}
[data-testid="stSidebar"] *{color:#A0A0A0!important;}
[data-testid="stSidebar"] hr{border-color:#1C1C1C!important;margin:14px 0!important;}
[data-testid="stSidebar"] a{color:#FACC15!important;text-decoration:none!important;}
[data-testid="stSidebar"] a:hover{color:#FDE68A!important;}
[data-testid="stSidebarNav"]{display:none!important;}
[data-testid="stSelectbox"] label{font-size:0.7rem!important;font-weight:700!important;letter-spacing:0.1em!important;text-transform:uppercase!important;color:#555!important;}
[data-testid="stSelectbox"]>div>div{background:#111!important;border:1px solid #222!important;border-radius:10px!important;color:#FFF!important;transition:all 0.2s!important;}
[data-testid="stSelectbox"]>div>div:hover{border-color:#FACC15!important;box-shadow:0 0 0 2px rgba(250,204,21,.10)!important;}
[data-testid="stSelectbox"] svg{fill:#FACC15!important;}
[data-testid="stNumberInput"] label{font-size:0.7rem!important;font-weight:700!important;letter-spacing:0.1em!important;text-transform:uppercase!important;color:#555!important;}
[data-testid="stNumberInput"] input{background:#111!important;border:1px solid #222!important;border-radius:10px!important;color:#FFF!important;font-family:'JetBrains Mono',monospace!important;transition:all 0.2s!important;}
[data-testid="stNumberInput"] input:focus{border-color:#FACC15!important;box-shadow:0 0 0 2px rgba(250,204,21,.12)!important;outline:none!important;}
[data-testid="stNumberInput"] button{background:#1A1A1A!important;border-color:#222!important;color:#FACC15!important;}
div[data-testid="stButton"]>button{width:100%!important;background:linear-gradient(135deg,#FACC15 0%,#EAB308 100%)!important;color:#0A0A0A!important;border:none!important;border-radius:12px!important;padding:0.9rem 2rem!important;font-size:1rem!important;font-weight:800!important;letter-spacing:0.4px!important;font-family:'Inter',sans-serif!important;box-shadow:0 4px 24px rgba(250,204,21,.30)!important;transition:all 0.2s ease!important;}
div[data-testid="stButton"]>button:hover{background:linear-gradient(135deg,#FDE047 0%,#FACC15 100%)!important;box-shadow:0 8px 32px rgba(250,204,21,.50)!important;transform:translateY(-2px)!important;}
div[data-testid="stButton"]>button:active{transform:translateY(0)!important;}
div[data-testid="stAlert"]{border-radius:10px!important;background:#111!important;}
[data-testid="stExpander"]{background:#111!important;border:1px solid #1C1C1C!important;border-radius:12px!important;}
[data-testid="stExpander"] summary{color:#888!important;font-size:0.82rem!important;font-weight:600!important;}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}
.fade{animation:fadeUp 0.35s ease forwards;}
</style>
    """, unsafe_allow_html=True)

# =============================================================================
# LOAD MODELS
# =============================================================================
@st.cache_resource(show_spinner=False)
def load_models():
    base    = os.path.join(os.path.dirname(__file__), "models")
    lr      = joblib.load(os.path.join(base, "linear_regression_model.pkl"))
    scaler  = joblib.load(os.path.join(base, "standard_scaler.pkl"))
    columns = joblib.load(os.path.join(base, "feature_columns.pkl"))
    return lr, scaler, columns

# =============================================================================
# AUTO-DERIVE
# =============================================================================
def auto_derive(source, dest, stops, airline, cls, holiday):
    base  = CITY_DISTANCES.get((source, dest), 1200)
    mult  = {"zero":1.0,"one":1.10,"two_or_more":1.20}
    lay   = {"zero":0.0,"one":3.0,"two_or_more":6.0}
    seats = {"zero":45,"one":65,"two_or_more":90}
    dist  = round(base * mult[stops])
    dur   = round(max(0.5,(base/750)*mult[stops]+lay[stops]),2)
    return dist, dur, RATINGS.get(airline,4.3), seats[stops], 15, "Evening"

# =============================================================================
# FEATURE ENGINEERING
# =============================================================================
def engineer(airline, cls, stops, seats, days, dist, dur, rating, holiday):
    sm   = {"zero":"Direct","one":"OneStop","two_or_more":"MultiStop"}
    jt   = cls + "_" + sm[stops]
    dl   = ("High" if seats<=30 and days<=7 else
            "Medium" if seats<=70 and days<=30 else "Low")
    bc   = ("Last Minute" if days<=7 else "Early" if days<=30 else "Advance")
    prem = int(rating >= 4.5)
    spd  = round(dist/dur, 2) if dur>0 else 0.0
    hol  = 1 if holiday=="Yes" else 0
    return jt, dl, bc, prem, spd, hol

# =============================================================================
# PREPROCESSING
# =============================================================================
def preprocess(airline, src, dst, dep, arr, stops, cls, hol,
               dur, days, dist, seats, rating,
               jt, dl, bc, prem, spd, feature_columns):
    row = {
        "duration":dur, "days_left":days, "flight_distance_km":dist,
        "seat_availability":int(seats), "holiday_season":hol,
        "airline_rating":rating, "premium_airline":prem, "speed_kmh":spd,
        "airline":airline, "source_city":src, "departure_time":dep,
        "stops":stops, "arrival_time":arr, "destination_city":dst,
        "class":cls, "journey_type":jt, "demand_level":dl, "booking_category":bc,
    }
    df = pd.DataFrame([row])
    df = pd.get_dummies(df,
        columns=["airline","source_city","departure_time","stops","arrival_time",
                 "destination_city","class","journey_type","demand_level","booking_category"],
        drop_first=True, dtype=int)
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    return df[feature_columns]

# =============================================================================
# SIDEBAR
# =============================================================================
def sidebar():
    with st.sidebar:
        st.markdown("""
<div style="padding:1.2rem 0 0.6rem;display:flex;align-items:center;gap:12px;">
    <div style="width:44px;height:44px;border-radius:10px;flex-shrink:0;
                background:linear-gradient(135deg,#FACC15,#EAB308);
                display:flex;align-items:center;justify-content:center;
                font-size:1.3rem;font-weight:900;color:#0A0A0A;">✈</div>
    <div>
        <div style="font-size:1rem;font-weight:900;color:#FFF;">FlightAI</div>
        <div style="font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;color:#333;">Price Intelligence</div>
    </div>
</div>""", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#FACC15;margin-bottom:8px;">About</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.79rem;color:#555;line-height:1.75;">Predicts Indian domestic flight fares using <strong style="color:#FACC15;">Linear Regression</strong> trained on 300,000+ real booking records. Only 7 inputs needed.</div>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#FACC15;margin-bottom:10px;">Model Performance</div>', unsafe_allow_html=True)
        for label, value in [("Algorithm","Linear Regression"),("Training Rows","240,174 flights"),("R² Score","0.937"),("MAE","₹ 3,708"),("Features","45 columns")]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #161616;"><span style="font-size:0.76rem;color:#444;">{label}</span><span style="font-size:0.76rem;font-weight:700;color:#FACC15;">{value}</span></div>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#FACC15;margin-bottom:8px;">Auto-Computed</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.77rem;color:#444;line-height:1.85;"><span style="color:#FACC15;">→</span> Flight distance<br><span style="color:#FACC15;">→</span> Flight duration<br><span style="color:#FACC15;">→</span> Airline rating<br><span style="color:#FACC15;">→</span> Seat availability<br><span style="color:#FACC15;">→</span> Booking window<br><span style="color:#FACC15;">→</span> Arrival time</div>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#FACC15;margin-bottom:8px;">Tech Stack</div>', unsafe_allow_html=True)
        for icon, tech in [("🐍","Python 3.11"),("🐼","Pandas · NumPy"),("🤖","Scikit-learn"),("💾","Joblib"),("📊","Plotly"),("🌐","Streamlit")]:
            st.markdown(f'<div style="font-size:0.77rem;padding:4px 0;color:#333;">{icon} &nbsp; {tech}</div>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("""
<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#FACC15;margin-bottom:10px;">Author</div>
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
    <div style="width:40px;height:40px;border-radius:50%;flex-shrink:0;
                background:linear-gradient(135deg,#FACC15,#EAB308);
                display:flex;align-items:center;justify-content:center;
                font-size:0.95rem;font-weight:900;color:#0A0A0A;">M</div>
    <div>
        <div style="font-size:0.86rem;font-weight:700;color:#E5E5E5;">Mohammed Nihal</div>
        <div style="font-size:0.7rem;color:#333;">Data Analyst Intern</div>
    </div>
</div>
<div style="display:flex;gap:8px;">
    <a href="https://github.com" target="_blank"
       style="flex:1;text-align:center;background:#111;border:1px solid #1C1C1C;
              border-radius:8px;padding:8px 4px;font-size:0.75rem;font-weight:700;
              color:#888!important;display:block;">🐙 GitHub</a>
    <a href="https://linkedin.com" target="_blank"
       style="flex:1;text-align:center;background:#111;border:1px solid #1C1C1C;
              border-radius:8px;padding:8px 4px;font-size:0.75rem;font-weight:700;
              color:#888!important;display:block;">💼 LinkedIn</a>
</div>""", unsafe_allow_html=True)

# =============================================================================
# HERO
# =============================================================================
def hero():
    st.markdown("""
<div class="fade" style="background:linear-gradient(135deg,#0F0F0F 0%,#1A1500 60%,#0F0F0F 100%);border:1px solid #1C1C1C;border-radius:20px;padding:3rem 3.5rem;margin:1.5rem 0 1.8rem;position:relative;overflow:hidden;">
    <div style="position:absolute;top:-80px;right:-80px;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(250,204,21,0.09),transparent 70%);pointer-events:none;"></div>
    <div style="position:absolute;bottom:-100px;left:10%;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(234,179,8,0.06),transparent 70%);pointer-events:none;"></div>
    <div style="position:absolute;right:3rem;top:50%;transform:translateY(-50%);font-size:9rem;opacity:0.04;pointer-events:none;line-height:1;">✈</div>
    <div style="display:flex;align-items:center;gap:8px;font-size:0.68rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#FACC15;margin-bottom:0.9rem;">
        <span style="display:inline-block;width:20px;height:2px;background:#FACC15;border-radius:1px;"></span>
        AI-Powered Fare Intelligence
    </div>
    <div style="font-size:2.6rem;font-weight:900;letter-spacing:-1px;line-height:1.15;color:#FFF;margin-bottom:0.6rem;">
        Flight Price <span style="background:linear-gradient(135deg,#FACC15,#FDE047);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Prediction</span>
    </div>
    <div style="font-size:0.9rem;color:#555;line-height:1.75;max-width:500px;margin-bottom:1.4rem;">
        Machine learning model trained on 300,000+ Indian domestic flights. Select your route and get a precise fare estimate instantly — no technical inputs required.
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <span style="font-size:0.7rem;font-weight:700;padding:4px 13px;border-radius:20px;color:#FACC15;border:1px solid rgba(250,204,21,0.25);background:rgba(250,204,21,0.07);">R² 0.937</span>
        <span style="font-size:0.7rem;font-weight:700;padding:4px 13px;border-radius:20px;color:#22C55E;border:1px solid rgba(34,197,94,0.25);background:rgba(34,197,94,0.07);">MAE ± ₹3,708</span>
        <span style="font-size:0.7rem;font-weight:700;padding:4px 13px;border-radius:20px;color:#888;border:1px solid #222;background:#111;">6 Indian Metros</span>
        <span style="font-size:0.7rem;font-weight:700;padding:4px 13px;border-radius:20px;color:#888;border:1px solid #222;background:#111;">7 Inputs Only</span>
    </div>
</div>""", unsafe_allow_html=True)

# =============================================================================
# INPUT SECTION WRAPPER
# =============================================================================
def section_header(icon, title):
    st.markdown(f'<div style="font-size:0.67rem;font-weight:700;letter-spacing:0.13em;text-transform:uppercase;color:#FACC15;margin:1.4rem 0 0.8rem;display:flex;align-items:center;gap:7px;">{icon} &nbsp; {title}<span style="flex:1;height:1px;background:linear-gradient(90deg,#1C1C1C,transparent);margin-left:10px;"></span></div>', unsafe_allow_html=True)

def input_box_start():
    st.markdown('<div style="background:#111;border:1px solid #1C1C1C;border-top:2px solid #FACC15;border-radius:14px;padding:1.5rem 1.8rem 1rem;">', unsafe_allow_html=True)

def input_box_end():
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# DIVIDER
# =============================================================================
def divider(label):
    st.markdown(f'<div style="display:flex;align-items:center;gap:14px;margin:2rem 0 1.2rem;"><div style="flex:1;height:1px;background:#1C1C1C;"></div><div style="font-size:0.66rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#FACC15;white-space:nowrap;">{label}</div><div style="flex:1;height:1px;background:#1C1C1C;"></div></div>', unsafe_allow_html=True)

# =============================================================================
# RESULT CARDS
# =============================================================================
def price_card(pred, low, high, jt, dl, bc, prem):
    dc = "#EF4444" if dl=="High" else "#F59E0B" if dl=="Medium" else "#22C55E"
    bc_col = "#EF4444" if bc=="Last Minute" else "#F59E0B" if bc=="Early" else "#22C55E"
    tc = "#FACC15" if prem else "#93C5FD"
    st.markdown(f"""
<div class="fade" style="background:linear-gradient(135deg,#111100,#1C1900);border:1px solid #2A2200;border-top:2px solid #FACC15;border-radius:18px;padding:2.4rem 2rem;text-align:center;position:relative;overflow:hidden;margin-bottom:1rem;">
    <div style="position:absolute;top:-40px;left:50%;transform:translateX(-50%);width:200px;height:200px;border-radius:50%;background:radial-gradient(circle,rgba(250,204,21,0.07),transparent 70%);pointer-events:none;"></div>
    <div style="font-size:0.66rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#555;margin-bottom:0.55rem;">Predicted Flight Fare</div>
    <div style="font-size:4rem;font-weight:900;letter-spacing:-2px;line-height:1;background:linear-gradient(135deg,#FACC15,#FDE047);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.5rem;">₹{int(pred):,}</div>
    <div style="font-size:0.77rem;color:#333;font-family:'JetBrains Mono',monospace;margin-bottom:1.8rem;">₹{int(low):,} &nbsp;—&nbsp; ₹{int(high):,}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
        <div style="background:#0A0A0A;border:1px solid #1C1C1C;border-radius:10px;padding:0.9rem 0.7rem;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#333;margin-bottom:5px;">Journey</div>
            <div style="font-size:0.82rem;font-weight:700;color:#FACC15;">{jt.replace("_"," ")}</div>
        </div>
        <div style="background:#0A0A0A;border:1px solid #1C1C1C;border-radius:10px;padding:0.9rem 0.7rem;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#333;margin-bottom:5px;">Demand</div>
            <div style="font-size:0.82rem;font-weight:700;color:{dc};">{dl}</div>
        </div>
        <div style="background:#0A0A0A;border:1px solid #1C1C1C;border-radius:10px;padding:0.9rem 0.7rem;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#333;margin-bottom:5px;">Booking</div>
            <div style="font-size:0.82rem;font-weight:700;color:{bc_col};">{bc}</div>
        </div>
        <div style="background:#0A0A0A;border:1px solid #1C1C1C;border-radius:10px;padding:0.9rem 0.7rem;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#333;margin-bottom:5px;">Tier</div>
            <div style="font-size:0.82rem;font-weight:700;color:{tc};">{"Premium ✦" if prem else "Budget"}</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)


def price_range(low, pred, high):
    st.markdown(f"""
<div style="background:#111;border:1px solid #1C1C1C;border-radius:14px;padding:1.3rem 1.5rem;margin-bottom:1rem;">
    <div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#555;margin-bottom:1rem;">💰 &nbsp; Estimated Price Range</div>
    <div style="display:flex;">
        <div style="flex:1;text-align:center;padding:1rem 0.5rem;background:#0A0A0A;border:1px solid #1C1C1C;border-right:none;border-radius:10px 0 0 10px;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#333;margin-bottom:6px;">Low</div>
            <div style="font-size:1.15rem;font-weight:700;color:#22C55E;font-family:'JetBrains Mono',monospace;">₹{int(low):,}</div>
        </div>
        <div style="flex:1;text-align:center;padding:1rem 0.5rem;background:linear-gradient(135deg,#1A1400,#221B00);border:2px solid #FACC15;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#FACC15;margin-bottom:6px;">Predicted</div>
            <div style="font-size:1.25rem;font-weight:900;color:#FACC15;font-family:'JetBrains Mono',monospace;">₹{int(pred):,}</div>
        </div>
        <div style="flex:1;text-align:center;padding:1rem 0.5rem;background:#0A0A0A;border:1px solid #1C1C1C;border-left:none;border-radius:0 10px 10px 0;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#333;margin-bottom:6px;">High</div>
            <div style="font-size:1.15rem;font-weight:700;color:#EF4444;font-family:'JetBrains Mono',monospace;">₹{int(high):,}</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)


def flight_summary(src, dst, airline, cls, stops_lbl, dep, holiday):
    rows = [("Route",f"{src} → {dst}"),("Airline",airline.replace("_"," ")),
            ("Class",cls),("Stops",stops_lbl.strip().replace("✈","").strip()),
            ("Departure",dep.replace("_"," ")),("Holiday",holiday)]
    html = "".join(f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #111;"><div style="width:5px;height:5px;border-radius:50%;background:#FACC15;flex-shrink:0;"></div><div style="font-size:0.73rem;color:#333;width:75px;flex-shrink:0;font-weight:500;">{k}</div><div style="font-size:0.82rem;font-weight:600;color:#BDBDBD;">{v}</div></div>' for k,v in rows)
    st.markdown(f'<div style="background:#111;border:1px solid #1C1C1C;border-radius:13px;padding:1.1rem 1.3rem;margin-bottom:1rem;">{html}</div>', unsafe_allow_html=True)


def auto_note(dist, dur, rating, seats, days, spd):
    st.markdown(f'<div style="background:rgba(250,204,21,0.05);border:1px solid rgba(250,204,21,0.15);border-radius:10px;padding:10px 14px;font-size:0.76rem;color:#FACC15;margin-bottom:1rem;font-family:\'JetBrains Mono\',monospace;line-height:1.7;">⚡ auto-computed &nbsp;·&nbsp; dist: <strong>{dist:,} km</strong> &nbsp;·&nbsp; dur: <strong>{dur:.1f} h</strong> &nbsp;·&nbsp; rating: <strong>{rating}</strong> &nbsp;·&nbsp; seats: <strong>{seats}</strong> &nbsp;·&nbsp; window: <strong>{days} days</strong> &nbsp;·&nbsp; speed: <strong>{spd:.0f} km/h</strong></div>', unsafe_allow_html=True)


def plotly_chart(low, pred, high):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Low Estimate","Predicted Price","High Estimate"],
        y=[low,pred,high],
        marker=dict(color=["#14290C","#FACC15","#2D0E0E"],
                    line=dict(color=["#22C55E","#EAB308","#EF4444"],width=2),
                    cornerradius=8),
        text=[f"₹{int(v):,}" for v in [low,pred,high]],
        textposition="outside",
        textfont=dict(size=12,family="JetBrains Mono",
                      color=["#22C55E","#FACC15","#EF4444"]),
        width=0.42,
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=pred,line_dash="dot",line_color="#FACC15",line_width=1.2)
    fig.update_layout(
        plot_bgcolor="#0A0A0A",paper_bgcolor="#0A0A0A",
        xaxis=dict(showgrid=False,tickfont=dict(color="#333",size=11),linecolor="#1C1C1C"),
        yaxis=dict(showgrid=True,gridcolor="#111",tickprefix="₹",tickformat=",",
                   tickfont=dict(color="#333",size=10,family="JetBrains Mono"),
                   range=[0,high*1.3],linecolor="#1C1C1C"),
        margin=dict(t=20,b=10,l=10,r=10),height=270,showlegend=False,bargap=0.5,
    )
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})


def insights(dl, cls, prem, holiday, stops_raw, dep):
    tips = []
    if dl=="High":
        tips.append(("#EF4444","rgba(239,68,68,0.08)","rgba(239,68,68,0.2)","🔴 High Demand","Seats are scarce and departure is near. Prices are at their peak."))
    elif dl=="Medium":
        tips.append(("#F59E0B","rgba(245,158,11,0.08)","rgba(245,158,11,0.2)","🟡 Moderate Demand","Some seats available. Price may rise as departure approaches."))
    else:
        tips.append(("#22C55E","rgba(34,197,94,0.08)","rgba(34,197,94,0.2)","🟢 Low Demand","Good availability and lead time — a more affordable pricing window."))
    if cls=="Business":
        tips.append(("#FACC15","rgba(250,204,21,0.06)","rgba(250,204,21,0.18)","💼 Business Class","Business fares average 8× more than Economy on Indian domestic routes."))
    if prem:
        tips.append(("#FACC15","rgba(250,204,21,0.06)","rgba(250,204,21,0.18)","⭐ Premium Airline","Vistara and Air India charge ~5× more than budget carriers on the same route."))
    else:
        tips.append(("#93C5FD","rgba(147,197,253,0.06)","rgba(147,197,253,0.18)","💡 Budget Carrier","Economy on a budget airline gives the lowest possible fare on any route."))
    if holiday=="Yes":
        tips.append(("#F59E0B","rgba(245,158,11,0.08)","rgba(245,158,11,0.2)","🎉 Holiday Season","Elevated demand during holidays typically pushes fares higher."))
    if stops_raw=="zero":
        tips.append(("#93C5FD","rgba(147,197,253,0.06)","rgba(147,197,253,0.18)","⚡ Non-Stop Flight","Direct flights have the shortest travel time on this route."))
    if dep in ["Early_Morning","Late_Night"]:
        tips.append(("#22C55E","rgba(34,197,94,0.08)","rgba(34,197,94,0.2)","🌙 Off-Peak Departure","Early morning and late night departures typically carry lower fares."))

    cols = st.columns(2)
    for idx,(fg,bg,border,title,desc) in enumerate(tips):
        with cols[idx%2]:
            st.markdown(f'<div style="background:{bg};border:1px solid {border};border-left:3px solid {fg};border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:8px;"><div style="font-size:0.82rem;font-weight:700;color:#FFF;margin-bottom:4px;">{title}</div><div style="font-size:0.77rem;color:#555;line-height:1.55;">{desc}</div></div>', unsafe_allow_html=True)


def footer():
    st.markdown("""
<div style="text-align:center;padding:2.5rem 1rem 1.5rem;margin-top:2rem;border-top:1px solid #111;line-height:2;">
    <div style="font-size:1.3rem;font-weight:900;letter-spacing:-0.5px;background:linear-gradient(135deg,#FACC15,#EAB308);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:4px;">FlightAI</div>
    <div style="font-size:0.77rem;color:#222;">Made with ❤️ by <strong style="color:#FACC15;">Mohammed Nihal</strong> &nbsp;·&nbsp; Machine Learning Project &nbsp;·&nbsp; <a href="https://github.com" target="_blank" style="color:#FACC15;text-decoration:none;font-weight:600;">GitHub</a> &nbsp;·&nbsp; <a href="https://linkedin.com" target="_blank" style="color:#FACC15;text-decoration:none;font-weight:600;">LinkedIn</a></div>
    <div style="font-size:0.68rem;color:#1A1A1A;margin-top:4px;">Streamlit · Scikit-learn · Plotly · Python &nbsp;·&nbsp; © 2025</div>
</div>""", unsafe_allow_html=True)

# =============================================================================
# MAIN
# =============================================================================
def main():
    css()

    try:
        lr_model, scaler, feature_columns = load_models()
    except FileNotFoundError as e:
        st.error(f"**Model files not found.** Ensure the `models/` folder is beside `app.py`.\n\n`{e}`")
        st.stop()

    sidebar()

    # ── Top bar ──────────────────────────────────────────────────
    st.markdown('<div style="padding:1.2rem 0 0;display:flex;align-items:center;justify-content:space-between;"><div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#333;">✈ &nbsp; FlightAI</div><div style="display:flex;gap:16px;"><span style="font-size:0.75rem;color:#333;font-weight:500;">Powered by Linear Regression</span><span style="font-size:0.75rem;color:#FACC15;font-weight:700;">R² 0.937</span></div></div>', unsafe_allow_html=True)

    # ── Project info toggle ───────────────────────────────────────
    with st.expander("☰  Project Info & Model Details", expanded=False):
        st.markdown('<div style="font-size:0.8rem;color:#555;line-height:1.8;padding:4px 0;"><strong style="color:#FACC15;">Algorithm:</strong> Linear Regression &nbsp;·&nbsp; <strong style="color:#FACC15;">Training rows:</strong> 240,174 flights &nbsp;·&nbsp; <strong style="color:#FACC15;">R²:</strong> 0.937 &nbsp;·&nbsp; <strong style="color:#FACC15;">MAE:</strong> ₹3,708<br><strong style="color:#FACC15;">Features:</strong> 45 columns &nbsp;·&nbsp; <strong style="color:#FACC15;">Author:</strong> Mohammed Nihal &nbsp;·&nbsp; <a href="https://github.com" style="color:#FACC15;">GitHub</a> &nbsp;·&nbsp; <a href="https://linkedin.com" style="color:#FACC15;">LinkedIn</a></div>', unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────
    hero()

    # ── Flight Information ────────────────────────────────────────
    section_header("🗺️","Flight Information")
    input_box_start()
    c1,c2,c3 = st.columns(3)
    with c1: source_city = st.selectbox("Source City", CITIES, index=2)
    with c2:
        dest_opts        = [c for c in CITIES if c!=source_city]
        destination_city = st.selectbox("Destination City", dest_opts)
    with c3: airline = st.selectbox("Airline", AIRLINES)
    c1,c2 = st.columns(2)
    with c1: departure_time = st.selectbox("Departure Time", TIMES)
    with c2:
        stops_label = st.selectbox("Number of Stops", list(STOPS.keys()))
        stops_raw   = STOPS[stops_label]
    input_box_end()

    # ── Passenger Details ─────────────────────────────────────────
    section_header("👤","Passenger Details")
    input_box_start()
    c1,c2 = st.columns(2)
    with c1: travel_class   = st.selectbox("Travel Class", CLASSES)
    with c2: holiday_season = st.selectbox("Holiday Season", HOLIDAY)
    input_box_end()

    # ── Predict button ────────────────────────────────────────────
    predict = st.button("✈  Predict Flight Price")

    # ── Prediction ───────────────────────────────────────────────
    if predict:
        if source_city == destination_city:
            st.error("⚠️  Source and destination city cannot be the same.")
            st.stop()

        dist,dur,rating,seats,days,arr = auto_derive(
            source_city,destination_city,stops_raw,airline,travel_class,holiday_season)

        jt,dl,bc,prem,spd,hol = engineer(
            airline,travel_class,stops_raw,seats,days,dist,dur,rating,holiday_season)

        df_input = preprocess(
            airline,source_city,destination_city,
            departure_time,arr,stops_raw,travel_class,
            hol,dur,days,float(dist),float(seats),rating,
            jt,dl,bc,prem,spd,feature_columns)

        X_scaled   = scaler.transform(df_input)
        prediction = lr_model.predict(X_scaled)[0]
        prediction = max(1000.0, prediction)
        low_price  = round(prediction*0.92)
        pred_price = round(prediction)
        high_price = round(prediction*1.08)

        divider("Prediction Results")

        col_l,col_r = st.columns([1,1],gap="large")
        with col_l:
            price_card(pred_price,low_price,high_price,jt,dl,bc,prem)
            price_range(low_price,pred_price,high_price)
        with col_r:
            st.markdown('<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#555;margin-bottom:8px;">Flight Summary</div>', unsafe_allow_html=True)
            flight_summary(source_city,destination_city,airline,
                           travel_class,stops_label,departure_time,holiday_season)
            auto_note(dist,dur,rating,seats,days,spd)
            st.markdown('<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#555;margin-bottom:6px;">Price Breakdown</div>', unsafe_allow_html=True)
            plotly_chart(low_price,pred_price,high_price)

        divider("Smart Booking Insights")
        insights(dl,travel_class,prem,holiday_season,stops_raw,departure_time)

    footer()

# =============================================================================
if __name__ == "__main__":
    main()
