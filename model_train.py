import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Step 1: Load dataset
df = pd.read_csv("data.csv")

# Step 2: Select features and target
X = df[["social_score", "app_usage_score", "bill_payment_score", "recharge_pattern_score"]]
y = df["is_defaulter"]

# Step 3: Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Step 5: Save the model
joblib.dump(model, "credit_model.pkl")

print("✅ Model trained and saved as credit_model.pkl")
