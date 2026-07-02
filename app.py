
import streamlit as st
import pandas as pd
import numpy as np
import joblib

# =========================
# TITLE
# =========================
st.title("✈️ Flight Price Prediction")

# =========================
# LOAD MODELS
# =========================
lr_model        = joblib.load("models/linear_regression_model.pkl")
scaler          = joblib.load("models/standard_scaler.pkl")
feature_columns = joblib.load("models/feature_columns.pkl")

# =========================
# INPUTS
# =========================
airline = st.selectbox("Airline", [
    "AirAsia", "Air_India", "GO_FIRST", "Indigo", "SpiceJet", "Vistara"
])

source_city = st.selectbox("Source City", [
    "Bangalore", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai"
])

destination_city = st.selectbox("Destination City", [
    "Bangalore", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai"
])

departure_time = st.selectbox("Departure Time", [
    "Early_Morning", "Morning", "Afternoon", "Evening", "Night", "Late_Night"
])

arrival_time = st.selectbox("Arrival Time", [
    "Early_Morning", "Morning", "Afternoon", "Evening", "Night", "Late_Night"
])

stops = st.selectbox("Stops", [
    "zero", "one", "two_or_more"
])

travel_class = st.selectbox("Class", [
    "Economy", "Business"
])

holiday_season = st.selectbox("Holiday Season", [
    "No", "Yes"
])

duration          = st.number_input("Duration (hours)", min_value=0.5,  max_value=49.0,  value=2.5)
days_left         = st.number_input("Days Left to Departure", min_value=1, max_value=49, value=15)
flight_distance   = st.number_input("Flight Distance (km)", min_value=100, max_value=2500, value=1150)
seat_availability = st.number_input("Seat Availability", min_value=0, max_value=139, value=50)
airline_rating    = st.number_input("Airline Rating", min_value=1.0, max_value=5.0, value=4.5)

# =========================
# PREDICT BUTTON
# =========================
if st.button("Predict Price"):

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

    # =========================
    # RESULT
    # =========================
    st.subheader("Prediction Result")
    st.write(f"Predicted Flight Price : ₹{prediction:,.2f}")
    st.write(f"Journey Type           : {journey_type}")
    st.write(f"Demand Level           : {demand_level}")
    st.write(f"Booking Category       : {booking_category}")
    st.write(f"Premium Airline        : {'Yes' if premium_airline else 'No'}")

    # =========================
    # PRICE RANGE
    # =========================
    low_price  = round(prediction * 0.92, 2)
    high_price = round(prediction * 1.08, 2)

    st.info(f"💰 Expected Price Range: ₹{low_price:,.2f} — ₹{high_price:,.2f}")

    # =========================
    # TIPS
    # =========================
    if days_left <= 7:
        st.warning("⚠️ Last-minute booking! Prices are typically 37% higher in the final 7 days.")

    if seat_availability <= 30 and days_left <= 7:
        st.error("🔴 High demand flight — very few seats left close to departure.")

    if travel_class == "Business":
        st.info("💺 Business class is on average 8× more expensive than Economy.")

    if premium_airline:
        st.info("⭐ Premium airline (Vistara / Air India) — fares are 5× higher than budget carriers.")


