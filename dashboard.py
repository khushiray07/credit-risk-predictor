import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Credit Risk Dashboard", layout="centered")

API_URL = "http://127.0.0.1:8000"

st.title("💳 Credit Risk Predictor")
st.markdown("Check user's **probability of default** using their ID or Email.")

# --- User Search Section ---
option = st.radio("Search by:", ["User ID", "Email"])

if option == "User ID":
    user_id = st.number_input("Enter User ID", min_value=1, max_value=500, step=1)
    if st.button("Predict Default Risk"):
        res = requests.get(f"{API_URL}/predict?user_id={user_id}")
        if res.status_code == 200:
            data = res.json()
            prob = data["probability_of_default"]
            is_defaulter = data.get("is_defaulter", None)

            st.success(f"User: {data['name']}")
            st.metric("Probability of Default", f"{prob * 100:.2f}%")

            # Show risk label
            if prob < 0.3:
                st.success("✅ Risk Level: Low")
            elif prob < 0.7:
                st.warning("⚠️ Risk Level: Medium")
            else:
                st.error("❌ Risk Level: High")

            # Show defaulter status
            if is_defaulter is not None:
                if is_defaulter:
                    st.error("🚨 Actual Status: Defaulter")
                else:
                    st.success("✔️ Actual Status: Non-Defaulter")

        else:
            st.error("User not found.")

else:
    email = st.text_input("Enter Email", value="user10@example.com")
    if st.button("Search User by Email"):
        res = requests.get(f"{API_URL}/search_user?email={email}")
        if res.status_code == 200:
            data = res.json()
            st.json(data)
        else:
            st.error("User not found.")

# --- Charts Section ---
st.markdown("---")
st.subheader("📊 Risk Distribution")

# Pie Chart from /risk-distribution
dist_res = requests.get(f"{API_URL}/risk-distribution")
if dist_res.status_code == 200:
    dist = dist_res.json()
    labels = ["Low Risk", "Medium Risk", "High Risk"]
    values = [dist["low_risk_users"], dist["medium_risk_users"], dist["high_risk_users"]]
    colors = ["#28a745", "#ffc107", "#dc3545"]

    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)
else:
    st.error("Failed to load risk distribution.")

# Line Chart from /all-users-risk
st.subheader("📈 Default Probability Across Users")

risk_res = requests.get(f"{API_URL}/all-users-risk")
if risk_res.status_code == 200:
    users_data = pd.DataFrame(risk_res.json())

    # Multi-user chart (User Name vs Probability)
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    sns.barplot(data=users_data, x="name", y="probability_of_default", palette="Blues_d", ax=ax2)
    ax2.set_xticklabels(users_data["name"], rotation=90)
    ax2.set_ylabel("Probability of Default")
    ax2.set_xlabel("User Name")
    ax2.set_ylim(0, 1)
    ax2.grid(True)
    st.pyplot(fig2)

    # Add Download CSV option
    st.subheader("📅 Download Predictions as CSV")
    if st.button("Export CSV"):
        try:
            csv_response = requests.get(f"{API_URL}/export-predictions")
            if csv_response.status_code == 200:
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_response.content,
                    file_name="credit_predictions.csv",
                    mime="text/csv"
                )
            else:
                st.error("Failed to fetch predictions for export.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.error("Failed to load user risk data.")
