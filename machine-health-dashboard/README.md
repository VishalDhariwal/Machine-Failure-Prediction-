# Machine Health Monitoring Dashboard

Industrial-grade real-time dashboard for machine failure prediction.

## Quick Start

```bash
# 1. Go into the project folder
cd machine-health-dashboard

# 2. Install dependencies
npm install

# 3. (Optional) Configure backend URL
# Edit .env → REACT_APP_API_URL=http://localhost:8000

# 4. Start the dev server
npm start
```

The app opens at http://localhost:3000.

## Backend Requirements

Your FastAPI backend must expose:

| Endpoint      | Method | Input                    | Output                                                    |
|---------------|--------|--------------------------|-----------------------------------------------------------|
| `/predict`    | POST   | JSON sensor payload      | `{failure_probability, failure_detected, failure_type}`   |
| `/predict_csv`| POST   | multipart CSV file       | Array of prediction objects                               |

If the backend is unreachable, the dashboard automatically falls into **DEMO MODE** — it still runs the simulation and generates plausible predictions locally.

## Environment Variables

| Variable              | Default                   | Description           |
|-----------------------|---------------------------|-----------------------|
| `REACT_APP_API_URL`   | `http://localhost:8000`   | FastAPI backend URL   |

## Project Structure

```
src/
├── App.js
├── index.js
├── index.css              ← Tailwind + custom CSS variables
├── components/
│   ├── Dashboard.js       ← Main layout, simulation loop, controls
│   ├── ChartComponent.js  ← Reusable Recharts line chart with anomaly dots
│   ├── StatusPanel.js     ← Failure probability, risk badge, sensor readouts
│   └── CSVUpload.js       ← Drag-and-drop CSV upload + results table
└── utils/
    ├── dataGenerator.js   ← Realistic sensor data generator (smooth walk + spikes)
    └── api.js             ← fetch wrappers for /predict and /predict_csv
```

## Features

- **Real-time simulation** at 1× or 2× speed with smooth random walk + spike injection
- **Live charts**: temperature pair, torque, tool wear, failure probability
- **Anomaly markers** (red dots on charts during spike events)
- **Risk color-coding**: green / yellow / red
- **Animated alert banner** when failure_probability > 0.7
- **CSV batch upload** with summary stats and downloadable results
- **Demo mode** when backend is offline
