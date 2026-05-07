# train_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# -----------------------
# 1. Generate synthetic dataset with rules
# -----------------------
np.random.seed(42)
n = 500

# Features
ndvi = np.random.uniform(0.2, 0.9, n)          # NDVI (crop health index)
temp = np.random.uniform(20, 40, n)            # Temperature (°C)
humidity = np.random.uniform(20, 90, n)        # Humidity (%)
soil_moisture = np.random.uniform(5, 40, n)    # Soil moisture

# Labels: Healthy = 1, At Risk = 0
labels = []
for i in range(n):
    if ndvi[i] > 0.6 and soil_moisture[i] > 20 and 22 < temp[i] < 35 and humidity[i] > 45:
        labels.append(1)  # Healthy
    else:
        labels.append(0)  # At Risk

# -----------------------
# 2. Train Random Forest model
# -----------------------
X = np.column_stack((ndvi, soil_moisture, temp, humidity))
y = np.array(labels)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# -----------------------
# 3. Save model
# -----------------------
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained successfully and saved as model.pkl")
