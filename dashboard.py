import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Credit Risk Dashboard", layout="centered")

API_URL = "https://credit-risk-predictor-h2hs.onrender.com"

st.title("💳 Credit Risk Predictor")
st.markdown("Check user's **probability of default** using their ID or Email.")

# --- User Search Section ---
option = st.radio("Search by:", ["User ID", "Email"])

if option == "User ID":
    user_id = st.number_input("Enter User ID", min_value=1, max_value=500, step=1)
    if st.button("Predict Default Risk"):
        try:
            res = requests.get(f"{API_URL}/predict?user_id={user_id}")
            res.raise_for_status()
            data = res.json()
            prob = data["probability_of_default"]
            is_defaulter = data.get("is_defaulter", None)

            st.success(f"User: {data['name']}")
            st.metric("Probability of Default", f"{prob * 100:.2f}%")

            # Risk label
            if prob < 0.3:
                st.success("✅ Risk Level: Low")
            elif prob < 0.7:
                st.warning("⚠️ Risk Level: Medium")
            else:
                st.error("❌ Risk Level: High")

            # Actual status
            if is_defaulter is not None:
                if is_defaulter:
                    st.error("🚨 Actual Status: Defaulter")
                else:
                    st.success("✔️ Actual Status: Non-Defaulter")
        except requests.exceptions.RequestException:
            st.error("🚫 Failed to fetch user data. Please check the backend connection.")
else:
    email = st.text_input("Enter Email", value="user10@example.com")
    if st.button("Search User by Email"):
        try:
            res = requests.get(f"{API_URL}/search_user?email={email}")
            res.raise_for_status()
            st.json(res.json())
        except requests.exceptions.RequestException:
            st.error("🚫 Failed to fetch user by email.")

# --- Charts Section ---
st.markdown("---")
st.subheader("📊 Risk Distribution")

# Pie Chart from /risk-distribution
try:
    dist_res = requests.get(f"{API_URL}/risk-distribution")
    dist_res.raise_for_status()
    dist = dist_res.json()
    labels = ["Low Risk", "Medium Risk", "High Risk"]
    values = [dist["low_risk_users"], dist["medium_risk_users"], dist["high_risk_users"]]
    colors = ["#28a745", "#ffc107", "#dc3545"]

    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)
except requests.exceptions.RequestException:
    st.error("🚫 Failed to load risk distribution.")

# --- User Risk Bar Chart ---
st.subheader("📈 Default Probability Across Users")

try:
    risk_res = requests.get(f"{API_URL}/all-users-risk")
    risk_res.raise_for_status()
    users_data = pd.DataFrame(risk_res.json())

    if not users_data.empty:
        fig2, ax2 = plt.subplots(figsize=(12, 4))
        sns.barplot(data=users_data, x="name", y="probability_of_default", palette="Blues_d", ax=ax2)
        ax2.set_xticklabels(users_data["name"], rotation=90)
        ax2.set_ylabel("Probability of Default")
        ax2.set_xlabel("User Name")
        ax2.set_ylim(0, 1)
        ax2.grid(True)
        st.pyplot(fig2)
    else:
        st.warning("No user data available.")
except requests.exceptions.RequestException:
    st.error("🚫 Failed to load user risk data.")

# --- Export Button ---
st.subheader("📅 Download Predictions as CSV")
if st.button("Export CSV"):
    try:
        csv_response = requests.get(f"{API_URL}/export-predictions")
        csv_response.raise_for_status()
        st.download_button(
            label="📄 Download CSV",
            data=csv_response.content,
            file_name="credit_predictions.csv",
            mime="text/csv"
        )
    except requests.exceptions.RequestException:
        st.error("🚫 Failed to fetch predictions for export.")
