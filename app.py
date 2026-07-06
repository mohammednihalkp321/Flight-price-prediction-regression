

# import streamlit as st
# import pandas as pd
# import numpy as np
# import joblib
# import plotly.graph_objects as go
# import os

# # =============================================================================
# # PAGE CONFIG
# # =============================================================================
# st.set_page_config(
#     page_title="Flight Price Predictor",
#     page_icon="✈️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # =============================================================================
# # REAL CITY-PAIR DISTANCES (km)  — used to auto-compute duration & distance
# # =============================================================================
# CITY_DISTANCES = {
#     ("Bangalore","Chennai"):290,  ("Chennai","Bangalore"):290,
#     ("Bangalore","Delhi"):1740,   ("Delhi","Bangalore"):1740,
#     ("Bangalore","Hyderabad"):500,("Hyderabad","Bangalore"):500,
#     ("Bangalore","Kolkata"):1560, ("Kolkata","Bangalore"):1560,
#     ("Bangalore","Mumbai"):845,   ("Mumbai","Bangalore"):845,
#     ("Chennai","Delhi"):1760,     ("Delhi","Chennai"):1760,
#     ("Chennai","Hyderabad"):520,  ("Hyderabad","Chennai"):520,
#     ("Chennai","Kolkata"):1360,   ("Kolkata","Chennai"):1360,
#     ("Chennai","Mumbai"):1035,    ("Mumbai","Chennai"):1035,
#     ("Delhi","Hyderabad"):1250,   ("Hyderabad","Delhi"):1250,
#     ("Delhi","Kolkata"):1305,     ("Kolkata","Delhi"):1305,
#     ("Delhi","Mumbai"):1150,      ("Mumbai","Delhi"):1150,
#     ("Hyderabad","Kolkata"):1185, ("Kolkata","Hyderabad"):1185,
#     ("Hyderabad","Mumbai"):620,   ("Mumbai","Hyderabad"):620,
#     ("Kolkata","Mumbai"):1660,    ("Mumbai","Kolkata"):1660,
# }

# # =============================================================================
# # CONSTANTS
# # =============================================================================
# AIRLINES      = ["AirAsia","Air_India","GO_FIRST","Indigo","SpiceJet","Vistara"]
# CITIES        = ["Bangalore","Chennai","Delhi","Hyderabad","Kolkata","Mumbai"]
# TIME_SLOTS    = ["Early_Morning","Morning","Afternoon","Evening","Night","Late_Night"]
# STOPS_DISPLAY = {"Non-Stop":"zero","1 Stop":"one","2+ Stops":"two_or_more"}
# CLASS_OPTIONS = ["Economy","Business"]
# HOLIDAY_OPT   = ["No","Yes"]
# PREMIUM_LIST  = ["Vistara","Air_India"]

# # =============================================================================
# # CSS  —  Deep teal + slate professional palette
# # =============================================================================
# def inject_css():
#     st.markdown("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

#     html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#     /* ── Background ── */
#     .stApp { background: #F1F5F9; }

#     /* ── Sidebar ── */
#     [data-testid="stSidebar"] {
#         background: linear-gradient(175deg, #0F2942 0%, #0D3D56 45%, #0A4A5E 100%);
#         border-right: none;
#         box-shadow: 4px 0 20px rgba(0,0,0,0.15);
#     }
#     [data-testid="stSidebar"] * { color: #E2EDF5 !important; }
#     [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.10) !important; margin:14px 0; }
#     [data-testid="stSidebar"] a { color: #67C6E3 !important; text-decoration:none; }
#     [data-testid="stSidebar"] a:hover { color:#FFFFFF !important; text-decoration:underline; }

#     /* ── Card ── */
#     .card {
#         background: #FFFFFF;
#         border-radius: 16px;
#         padding: 1.6rem 1.8rem 1.4rem;
#         margin-bottom: 1.1rem;
#         box-shadow: 0 1px 8px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
#         border: 1px solid #E2E8F0;
#     }
#     .card-title {
#         font-size: 0.7rem;
#         font-weight: 700;
#         letter-spacing: 0.12em;
#         text-transform: uppercase;
#         color: #0D6EFD;
#         margin: 0 0 1.2rem;
#         padding-bottom: 0.7rem;
#         border-bottom: 2px solid #EEF2F7;
#         display: flex;
#         align-items: center;
#         gap: 7px;
#     }

#     /* ── Hero banner ── */
#     .hero {
#         background: linear-gradient(130deg, #0F2942 0%, #0D6EFD 60%, #06B6D4 100%);
#         border-radius: 18px;
#         padding: 2.2rem 2.6rem;
#         margin-bottom: 1.4rem;
#         box-shadow: 0 8px 30px rgba(13,110,253,0.28);
#         position: relative;
#         overflow: hidden;
#     }
#     .hero::after {
#         content: "✈";
#         position: absolute;
#         right: 2rem; top: 50%;
#         transform: translateY(-50%) rotate(45deg);
#         font-size: 8rem;
#         opacity: 0.06;
#         pointer-events: none;
#     }
#     .hero h1 {
#         color: #FFFFFF;
#         font-size: 2rem;
#         font-weight: 800;
#         margin: 0 0 0.4rem;
#         letter-spacing: -0.6px;
#     }
#     .hero p {
#         color: rgba(255,255,255,0.78);
#         font-size: 0.93rem;
#         margin: 0;
#         max-width: 540px;
#     }

#     /* ── Price result card ── */
#     .price-card {
#         background: linear-gradient(130deg, #0F2942 0%, #0D6EFD 100%);
#         border-radius: 16px;
#         padding: 2.4rem 2rem;
#         text-align: center;
#         color: white;
#         box-shadow: 0 8px 32px rgba(13,110,253,0.30);
#         margin-bottom: 1rem;
#     }
#     .price-eyebrow {
#         font-size: 0.72rem;
#         font-weight: 600;
#         letter-spacing: 0.14em;
#         text-transform: uppercase;
#         opacity: 0.65;
#         margin-bottom: 0.5rem;
#     }
#     .price-main {
#         font-size: 3.6rem;
#         font-weight: 800;
#         letter-spacing: -2px;
#         line-height: 1;
#     }
#     .price-range {
#         font-size: 0.83rem;
#         opacity: 0.62;
#         margin-top: 0.6rem;
#     }

#     /* ── Stat boxes ── */
#     .stat-grid {
#         display: grid;
#         grid-template-columns: repeat(4,1fr);
#         gap: 10px;
#         margin-top: 4px;
#     }
#     .stat-box {
#         background: #F8FAFC;
#         border: 1px solid #E2E8F0;
#         border-radius: 12px;
#         padding: 0.9rem 0.8rem;
#         text-align: center;
#     }
#     .stat-label {
#         font-size: 0.66rem;
#         font-weight: 700;
#         text-transform: uppercase;
#         letter-spacing: 0.09em;
#         color: #94A3B8;
#         margin-bottom: 5px;
#     }
#     .stat-value {
#         font-size: 1.0rem;
#         font-weight: 700;
#         color: #0F2942;
#     }

