import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# === Load the processed dataset ===
data_path = "data/processed_data.pkl"
df = pd.read_pickle(data_path)

# === Define target and features ===
target = "MOCategory"
features = ["CrimeType", "WeaponUsed_x", "SeverityScore", "IsGangRelated"]

# Drop any rows with missing data in selected columns
df = df.dropna(subset=[target] + features)

X = df[features]
y = df[target]

# === Define preprocessing ===
categorical_features = ["CrimeType", "WeaponUsed_x", "IsGangRelated"]
numerical_features = ["SeverityScore"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
    ],
    remainder="passthrough"
)

# === Build and Train the Pipeline ===
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

# === Save the model and vectorizer ===
joblib.dump(pipeline, "models/trained_model.pkl")
joblib.dump(preprocessor.named_transformers_["cat"], "models/vectorizer.pkl")

print("✅ Model trained and saved successfully.")
