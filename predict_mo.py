import pandas as pd
import joblib

# === Load model and vectorizer ===
model = joblib.load("../models/trained_model.pkl")

# === Load processed data ===
df = pd.read_pickle("../data/processed_data.pkl")

# === Select the same features used in training ===
features = ["CrimeType", "WeaponUsed_x", "SeverityScore", "IsGangRelated"]

# Remove rows with missing feature values
df = df.dropna(subset=features)

# === Prepare input data ===
X = df[features]

# === Predict Modus Operandi Category ===
predictions = model.predict(X)

# === Save results to CSV ===
df["PredictedMOCategory"] = predictions
df.to_csv("../data/mo_predictions.csv", index=False)

print("✅ Predictions completed! Results saved to: ../data/mo_predictions.csv")