#     /* ── Auto-computed info banner ── */
#     .auto-banner {
#         background: #EFF6FF;
#         border: 1px solid #BFDBFE;
#         border-radius: 10px;
#         padding: 10px 14px;
#         font-size: 0.82rem;
#         color: #1E40AF;
#         margin-top: 10px;
#         line-height: 1.6;
#     }

#     /* ── Chip badges ── */
#     .chip-row { display:flex; flex-wrap:wrap; gap:7px; margin-top:8px; }
#     .chip {
#         font-size: 0.78rem;
#         font-weight: 600;
#         padding: 4px 12px;
#         border-radius: 20px;
#         display: inline-block;
#     }
#     .chip-blue   { background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; }
#     .chip-green  { background:#F0FDF4; color:#15803D; border:1px solid #BBF7D0; }
#     .chip-amber  { background:#FFFBEB; color:#92400E; border:1px solid #FDE68A; }
#     .chip-red    { background:#FFF1F2; color:#9F1239; border:1px solid #FECDD3; }
#     .chip-purple { background:#FAF5FF; color:#6B21A8; border:1px solid #E9D5FF; }
#     .chip-cyan   { background:#ECFEFF; color:#155E75; border:1px solid #A5F3FC; }

#     /* ── Button ── */
#     div[data-testid="stButton"] > button {
#         background: linear-gradient(135deg, #0F2942 0%, #0D6EFD 100%);
#         color: white;
#         border: none;
#         border-radius: 12px;
#         padding: 0.8rem 2rem;
#         font-size: 1rem;
#         font-weight: 700;
#         width: 100%;
#         letter-spacing: 0.2px;
#         box-shadow: 0 4px 14px rgba(13,110,253,0.35);
#         transition: all 0.2s;
#     }
#     div[data-testid="stButton"] > button:hover {
#         box-shadow: 0 6px 20px rgba(13,110,253,0.45);
#         transform: translateY(-1px);
#     }

#     /* ── Inputs ── */
#     div[data-testid="stSelectbox"] label,
#     div[data-testid="stNumberInput"] label {
#         font-size: 0.86rem;
#         font-weight: 600;
#         color: #334155;
#     }

#     /* ── Alert styling ── */
#     div[data-testid="stAlert"] { border-radius: 10px !important; }

#     /* ── Footer ── */
#     .footer {
#         text-align: center;
#         padding: 2rem 1rem 1.5rem;
#         margin-top: 2.5rem;
#         border-top: 1px solid #E2E8F0;
#         color: #94A3B8;
#         font-size: 0.8rem;
#         line-height: 1.9;
#     }
#     .footer a { color: #0D6EFD; text-decoration: none; font-weight: 600; }
#     .footer a:hover { text-decoration: underline; }
#     </style>
#     """, unsafe_allow_html=True)


# # =============================================================================
# # LOAD MODELS
# # =============================================================================
# @st.cache_resource(show_spinner=False)
# def load_models():
#     base    = os.path.join(os.path.dirname(__file__), "models")
#     lr      = joblib.load(os.path.join(base, "linear_regression_model.pkl"))
#     scaler  = joblib.load(os.path.join(base, "standard_scaler.pkl"))
#     columns = joblib.load(os.path.join(base, "feature_columns.pkl"))
#     return lr, scaler, columns


# # =============================================================================
# # AUTO-DERIVE removed inputs from available inputs
# # =============================================================================
# def auto_derive(source_city, destination_city, stops, airline,
#                 travel_class, holiday_season):
#     """
#     Automatically compute the 6 removed inputs using real-world logic
#     so the model still receives all values it was trained on.
#     """
#     # 1. Flight distance — real geodesic distance per city pair
#     base_dist    = CITY_DISTANCES.get((source_city, destination_city), 1200)
#     stop_mult    = {"zero": 1.0, "one": 1.10, "two_or_more": 1.20}
#     flight_distance = round(base_dist * stop_mult[stops])

#     # 2. Duration — distance / cruise speed + layover time
#     cruise_speed  = 750   # km/h typical Indian domestic jet
#     layover_hours = {"zero": 0, "one": 3.0, "two_or_more": 6.0}
#     air_time      = base_dist / cruise_speed
#     duration      = round(air_time * stop_mult[stops] + layover_hours[stops], 2)
#     duration      = max(0.5, duration)

#     # 3. Airline rating — fixed real-world ratings per carrier
#     airline_ratings = {
#         "Vistara": 4.7, "Air_India": 4.6, "Indigo": 4.5,
#         "SpiceJet": 4.2, "AirAsia": 4.1, "GO_FIRST": 4.0,
#     }
#     airline_rating = airline_ratings.get(airline, 4.3)

#     # 4. Seat availability — realistic estimate by route demand + stops
#     # Fewer seats → more expensive; more stops → typically less demand
#     base_seats = {"zero": 45, "one": 65, "two_or_more": 90}
#     seat_availability = base_seats[stops]

#     # 5. Days left — neutral mid-range: 15 days
#     days_left = 15

#     # 6. Arrival time — set to most common arrival band per departure analysis
#     # Using "Evening" as the most frequent arrival slot; all arrival_time_* OHE
#     # columns will be zero if it maps to the baseline "Afternoon" dropped category
#     arrival_time = "Evening"

#     return (flight_distance, duration, airline_rating,
#             seat_availability, days_left, arrival_time)


# # =============================================================================
# # FEATURE ENGINEERING  (mirrors notebook cells 59, 62, 65, 69, 72, 77 exactly)
# # =============================================================================
# def engineer_features(airline, travel_class, stops,
#                       seat_availability, days_left,
#                       flight_distance, duration,
#                       airline_rating, holiday_season):

#     # journey_type (cell 59)
#     stop_map     = {"zero": "Direct", "one": "OneStop", "two_or_more": "MultiStop"}
#     journey_type = travel_class + "_" + stop_map[stops]

#     # demand_level (cell 62)
#     if seat_availability <= 30 and days_left <= 7:
#         demand_level = "High"
#     elif seat_availability <= 70 and days_left <= 30:
#         demand_level = "Medium"
#     else:
#         demand_level = "Low"

#     # booking_category (cell 65)  bins=[0,7,30,inf]
#     if days_left <= 7:
#         booking_category = "Last Minute"
#     elif days_left <= 30:
#         booking_category = "Early"
#     else:
#         booking_category = "Advance"

#     # premium_airline (cell 69)
#     premium_airline = int(airline_rating >= 4.5)

#     # speed_kmh (cell 72)
#     speed_kmh = round(flight_distance / duration, 2) if duration > 0 else 0.0

#     # holiday_season label encode (cell 77)  No=0 Yes=1
#     holiday_encoded = 1 if holiday_season == "Yes" else 0

#     return (journey_type, demand_level, booking_category,
#             premium_airline, speed_kmh, holiday_encoded)


# # =============================================================================
# # PREPROCESSING  (mirrors notebook cells 77, 79 exactly)
# # =============================================================================
# def preprocess(airline, source_city, destination_city,
#                departure_time, arrival_time, stops, travel_class,
#                holiday_encoded, duration, days_left,
#                flight_distance, seat_availability, airline_rating,
#                journey_type, demand_level, booking_category,
#                premium_airline, speed_kmh, feature_columns):

