from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Allow React frontend

# Load trained model and dataset
model = joblib.load("model.pkl")
df = pd.read_csv("dummy_npi_data.csv")

# Convert login/logout times
def convert_to_datetime(time_str):
    return datetime.strptime(time_str, "%H:%M")

df["Login Time"] = df["Login Time"].apply(convert_to_datetime)
df["Logout Time"] = df["Logout Time"].apply(convert_to_datetime)

# Extract hours
df["Login Hour"] = df["Login Time"].dt.hour
df["Logout Hour"] = df["Logout Time"].dt.hour

print("Unique Login Hours in Dataset:", df["Login Hour"].unique())
print("Unique Logout Hours in Dataset:", df["Logout Hour"].unique())


@app.route("/predict", methods=["POST"])
def predict():
    """Predict the most likely doctors to attend a survey at the given time."""
    try:
        data = request.json
        print("Received request data:", data)  # Debugging line

        input_hour = int(data.get("hour", "0"))
        input_minute = int(data.get("minute", "0"))
        print(f"Processed Input Hour: {input_hour}, Minute: {input_minute}")  # Debugging line

        # Filter relevant doctors
        relevant_doctors = df[
            (df["Login Hour"] <= input_hour) & (df["Logout Hour"] >= input_hour)
        ].copy()
        print("Relevant Doctors Count:", len(relevant_doctors))  # Debugging line

        if relevant_doctors.empty:
            return jsonify({"error": "No matching doctors found for this time"}), 404
        
        feature_columns = ["Login Hour", "Logout Hour", "Usage Time (mins)", "Count of Survey Attempts"]

        # Ensure missing columns are filled with 0 (default values)
        for col in feature_columns:
            if col not in relevant_doctors:
                relevant_doctors[col] = 0  # Assign default value

        print("Input Features for Model Prediction:\n", relevant_doctors[feature_columns])
        print("Predicted Probabilities:\n", model.predict_proba(relevant_doctors[feature_columns])[:, 1])

        relevant_doctors["Probability"] = model.predict_proba(relevant_doctors[feature_columns])[:, 1]



        # Predict probability for filtered doctors
        feature_columns = ["Login Hour", "Logout Hour", "Usage Time (mins)", "Count of Survey Attempts"]  # Add useful features
        relevant_doctors["Probability"] = model.predict_proba(relevant_doctors[feature_columns])[:, 1] 


        # Sort doctors by highest probability
        df_sorted = relevant_doctors.sort_values(by="Probability", ascending=False).head(10)
        filename = "predicted_doctors.csv"
        df_sorted = df_sorted.drop(columns=["Login Hour", "Logout Hour"], errors="ignore")
        df_sorted.to_csv(filename, index=False)



        return send_file(filename, as_attachment=True)

    except Exception as e:
        print("Error Occurred:", str(e))  # Debugging line
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
