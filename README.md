# 🏭 Machine Failure Prediction App

An end-to-end **machine health monitoring system** that predicts equipment failure using machine learning models and detects anomalies from sensor data.  
The system combines:
- Supervised ML (failure prediction)
- Isolation Forest (anomaly detection)
- Rule-based risk scoring
- Interactive React dashboard

---

# 🚀 Features

- 📊 Real-time machine failure prediction
- ⚠️ Anomaly detection using Isolation Forest + statistical rules
- 📈 Risk scoring system (Normal / Warning / Critical)
- 🧠 Failure type classification (multi-class model)
- 📁 CSV upload for batch predictions
- 📉 Interactive dashboard (charts + status panel)

---

# 🧠 Tech Stack

## Backend
- FastAPI
- Scikit-learn
- Pandas
- Joblib

## Frontend
- React.js
- Tailwind CSS
- Chart.js

---

# 📁 Project Structure

.
├── Backend/ # FastAPI + ML models
│ ├── main.py # API entry point
│ ├── models.py # ML prediction logic
│ ├── schema.py # Request/response models
│ ├── dataGenerator.py # synthetic data generator
│ └── ml-models/ # trained models
│
├── machine-health-dashboard/ # React frontend
│ ├── src/
│ ├── components/
│ └── utils/api.js
│
├── requirement.txt
└── structure.txt

---

# ⚙️ Setup Instructions

## 🔧 1. Clone the Project
```bash id="clone"
git clone <https://github.com/VishalDhariwal/Machine-Failure-Prediction>

🐍 2. Backend Setup (FastAPI)
Install dependencies:

pip install -r requirement.txt


Run backend server:

uvicorn Backend.main:app --reload


Backend runs at:

http://localhost:8000


⚛️ 3. Frontend Setup (React)
Navigate to frontend folder:

cd machine-health-dashboard


Install dependencies:

npm install


Start React app:

npm start


Frontend runs at:

http://localhost:3000


🔗 API Connection
Frontend communicates with backend at:

http://localhost:8000


Make sure backend is running before using the dashboard.
📊 How It Works
User inputs machine sensor data or uploads CSV
Backend processes data through ML pipeline:Stage 1: Failure probability prediction
Isolation Forest: anomaly detection
Risk scoring engine: severity calculation
Stage 2: Failure type classification
Results are sent back to frontend dashboard
🚨 Prediction Logic
Failure Probability ≥ 0.9 → CRITICAL FAILURE
Anomaly detected → HIGH RISK
Otherwise:Risk ≥ 0.7 → CRITICAL
Risk ≥ 0.4 → WARNING
Else → NORMAL
📦 ML Models Used
Stage 1 Model → Binary failure prediction
Stage 2 Model → Failure type classification
Isolation Forest → Anomaly detection
🧪 Example Input

{
  "Air_temperature__K_": 302.5,
  "Process_temperature__K_": 310.2,
  "Rotational_speed__rpm_": 1800,
  "Torque__Nm_": 45,
  "Tool_wear__min_": 120,
  "Type": "L"
}

📌 Output Example

{
  "failure_probability": 0.92,
  "failure_detected": true,
  "failure_type": "Heat Failure",
  "is_anomaly": true,
  "risk_score": 0.87,
  "risk_level": "CRITICAL"
}

🛠️ Common Issues
❌ CORS Error
Enable in FastAPI:


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

❌ React not starting

npm install
npm start

👨‍💻 Author
Built as a machine learning + full-stack project for predictive maintenance systems.
📈 Future Improvements
Real-time IoT sensor integration
Kafka streaming pipeline
Model retraining pipeline
Cloud deployment (AWS / Azure)
SHAP explainability for predictions