#     row = {
#         "duration":           duration,
#         "days_left":          days_left,
#         "flight_distance_km": flight_distance,
#         "seat_availability":  int(seat_availability),
#         "holiday_season":     holiday_encoded,
#         "airline_rating":     airline_rating,
#         "premium_airline":    premium_airline,
#         "speed_kmh":          speed_kmh,
#         "airline":            airline,
#         "source_city":        source_city,
#         "departure_time":     departure_time,
#         "stops":              stops,
#         "arrival_time":       arrival_time,
#         "destination_city":   destination_city,
#         "class":              travel_class,
#         "journey_type":       journey_type,
#         "demand_level":       demand_level,
#         "booking_category":   booking_category,
#     }

#     df = pd.DataFrame([row])
#     df = pd.get_dummies(
#         df,
#         columns=["airline","source_city","departure_time","stops",
#                  "arrival_time","destination_city","class",
#                  "journey_type","demand_level","booking_category"],
#         drop_first=True, dtype=int
#     )

#     # Align to training columns
#     for col in feature_columns:
#         if col not in df.columns:
#             df[col] = 0

#     return df[feature_columns]


# # =============================================================================
# # PLOTLY PRICE RANGE CHART
# # =============================================================================
# def price_chart(low, predicted, high):
#     labels = ["Low Estimate", "Predicted Price", "High Estimate"]
#     values = [low, predicted, high]
#     colors = ["#93C5FD", "#0D6EFD", "#6EE7B7"]

#     fig = go.Figure()
#     fig.add_trace(go.Bar(
#         x=labels, y=values,
#         marker=dict(
#             color=colors,
#             line=dict(color=["#60A5FA","#0B5ED7","#34D399"], width=1.5)
#         ),
#         text=[f"₹{v:,.0f}" for v in values],
#         textposition="outside",
#         textfont=dict(size=12, color="#0F2942", family="Inter"),
#         width=0.38
#     ))
#     fig.update_layout(
#         yaxis=dict(
#             title="Price (₹)",
#             showgrid=True, gridcolor="#F1F5F9",
#             tickformat=",", tickprefix="₹",
#             range=[0, high * 1.22]
#         ),
#         xaxis=dict(showgrid=False),
#         plot_bgcolor="#FFFFFF",
#         paper_bgcolor="#FFFFFF",
#         margin=dict(t=30, b=10, l=10, r=10),
#         height=300,
#         showlegend=False,
#         font=dict(family="Inter", color="#334155")
#     )
#     return fig


# # =============================================================================
# # SIDEBAR
# # =============================================================================
# def render_sidebar():
#     with st.sidebar:

#         st.markdown("""
#         <div style="text-align:center;padding:1.2rem 0 0.6rem;">
#             <div style="font-size:3.2rem;">✈️</div>
#             <div style="font-size:1.15rem;font-weight:800;letter-spacing:-0.3px;
#                         margin:0.3rem 0 0.15rem;">Flight Price Predictor</div>
#             <div style="font-size:0.75rem;opacity:0.5;letter-spacing:0.04em;">
#                 ML REGRESSION PROJECT
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#         st.markdown("---")

#         st.markdown("""
#         <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
#                     text-transform:uppercase;opacity:0.45;margin-bottom:8px;">
#             About
#         </div>
#         <div style="font-size:0.82rem;opacity:0.78;line-height:1.7;">
#             Predicts Indian domestic flight fares using a
#             <strong>Linear Regression</strong> model trained on
#             300,000+ real flight records. Just pick your route and
#             get an instant fare estimate — no technical inputs needed.
#         </div>
#         """, unsafe_allow_html=True)

#         st.markdown("---")

#         st.markdown("""
#         <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
#                     text-transform:uppercase;opacity:0.45;margin-bottom:10px;">
#             Model Info
#         </div>
#         """, unsafe_allow_html=True)

#         for k, v in [
#             ("🧠 Algorithm",    "Linear Regression"),
#             ("📊 Training Rows","240,174 flights"),
#             ("🎯 R² Score",     "0.937"),
#             ("📉 MAE",          "₹3,708"),
#             ("⚙️ Features",     "45 columns"),
#         ]:
#             st.markdown(f"""
#             <div style="display:flex;justify-content:space-between;padding:5px 0;
#                         border-bottom:1px solid rgba(255,255,255,0.07);">
#                 <span style="font-size:0.79rem;opacity:0.68;">{k}</span>
#                 <span style="font-size:0.79rem;font-weight:700;">{v}</span>
#             </div>""", unsafe_allow_html=True)

#         st.markdown("---")

#         st.markdown("""
#         <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
#                     text-transform:uppercase;opacity:0.45;margin-bottom:8px;">
#             Auto-Computed Inputs
#         </div>
#         <div style="font-size:0.79rem;opacity:0.72;line-height:1.75;">
#             The following values are <em>automatically derived</em> from
#             your route &amp; airline — so you don't need to enter them manually:<br>
#             • Flight distance (real city-pair km)<br>
#             • Flight duration (distance ÷ cruise speed + layover)<br>
#             • Airline rating (per-carrier real ratings)<br>
#             • Seat availability (typical fill by stop type)<br>
#             • Booking window (15-day default)<br>
#             • Arrival time (route-typical band)
#         </div>
#         """, unsafe_allow_html=True)

#         st.markdown("---")

#         st.markdown("""
#         <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
#                     text-transform:uppercase;opacity:0.45;margin-bottom:8px;">
#             Technologies
#         </div>""", unsafe_allow_html=True)

#         for t in ["🐍 Python 3.11","🔢 Pandas · NumPy",
#                   "🤖 Scikit-learn","💾 Joblib","📊 Plotly","🌐 Streamlit"]:
#             st.markdown(f"""
#             <div style="font-size:0.8rem;padding:4px 0;opacity:0.75;">{t}</div>
#             """, unsafe_allow_html=True)

#         st.markdown("---")

#         st.markdown("""
#         <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
#                     text-transform:uppercase;opacity:0.45;margin-bottom:10px;">
#             Author
#         </div>
#         <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
#             <div style="width:42px;height:42px;border-radius:50%;flex-shrink:0;
#                         background:linear-gradient(135deg,#0D6EFD,#06B6D4);
#                         display:flex;align-items:center;justify-content:center;
#                         font-size:1.1rem;font-weight:800;">M</div>
#             <div>
#                 <div style="font-size:0.9rem;font-weight:700;">Mohammed Nihal</div>
#                 <div style="font-size:0.72rem;opacity:0.55;">Data Analyst Intern</div>
#             </div>
#         </div>
#         <div style="display:flex;gap:8px;">
#             <a href="https://github.com" target="_blank"
#                style="flex:1;text-align:center;background:rgba(255,255,255,0.10);
#                       border-radius:8px;padding:7px 4px;font-size:0.78rem;
#                       font-weight:700;color:#E2EDF5 !important;">🐙 GitHub</a>
#             <a href="https://linkedin.com" target="_blank"
#                style="flex:1;text-align:center;background:rgba(255,255,255,0.10);
#                       border-radius:8px;padding:7px 4px;font-size:0.78rem;
#                       font-weight:700;color:#E2EDF5 !important;">💼 LinkedIn</a>
#         </div>
#         """, unsafe_allow_html=True)


