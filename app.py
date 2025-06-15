from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta

app = FastAPI()

CSV_PATH = "data.csv"
MODEL_PATH = "credit_model.pkl"
EXPORT_PATH = "predictions.csv"
CSV_EXPIRY_MINUTES = 10

# Load dataset and model safely
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"'{CSV_PATH}' not found. Please upload it to your Render repo.")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"'{MODEL_PATH}' not found. Please upload it to your Render repo.")

df = pd.read_csv(CSV_PATH)
model = joblib.load(MODEL_PATH)

# Compute probability of default
def calculate_default_prob(row):
    features = [[
        row["social_score"],
        row["app_usage_score"],
        row["bill_payment_score"],
        row["recharge_pattern_score"]
    ]]
    return model.predict_proba(features)[0][1]

df["probability_of_default"] = df.apply(calculate_default_prob, axis=1)

@app.get("/")
def home():
    return {"message": "🚀 Credit Risk API is live!"}

@app.get("/predict")
def predict(user_id: int):
    user = df[df["user_id"] == user_id]
    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")
    
    probability = user["probability_of_default"].values[0]
    return {
        "user_id": int(user["user_id"]),
        "name": user["name"].values[0],
        "probability_of_default": round(probability, 2),
        "is_defaulter": bool(user["is_defaulter"].values[0])
    }

@app.get("/search_user")
def search_user(email: str):
    user = df[df["email"] == email]
    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.to_dict(orient="records")[0]

@app.get("/risk-distribution")
def risk_distribution():
    low = sum(df["probability_of_default"] < 0.3)
    medium = sum((df["probability_of_default"] >= 0.3) & (df["probability_of_default"] < 0.7))
    high = sum(df["probability_of_default"] >= 0.7)
    
    return {
        "low_risk_users": int(low),
        "medium_risk_users": int(medium),
        "high_risk_users": int(high)
    }

@app.get("/all-users-risk")
def all_users_risk():
    return df[["user_id", "name", "probability_of_default", "is_defaulter"]].to_dict(orient="records")

@app.get("/export-predictions")
def export_predictions():
    # Use cached file if it's fresh
    if os.path.exists(EXPORT_PATH):
        modified_time = datetime.fromtimestamp(os.path.getmtime(EXPORT_PATH))
        if datetime.now() - modified_time < timedelta(minutes=CSV_EXPIRY_MINUTES):
            return FileResponse(
                path=EXPORT_PATH,
                media_type='text/csv',
                filename="credit_predictions.csv"
            )

    # Recreate the CSV if old or missing
    export_df = df[["user_id", "name", "email", "probability_of_default", "is_defaulter"]]
    export_df.to_csv(EXPORT_PATH, index=False)
    
    return FileResponse(
        path=EXPORT_PATH,
        media_type='text/csv',
        filename="credit_predictions.csv"
    )
