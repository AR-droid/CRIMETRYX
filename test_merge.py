import pandas as pd

# Load both files
df_rule = pd.read_csv("backend/data/rule_based_predictions.csv")
df_risk = pd.read_csv("backend/data/risk_scores.csv")

# Merge on SuspectID
df = pd.merge(df_rule, df_risk, on="SuspectID", how="inner")

# Print sample to verify
print(df.head())
print(f"\nMerged shape: {df.shape}")