# # =============================================================================
# # DYNAMIC TIPS
# # =============================================================================
# def render_tips(days_left, seat_availability, travel_class,
#                 premium_airline, demand_level, holiday_season):

#     if demand_level == "High":
#         st.error("🔴 **High Demand Flight** — Seats are scarce and departure is near. "
#                  "This is the peak pricing window.")
#     elif demand_level == "Medium":
#         st.warning("🟡 **Moderate Demand** — Some seats available with moderate "
#                    "booking urgency. Price may rise closer to departure.")
#     else:
#         st.success("🟢 **Low Demand Window** — Good availability and lead time. "
#                    "This is one of the more affordable pricing windows.")

#     if travel_class == "Business":
#         st.info("💺 **Business Class** — Business tickets average **8× more** "
#                 "than Economy on Indian domestic routes.")

#     if premium_airline:
#         st.info("⭐ **Premium Airline Selected** — Vistara and Air India charge "
#                 "approximately **5× more** than budget carriers on the same route.")

#     if holiday_season == "Yes":
#         st.warning("🎉 **Holiday Season** — Travelling during a holiday period. "
#                    "Demand is typically higher, which can push fares up.")

#     if not premium_airline and travel_class == "Economy":
#         st.success("💡 **Best Value Combination** — Economy class on a budget carrier "
#                    "gives you the lowest possible fare on this route.")


# # =============================================================================
# # MAIN
# # =============================================================================
# def main():

#     inject_css()

#     # ── Load models ───────────────────────────────────────────────────────────
#     try:
#         lr_model, scaler, feature_columns = load_models()
#     except FileNotFoundError as e:
#         st.error(f"**Model files not found.**  Make sure the `models/` folder "
#                  f"is in the same directory as `app.py`.\n\n`{e}`")
#         st.stop()

#     render_sidebar()

#     # ── Hero ──────────────────────────────────────────────────────────────────
#     st.markdown("""
#     <div class="hero">
#         <h1>✈️ Flight Price Prediction</h1>
#         <p>Select your route, airline, and travel preferences — the app handles
#            everything else and gives you an instant AI-powered fare estimate.</p>
#     </div>
#     """, unsafe_allow_html=True)

#     # =========================================================================
#     # SECTION 1 — FLIGHT INFORMATION
#     # =========================================================================
#     st.markdown('<div class="card"><div class="card-title">🗺️ Flight Information</div>',
#                 unsafe_allow_html=True)

#     col1, col2, col3 = st.columns(3)
#     with col1:
#         source_city = st.selectbox("📍 Source City", CITIES, index=2)
#     with col2:
#         dest_opts        = [c for c in CITIES if c != source_city]
#         destination_city = st.selectbox("📍 Destination City", dest_opts)
#     with col3:
#         airline = st.selectbox("🛫 Airline", AIRLINES)

#     col1, col2 = st.columns(2)
#     with col1:
#         departure_time = st.selectbox("🕐 Departure Time", TIME_SLOTS)
#     with col2:
#         stops_display = st.selectbox("🛑 Number of Stops",
#                                      list(STOPS_DISPLAY.keys()))
#         stops = STOPS_DISPLAY[stops_display]

#     st.markdown('</div>', unsafe_allow_html=True)

#     # =========================================================================
#     # SECTION 2 — PASSENGER INFORMATION
#     # =========================================================================
#     st.markdown('<div class="card"><div class="card-title">👤 Passenger Details</div>',
#                 unsafe_allow_html=True)

#     col1, col2 = st.columns(2)
#     with col1:
#         travel_class   = st.selectbox("💺 Travel Class", CLASS_OPTIONS)
#     with col2:
#         holiday_season = st.selectbox("🎉 Holiday Season", HOLIDAY_OPT)

#     st.markdown('</div>', unsafe_allow_html=True)

#     # ── Predict button ────────────────────────────────────────────────────────
#     st.markdown("<div style='margin-top:0.5rem;'>", unsafe_allow_html=True)
#     predict_clicked = st.button("🔍  Predict Flight Price")
#     st.markdown("</div>", unsafe_allow_html=True)

#     if predict_clicked:

#         if source_city == destination_city:
#             st.error("Source city and destination city cannot be the same.")
#             st.stop()

#         # ── Auto-derive removed inputs ────────────────────────────────────────
#         (flight_distance, duration, airline_rating,
#          seat_availability, days_left, arrival_time) = auto_derive(
#             source_city, destination_city, stops, airline,
#             travel_class, holiday_season
#         )

#         # ── Feature engineering ───────────────────────────────────────────────
#         (journey_type, demand_level, booking_category,
#          premium_airline, speed_kmh, holiday_encoded) = engineer_features(
#             airline, travel_class, stops,
#             seat_availability, days_left,
#             flight_distance, duration,
#             airline_rating, holiday_season
#         )

#         # ── Preprocess & predict ──────────────────────────────────────────────
#         df_input = preprocess(
#             airline, source_city, destination_city,
#             departure_time, arrival_time, stops, travel_class,
#             holiday_encoded, duration, days_left,
#             float(flight_distance), float(seat_availability), airline_rating,
#             journey_type, demand_level, booking_category,
#             premium_airline, speed_kmh, feature_columns
#         )

#         X_scaled   = scaler.transform(df_input)
#         prediction = lr_model.predict(X_scaled)[0]
#         prediction = max(1000.0, prediction)

#         low_price  = round(prediction * 0.92)
#         pred_price = round(prediction)
#         high_price = round(prediction * 1.08)

#         st.markdown("<br>", unsafe_allow_html=True)

#         # =====================================================================
#         # SECTION 3 — PREDICTION RESULT
#         # =====================================================================
#         st.markdown('<div class="card"><div class="card-title">🎯 Prediction Result</div>',
#                     unsafe_allow_html=True)

#         col_main, col_right = st.columns([1.2, 1])

#         with col_main:
#             st.markdown(f"""
#             <div class="price-card">
#                 <div class="price-eyebrow">Predicted Flight Price</div>
#                 <div class="price-main">₹{pred_price:,}</div>
#                 <div class="price-range">
#                     Range &nbsp; ₹{low_price:,} — ₹{high_price:,}
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)

#         with col_right:
#             st.markdown(f"""
#             <div style="display:flex;flex-direction:column;gap:10px;
#                         padding:4px 0;height:100%;">
#                 <div class="stat-box">
#                     <div class="stat-label">Route</div>
#                     <div class="stat-value" style="font-size:0.9rem;">
#                         {source_city} → {destination_city}
#                     </div>
#                 </div>
#                 <div class="stat-box">
#                     <div class="stat-label">Airline</div>
#                     <div class="stat-value" style="font-size:0.9rem;">
#                         {airline.replace("_"," ")}
#                     </div>
#                 </div>
#                 <div class="stat-box">
#                     <div class="stat-label">Class · Stops</div>
#                     <div class="stat-value" style="font-size:0.9rem;">
#                         {travel_class} · {stops_display}
#                     </div>
#                 </div>
#                 <div class="stat-box">
#                     <div class="stat-label">Departure</div>
#                     <div class="stat-value" style="font-size:0.9rem;">
#                         {departure_time.replace("_"," ")}
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)

