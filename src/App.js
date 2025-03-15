import React, { useState } from "react";
import axios from "axios";

function App() {
  const [hour, setHour] = useState("");
  const [minute, setMinute] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    if (
      !hour.match(/^(0?[0-9]|1[0-9]|2[0-3])$/) ||
      !minute.match(/^[0-5]?[0-9]$/)
    ) {
      setError("Enter a valid time (HH:MM in 24-hour format).");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/predict",
        { hour, minute },
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "predicted_doctors.csv");
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      setError("Failed to get predictions. Try again.");
      console.error("Error fetching predictions:", err);
    }
    setLoading(false);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Doctor Survey Predictor</h1>
      <p>
        Enter a time in <strong>24-hour format (HH:MM)</strong> to get the best
        doctors for surveys.
      </p>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "10px",
          alignItems: "center",
        }}
      >
        <input
          type="number"
          value={hour}
          onChange={(e) => setHour(e.target.value)}
          placeholder="HH"
          min="0"
          max="23"
          style={{
            width: "60px",
            padding: "8px",
            fontSize: "16px",
            textAlign: "center",
          }}
        />
        <span style={{ fontSize: "20px" }}>:</span>
        <input
          type="number"
          value={minute}
          onChange={(e) => setMinute(e.target.value)}
          placeholder="MM"
          min="0"
          max="59"
          style={{
            width: "60px",
            padding: "8px",
            fontSize: "16px",
            textAlign: "center",
          }}
        />
      </div>

      <button
        onClick={handlePredict}
        disabled={loading}
        style={{ padding: "8px 15px", fontSize: "16px", marginTop: "10px" }}
      >
        {loading ? "Processing..." : "Get Predictions"}
      </button>

      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}
    </div>
  );
}

export default App;
