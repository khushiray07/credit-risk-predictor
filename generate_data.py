import pandas as pd
import numpy as np

data = []

cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata']
professions = ['Engineer', 'Freelancer', 'Teacher', 'Driver', 'Manager']

for i in range(1, 501):
    entry = {
        "user_id": i,
        "name": f"User{i}",
        "email": f"user{i}@example.com",
        "phone": f"98765{str(i).zfill(5)}",
        "age": np.random.randint(20, 50),
        "city": np.random.choice(cities),
        "profession": np.random.choice(professions),
        "social_score": round(np.random.uniform(0, 1), 2),
        "app_usage_score": round(np.random.uniform(0, 1), 2),
        "bill_payment_score": round(np.random.uniform(0, 1), 2),
        "recharge_pattern_score": round(np.random.uniform(0, 1), 2),
        "is_defaulter": np.random.choice([0, 1], p=[0.75, 0.25])
    }
    data.append(entry)

df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)
print("✅ data.csv created successfully.")