#         st.markdown('</div>', unsafe_allow_html=True)

#         # =====================================================================
#         # SECTION 4 — PRICE INSIGHTS
#         # =====================================================================
#         st.markdown('<div class="card"><div class="card-title">📊 Price Insights</div>',
#                     unsafe_allow_html=True)

#         # Stat row
#         st.markdown(f"""
#         <div class="stat-grid">
#             <div class="stat-box">
#                 <div class="stat-label">Journey Type</div>
#                 <div class="stat-value">{journey_type.replace("_"," ")}</div>
#             </div>
#             <div class="stat-box">
#                 <div class="stat-label">Demand Level</div>
#                 <div class="stat-value">{demand_level}</div>
#             </div>
#             <div class="stat-box">
#                 <div class="stat-label">Booking Window</div>
#                 <div class="stat-value">{booking_category}</div>
#             </div>
#             <div class="stat-box">
#                 <div class="stat-label">Airline Tier</div>
#                 <div class="stat-value">
#                     {"Premium" if premium_airline else "Budget"}
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#         # Chip badges
#         demand_chip = (
#             "chip-red"   if demand_level == "High"   else
#             "chip-amber" if demand_level == "Medium" else "chip-green"
#         )
#         booking_chip = (
#             "chip-red"   if booking_category == "Last Minute" else
#             "chip-amber" if booking_category == "Early"       else "chip-green"
#         )
#         chips = [
#             (journey_type.replace("_"," "), "chip-blue"),
#             (demand_level + " Demand",      demand_chip),
#             (booking_category,              booking_chip),
#             ("Premium Airline" if premium_airline else "Budget Airline",
#              "chip-purple" if premium_airline else "chip-cyan"),
#             (travel_class,  "chip-blue"),
#             (f"{speed_kmh:.0f} km/h", "chip-cyan"),
#         ]
#         html = '<div class="chip-row">'
#         for label, cls in chips:
#             html += f'<span class="chip {cls}">{label}</span>'
#         html += '</div>'
#         st.markdown(html, unsafe_allow_html=True)

#         # Auto-computed info banner
#         st.markdown(f"""
#         <div class="auto-banner">
#             ℹ️ <strong>Auto-computed values used in prediction:</strong>
#             &nbsp; Distance: <strong>{flight_distance:,} km</strong>
#             &nbsp;·&nbsp; Duration: <strong>{duration:.1f} hrs</strong>
#             &nbsp;·&nbsp; Airline Rating: <strong>{airline_rating}</strong>
#             &nbsp;·&nbsp; Est. Seats: <strong>{seat_availability}</strong>
#             &nbsp;·&nbsp; Booking window: <strong>{days_left} days</strong>
#             &nbsp;·&nbsp; Speed: <strong>{speed_kmh:.0f} km/h</strong>
#         </div>
#         """, unsafe_allow_html=True)

#         st.markdown('</div>', unsafe_allow_html=True)

#         # =====================================================================
#         # PRICE RANGE CHART
#         # =====================================================================
#         st.markdown('<div class="card"><div class="card-title">📈 Price Range Visualization</div>',
#                     unsafe_allow_html=True)
#         st.plotly_chart(price_chart(low_price, pred_price, high_price),
#                         use_container_width=True)
#         st.markdown('</div>', unsafe_allow_html=True)

#         # =====================================================================
#         # SMART TIPS
#         # =====================================================================
#         st.markdown('<div class="card"><div class="card-title">💡 Smart Booking Tips</div>',
#                     unsafe_allow_html=True)
#         render_tips(days_left, seat_availability, travel_class,
#                     premium_airline, demand_level, holiday_season)
#         st.markdown('</div>', unsafe_allow_html=True)

#     # =========================================================================
#     # FOOTER
#     # =========================================================================
#     st.markdown("""
#     <div class="footer">
#         Made with ❤️ by <strong>Mohammed Nihal</strong>
#         &nbsp;·&nbsp; Machine Learning Project
#         &nbsp;·&nbsp; <a href="https://github.com" target="_blank">🐙 GitHub</a>
#         &nbsp;·&nbsp; <a href="https://linkedin.com" target="_blank">💼 LinkedIn</a>
#         <br>
#         <span style="font-size:0.73rem;opacity:0.55;">
#             Built with Streamlit · Scikit-learn · Plotly &nbsp;·&nbsp; © 2025
#         </span>
#     </div>
#     """, unsafe_allow_html=True)


# # =============================================================================
# # ENTRY POINT
# # =============================================================================
# if __name__ == "__main__":
#     main()



import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="FlightAI — Price Predictor",
    page_icon="🛩️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# DARK THEME CSS
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background-color: #080C14;
    color: #CBD5E1;
}

