from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import joblib
import os
from utils.neo4j_ingest import fetch_graph_data

# === Setup paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_PUBLIC_PATH = os.path.join(BASE_DIR, "../frontend/public")

# === Init Flask app ===
app = Flask(__name__, static_folder=FRONTEND_PUBLIC_PATH, static_url_path='')

# === Load ML model ===
model = joblib.load("models/trained_model.pkl")

# === Load rule-based + risk data ===
PREDICTIONS_PATH = os.path.join(BASE_DIR, "data", "rule_based_predictions.csv")
RISK_SCORES_PATH = os.path.join(BASE_DIR, "data", "risk_scores.csv")

pred_df = pd.read_csv(PREDICTIONS_PATH)
risk_df = pd.read_csv(RISK_SCORES_PATH)
df = pd.merge(pred_df, risk_df, on="SuspectID", how="left")

# === Static Pages ===
@app.route('/')
def home():
    return send_from_directory(FRONTEND_PUBLIC_PATH, "index.html")

@app.route('/graph')
def graph_page():
    return send_from_directory(FRONTEND_PUBLIC_PATH, "graph.html")

@app.route('/predictions')
def predictions_page():
    return send_from_directory(FRONTEND_PUBLIC_PATH, "predictions.html")

# === API: Neo4j Graph ===
@app.route('/api/graph-data', methods=['GET'])
def api_graph_data():
    try:
        graph_data = fetch_graph_data()
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === API: Suspect Predictions ===
@app.route('/api/predictions', methods=['GET'])
def api_predictions():
    search = request.args.get("search", "")
    filter_crime = request.args.get("crime", "")
    filter_risk = request.args.get("risk", "")

    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df["SuspectID"].str.contains(search, case=False)]
    if filter_crime:
        filtered_df = filtered_df[filtered_df["PredictedCrimeType"] == filter_crime]
    if filter_risk:
        if filter_risk == "High":
            filtered_df = filtered_df[filtered_df["RiskScore"] >= 8]
        elif filter_risk == "Medium":
            filtered_df = filtered_df[(filtered_df["RiskScore"] >= 4) & (filtered_df["RiskScore"] < 8)]
        else:
            filtered_df = filtered_df[filtered_df["RiskScore"] < 4]

    return jsonify(filtered_df.to_dict(orient="records")), 200

@app.route('/api/suspect/<sid>', methods=['GET'])
def api_suspect_view(sid):
    record = df[df['SuspectID'] == sid]
    if record.empty:
        return jsonify({"error": f"Suspect {sid} not found."}), 404
    return jsonify(record.iloc[0].to_dict()), 200

# === API: ML Prediction ===
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()
        df_input = pd.DataFrame([input_data])
        prediction = model.predict(df_input)
        predicted_class = int(prediction[0])

        return jsonify({
            "success": True,
            "PredictedCrimeType": predicted_class
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# === Run the server ===
if __name__ == "__main__":
    app.run(debug=True, port=5001)