/* ── Remove default padding ── */
.block-container {
    padding: 1.5rem 2.5rem 4rem;
    max-width: 1180px;
}

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D1117 !important;
    border-right: 1px solid #161D2D;
}
[data-testid="stSidebar"] * { color: #94A3B8 !important; }
[data-testid="stSidebar"] hr { border-color: #161D2D !important; margin: 14px 0; }
[data-testid="stSidebar"] a { color: #818CF8 !important; text-decoration: none; }
[data-testid="stSidebar"] a:hover { color: #A5B4FC !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #0D1117 !important;
    border: 1px solid #1E293B !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: #4F46E5 !important;
}

/* ── Number input ── */
[data-testid="stNumberInput"] label {
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
}
[data-testid="stNumberInput"] input {
    background: #0D1117 !important;
    border: 1px solid #1E293B !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 2px rgba(79,70,229,0.2) !important;
}

/* ── Predict button ── */
div[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 0.85rem 2rem;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 4px 20px rgba(79,70,229,0.4);
    transition: all 0.25s ease;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 8px 30px rgba(79,70,229,0.6);
    transform: translateY(-2px);
}

/* ── Alert ── */
div[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0D1117; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4F46E5; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# LOAD MODELS
# =============================================================================
@st.cache_resource(show_spinner=False)
def load_models():
    lr      = joblib.load("models/linear_regression_model.pkl")
    scaler  = joblib.load("models/standard_scaler.pkl")
    columns = joblib.load("models/feature_columns.pkl")
    return lr, scaler, columns

try:
    lr_model, scaler, feature_columns = load_models()
except FileNotFoundError as e:
    st.error(f"**Model files not found.** Make sure the `models/` folder is beside `app.py`.\n\n`{e}`")
    st.stop()


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:

    # ── Logo ──
    st.markdown("""
    <div style="padding:1rem 0 0.4rem;display:flex;align-items:center;gap:12px;">
        <div style="width:44px;height:44px;border-radius:12px;
                    background:linear-gradient(135deg,#4F46E5,#7C3AED);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.4rem;flex-shrink:0;">🛩️</div>
        <div>
            <div style="font-size:1.05rem;font-weight:800;color:#E2E8F0;">FlightAI</div>
            <div style="font-size:0.65rem;letter-spacing:0.1em;color:#334155;
                        text-transform:uppercase;">Price Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── About ──
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4F46E5;margin-bottom:8px;">
        About
    </div>
    <div style="font-size:0.8rem;color:#475569;line-height:1.75;">
        Predicts Indian domestic flight fares using
        <strong style="color:#818CF8;">Linear Regression</strong>
        trained on 300,000+ real booking records.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Model stats ──
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4F46E5;margin-bottom:10px;">
        Model Info
    </div>
    """, unsafe_allow_html=True)

    for label, value in [
        ("Algorithm",      "Linear Regression"),
        ("Training rows",  "240,174 flights"),
        ("R² Score",       "0.937"),
        ("MAE",            "₹ 3,708"),
        ("Features",       "45 columns"),
    ]:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:7px 0;border-bottom:1px solid #161D2D;">
            <span style="font-size:0.78rem;color:#475569;">{label}</span>
            <span style="font-size:0.78rem;font-weight:700;color:#818CF8;">{value}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Tech stack ──
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4F46E5;margin-bottom:8px;">
        Tech Stack
    </div>
    """, unsafe_allow_html=True)
    for icon, tech in [
        ("🐍", "Python 3.11"),
        ("🐼", "Pandas · NumPy"),
        ("🤖", "Scikit-learn"),
        ("💾", "Joblib"),
        ("📊", "Plotly"),
        ("🌐", "Streamlit"),
    ]:
        st.markdown(f"""
        <div style="font-size:0.79rem;padding:4px 0;color:#334155;">
            {icon} &nbsp; {tech}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Author ──
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4F46E5;margin-bottom:10px;">
        Author
    </div>
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
        <div style="width:40px;height:40px;border-radius:50%;flex-shrink:0;
                    background:linear-gradient(135deg,#4F46E5,#7C3AED);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1rem;font-weight:800;color:white;">M</div>
        <div>
            <div style="font-size:0.88rem;font-weight:700;color:#E2E8F0;">Mohammed Nihal</div>
            <div style="font-size:0.7rem;color:#334155;">Data Analyst Intern</div>
        </div>
    </div>
    <div style="display:flex;gap:8px;">
        <a href="https://github.com" target="_blank"
           style="flex:1;text-align:center;background:#0D1117;
                  border:1px solid #1E293B;border-radius:8px;padding:7px 4px;
                  font-size:0.76rem;font-weight:700;color:#94A3B8;">
            🐙 GitHub
        </a>
        <a href="https://linkedin.com" target="_blank"
           style="flex:1;text-align:center;background:#0D1117;
                  border:1px solid #1E293B;border-radius:8px;padding:7px 4px;
                  font-size:0.76rem;font-weight:700;color:#94A3B8;">
            💼 LinkedIn
        </a>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# HERO BANNER
# =============================================================================

st.markdown("""
<div style="background:#0D1117;border:1px solid #1E293B;border-radius:20px;
            padding:2.5rem 3rem;margin-bottom:1.8rem;">
    <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.2em;
                text-transform:uppercase;color:#4F46E5;margin-bottom:0.7rem;">
        AI-Powered Fare Intelligence
    </div>
    <div style="font-size:2.2rem;font-weight:800;color:#F1F5F9;
                letter-spacing:-0.8px;line-height:1.2;margin-bottom:0.6rem;">
        Predict Your Flight Price
    </div>
    <div style="font-size:0.88rem;color:#475569;line-height:1.7;
                margin-bottom:1.2rem;">
        Machine learning model trained on 300,000+ Indian domestic flights.
        Enter your journey details and get a precise fare estimate in seconds.
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# HELPER — section card wrapper
# =============================================================================
def card_start(icon, title):
    st.markdown(f"""
    <div style="background:#0D1117;border:1px solid #1E293B;border-radius:16px;
                padding:1.6rem 1.8rem 1.2rem;margin-bottom:1.2rem;
                position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:1px;
                    background:linear-gradient(90deg,transparent,rgba(79,70,229,0.5),transparent);">
        </div>
        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;
                    text-transform:uppercase;color:#4F46E5;margin-bottom:1.1rem;
                    display:flex;align-items:center;gap:7px;">
            {icon} &nbsp; {title}
            <span style="flex:1;height:1px;
                         background:linear-gradient(90deg,#1E293B,transparent);
                         margin-left:6px;display:inline-block;"></span>
        </div>
    """, unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# SECTION 1 — FLIGHT INFORMATION
# =============================================================================
card_start("🗺️", "Flight Information")

c1, c2, c3 = st.columns(3)
with c1:
    airline = st.selectbox("Airline", [
        "AirAsia", "Air_India", "GO_FIRST", "Indigo", "SpiceJet", "Vistara"
    ])
with c2:
    source_city = st.selectbox("Source City", [
        "Bangalore", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai"
    ])
with c3:
    destination_city = st.selectbox("Destination City", [
        "Bangalore", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai"
    ])

c1, c2, c3 = st.columns(3)
with c1:
    departure_time = st.selectbox("Departure Time", [
        "Early_Morning", "Morning", "Afternoon", "Evening", "Night", "Late_Night"
    ])
with c2:
    arrival_time = st.selectbox("Arrival Time", [
        "Early_Morning", "Morning", "Afternoon", "Evening", "Night", "Late_Night"
    ])
with c3:
    stops = st.selectbox("Stops", ["zero", "one", "two_or_more"])

card_end()


# =============================================================================
# SECTION 2 — PASSENGER & BOOKING
# =============================================================================
card_start("👤", "Passenger & Booking Details")

c1, c2, c3 = st.columns(3)
with c1:
    travel_class   = st.selectbox("Class", ["Economy", "Business"])
    holiday_season = st.selectbox("Holiday Season", ["No", "Yes"])
with c2:
    duration  = st.number_input("Duration (hours)",       min_value=0.5,  max_value=49.0,  value=2.5,  step=0.5)
    days_left = st.number_input("Days Left to Departure", min_value=1,    max_value=49,    value=15,   step=1)
with c3:
    flight_distance   = st.number_input("Flight Distance (km)", min_value=100,  max_value=2500, value=1150, step=50)
    seat_availability = st.number_input("Seat Availability",    min_value=0,    max_value=139,  value=50,   step=1)

c1, _, _ = st.columns(3)
with c1:
    airline_rating = st.number_input("Airline Rating", min_value=1.0, max_value=5.0, value=4.5, step=0.1)

card_end()


# =============================================================================
# PREDICT BUTTON
# =============================================================================
predict = st.button("🔍  Predict Flight Price")


# =============================================================================
# PREDICTION LOGIC
# =============================================================================
if predict:

    if source_city == destination_city:
        st.error("⚠️ Source and destination city cannot be the same.")
        st.stop()

    # =========================
    # FEATURE ENGINEERING
    # =========================

    # journey_type
    stop_map     = {"zero": "Direct", "one": "OneStop", "two_or_more": "MultiStop"}
    journey_type = travel_class + "_" + stop_map[stops]

    # demand_level
    if seat_availability <= 30 and days_left <= 7:
        demand_level = "High"
    elif seat_availability <= 70 and days_left <= 30:
        demand_level = "Medium"
    else:
        demand_level = "Low"

    # booking_category
    if days_left <= 7:
        booking_category = "Last Minute"
    elif days_left <= 30:
        booking_category = "Early"
    else:
        booking_category = "Advance"

    # premium_airline
    premium_airline = int(airline_rating >= 4.5)

    # speed_kmh
    speed_kmh = round(flight_distance / duration, 2)

    # holiday_season encode
    holiday_encoded = 1 if holiday_season == "Yes" else 0

    # =========================
    # BUILD INPUT ROW
    # =========================
    row = {
        "duration":           duration,
        "days_left":          days_left,
        "flight_distance_km": flight_distance,
        "seat_availability":  int(seat_availability),
        "holiday_season":     holiday_encoded,
        "airline_rating":     airline_rating,
        "premium_airline":    premium_airline,
        "speed_kmh":          speed_kmh,
        "airline":            airline,
        "source_city":        source_city,
        "departure_time":     departure_time,
        "stops":              stops,
        "arrival_time":       arrival_time,
        "destination_city":   destination_city,
        "class":              travel_class,
        "journey_type":       journey_type,
        "demand_level":       demand_level,
        "booking_category":   booking_category,
    }

    # =========================
    # ONE HOT ENCODING
    # =========================
    df_input = pd.DataFrame([row])
    df_input = pd.get_dummies(
        df_input,
        columns=[
            "airline", "source_city", "departure_time", "stops",
            "arrival_time", "destination_city", "class",
            "journey_type", "demand_level", "booking_category"
        ],
        drop_first=True,
        dtype=int
    )

    # =========================
    # ALIGN COLUMNS
    # =========================
    for col in feature_columns:
        if col not in df_input.columns:
            df_input[col] = 0
    df_input = df_input[feature_columns]

    # =========================
    # SCALE AND PREDICT
    # =========================
    X_scaled   = scaler.transform(df_input)
    prediction = lr_model.predict(X_scaled)[0]
    prediction = max(1000, round(prediction, 2))

    low_price  = round(prediction * 0.92, 2)
    high_price = round(prediction * 1.08, 2)

    st.markdown("<br>", unsafe_allow_html=True)

    # =================================================================
    # RESULT LAYOUT — left price card | right insight panel
    # =================================================================
    col_price, col_insight = st.columns([1, 1], gap="large")

    # ── Left: Price card ──────────────────────────────────────────
    with col_price:
        card_start("🎯", "Prediction Result")

        # Big price
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0F0D2A,#13103A);
                    border:1px solid #2D1F6E;border-radius:16px;
                    padding:2.4rem 2rem;text-align:center;
                    position:relative;overflow:hidden;margin-bottom:1rem;">
            <div style="position:absolute;top:0;left:0;right:0;bottom:0;
                        background:radial-gradient(ellipse at top,
                        rgba(99,102,241,0.1),transparent 60%);
                        pointer-events:none;"></div>
            <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;
                        text-transform:uppercase;color:#6366F1;margin-bottom:0.6rem;">
                Predicted Flight Fare
            </div>
            <div style="font-size:3.8rem;font-weight:800;letter-spacing:-2px;
                        line-height:1;background:linear-gradient(135deg,#E2E8F0,#A78BFA);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text;">
                ₹{int(prediction):,}
            </div>
            <div style="font-size:0.8rem;color:#334155;margin-top:0.8rem;
                        font-family:'JetBrains Mono',monospace;">
                ₹{int(low_price):,} &nbsp;——&nbsp; ₹{int(high_price):,}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Flight summary rows
        summary = [
            ("Route",       f"{source_city} → {destination_city}"),
            ("Airline",     airline.replace("_", " ")),
            ("Class",       travel_class),
            ("Stops",       stops.replace("_", " ")),
            ("Departure",   departure_time.replace("_", " ")),
            ("Arrival",     arrival_time.replace("_", " ")),
            ("Holiday",     holiday_season),
            ("Duration",    f"{duration} hrs"),
            ("Distance",    f"{int(flight_distance):,} km"),
        ]
        for k, v in summary:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;
                        padding:8px 0;border-bottom:1px solid #111827;">
                <div style="width:6px;height:6px;border-radius:50%;
                            background:#4F46E5;flex-shrink:0;"></div>
                <div style="font-size:0.75rem;color:#334155;
                            width:90px;flex-shrink:0;">{k}</div>
                <div style="font-size:0.85rem;font-weight:600;
                            color:#CBD5E1;">{v}</div>
            </div>
            """, unsafe_allow_html=True)

        card_end()

    # ── Right: Insight panel ──────────────────────────────────────
    with col_insight:
        card_start("📊", "Price Insights")

        # ── 4 metric tiles ──
        dm_col = ("#FCA5A5" if demand_level == "High"
                  else "#FCD34D" if demand_level == "Medium"
                  else "#86EFAC")
        bk_col = ("#FCA5A5" if booking_category == "Last Minute"
                  else "#FCD34D" if booking_category == "Early"
                  else "#86EFAC")
        tr_col = "#C4B5FD" if premium_airline else "#93C5FD"

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;
                    margin-bottom:12px;">
            <div style="background:#080C14;border:1px solid #1E293B;
                        border-radius:12px;padding:1rem;text-align:center;
                        position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:20%;right:20%;height:1px;
                            background:linear-gradient(90deg,transparent,#4F46E5,transparent);"></div>
                <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
                            text-transform:uppercase;color:#334155;margin-bottom:5px;">
                    Journey Type
                </div>
                <div style="font-size:0.88rem;font-weight:700;color:#C4B5FD;">
                    {journey_type.replace("_"," ")}
                </div>
            </div>
            <div style="background:#080C14;border:1px solid #1E293B;
                        border-radius:12px;padding:1rem;text-align:center;
                        position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:20%;right:20%;height:1px;
                            background:linear-gradient(90deg,transparent,#4F46E5,transparent);"></div>
                <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
                            text-transform:uppercase;color:#334155;margin-bottom:5px;">
                    Demand Level
                </div>
                <div style="font-size:0.88rem;font-weight:700;color:{dm_col};">
                    {demand_level}
                </div>
            </div>
            <div style="background:#080C14;border:1px solid #1E293B;
                        border-radius:12px;padding:1rem;text-align:center;
                        position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:20%;right:20%;height:1px;
                            background:linear-gradient(90deg,transparent,#4F46E5,transparent);"></div>
                <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
                            text-transform:uppercase;color:#334155;margin-bottom:5px;">
                    Booking Window
                </div>
                <div style="font-size:0.88rem;font-weight:700;color:{bk_col};">
                    {booking_category}
                </div>
            </div>
            <div style="background:#080C14;border:1px solid #1E293B;
                        border-radius:12px;padding:1rem;text-align:center;
                        position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:20%;right:20%;height:1px;
                            background:linear-gradient(90deg,transparent,#4F46E5,transparent);"></div>
                <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
                            text-transform:uppercase;color:#334155;margin-bottom:5px;">
                    Airline Tier
                </div>
                <div style="font-size:0.88rem;font-weight:700;color:{tr_col};">
                    {"Premium ✦" if premium_airline else "Budget"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tag badges ──
        tags = [
            (journey_type.replace("_"," "), "rgba(79,70,229,0.15)", "#818CF8", "rgba(79,70,229,0.3)"),
            (f"{demand_level} Demand",
             "rgba(239,68,68,0.12)" if demand_level=="High" else "rgba(245,158,11,0.12)" if demand_level=="Medium" else "rgba(16,185,129,0.12)",
             "#FCA5A5" if demand_level=="High" else "#FCD34D" if demand_level=="Medium" else "#86EFAC",
             "rgba(239,68,68,0.25)" if demand_level=="High" else "rgba(245,158,11,0.25)" if demand_level=="Medium" else "rgba(16,185,129,0.25)"),
            (booking_category,
             "rgba(239,68,68,0.12)" if booking_category=="Last Minute" else "rgba(245,158,11,0.12)" if booking_category=="Early" else "rgba(16,185,129,0.12)",
             "#FCA5A5" if booking_category=="Last Minute" else "#FCD34D" if booking_category=="Early" else "#86EFAC",
             "rgba(239,68,68,0.25)" if booking_category=="Last Minute" else "rgba(245,158,11,0.25)" if booking_category=="Early" else "rgba(16,185,129,0.25)"),
            ("Premium" if premium_airline else "Budget",
             "rgba(167,139,250,0.12)", "#C4B5FD", "rgba(167,139,250,0.3)"),
            (f"{speed_kmh} km/h",
             "rgba(59,130,246,0.12)", "#93C5FD", "rgba(59,130,246,0.25)"),
        ]
        tags_html = '<div style="display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px;">'
        for label, bg, fg, border in tags:
            tags_html += f"""
            <span style="font-size:0.74rem;font-weight:600;padding:5px 12px;
                         border-radius:6px;background:{bg};color:{fg};
                         border:1px solid {border};">{label}</span>"""
        tags_html += "</div>"
        st.markdown(tags_html, unsafe_allow_html=True)

        # ── Plotly bar chart ──
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Low Estimate", "Predicted Price", "High Estimate"],
            y=[low_price, prediction, high_price],
            marker=dict(
                color=["#312E81", "#4F46E5", "#7C3AED"],
                line=dict(color=["#4338CA","#4338CA","#6D28D9"], width=1),
                cornerradius=8,
            ),
            text=[f"₹{int(v):,}" for v in [low_price, prediction, high_price]],
            textposition="outside",
            textfont=dict(size=12, color="#818CF8",
                          family="JetBrains Mono"),
            width=0.4,
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
        ))
        fig.add_hline(
            y=prediction, line_dash="dot",
            line_color="#818CF8", line_width=1.2,
        )
        fig.update_layout(
            plot_bgcolor="#080C14",
            paper_bgcolor="#080C14",
            xaxis=dict(showgrid=False, tickfont=dict(color="#334155", size=11),
                       linecolor="#1E293B"),
            yaxis=dict(showgrid=True, gridcolor="#0D1117",
                       tickprefix="₹", tickformat=",",
                       tickfont=dict(color="#334155", size=10,
                                     family="JetBrains Mono"),
                       range=[0, high_price * 1.28], linecolor="#1E293B"),
            margin=dict(t=20, b=10, l=10, r=10),
            height=280,
            showlegend=False,
            bargap=0.5,
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

        card_end()

    # =================================================================
    # SMART TIPS
    # =================================================================
    card_start("💡", "Smart Booking Tips")

    tips = []

    if demand_level == "High":
        tips.append(("🔴", "<strong style='color:#F1F5F9;'>High demand detected.</strong> Seats are scarce and departure is near — prices are at their peak."))
    elif demand_level == "Medium":
        tips.append(("🟡", "<strong style='color:#F1F5F9;'>Moderate demand.</strong> Price may rise as departure approaches."))
    else:
        tips.append(("🟢", "<strong style='color:#F1F5F9;'>Low demand window.</strong> Good availability — one of the cheaper pricing windows."))

    if days_left <= 7:
        tips.append(("⚠️", "<strong style='color:#F1F5F9;'>Last-minute booking!</strong> Fares are typically 37% higher within 7 days of departure."))

    if seat_availability <= 30 and days_left <= 7:
        tips.append(("🪑", f"<strong style='color:#F1F5F9;'>Very few seats left ({int(seat_availability)}).</strong> Price will likely increase further."))

    if travel_class == "Business":
        tips.append(("💼", "<strong style='color:#F1F5F9;'>Business class selected.</strong> Business fares average 8× more than Economy on Indian domestic routes."))

    if premium_airline:
        tips.append(("⭐", "<strong style='color:#F1F5F9;'>Premium airline.</strong> Vistara and Air India charge ~5× more than budget carriers on the same route."))

    if not premium_airline and travel_class == "Economy":
        tips.append(("💡", "<strong style='color:#F1F5F9;'>Best value combo.</strong> Economy on a budget carrier gives the lowest possible fare on any route."))

    if holiday_season == "Yes":
        tips.append(("🎉", "<strong style='color:#F1F5F9;'>Holiday season.</strong> Elevated demand during holidays typically pushes fares higher."))

    for icon, text in tips:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:12px;
                    padding:10px 0;border-bottom:1px solid #0D1117;
                    font-size:0.84rem;color:#475569;line-height:1.65;">
            <span style="font-size:1.1rem;flex-shrink:0;">{icon}</span>
            <span>{text}</span>
        </div>
        """, unsafe_allow_html=True)

    card_end()


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("""
<div style="text-align:center;padding:2.5rem 1rem 1rem;
            margin-top:1rem;border-top:1px solid #111827;
            color:#1E293B;font-size:0.78rem;line-height:2;">
    <div style="font-size:1.3rem;font-weight:800;letter-spacing:-0.5px;
                background:linear-gradient(135deg,#4F46E5,#7C3AED);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;margin-bottom:4px;">FlightAI</div>
    Made with ❤️ by
    <strong style="color:#818CF8;">Mohammed Nihal</strong>
    &nbsp;·&nbsp; Machine Learning Project &nbsp;·&nbsp;
    <a href="https://github.com" target="_blank"
       style="color:#4F46E5;text-decoration:none;font-weight:600;">GitHub</a>
    &nbsp;·&nbsp;
    <a href="https://linkedin.com" target="_blank"
       style="color:#4F46E5;text-decoration:none;font-weight:600;">LinkedIn</a>
    <br>
    <span style="font-size:0.7rem;color:#0F172A;">
        Streamlit · Scikit-learn · Plotly · Python &nbsp;·&nbsp; © 2025
    </span>
</div>
""", unsafe_allow_html=True)