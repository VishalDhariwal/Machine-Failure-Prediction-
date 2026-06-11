import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Square, AlertTriangle } from "lucide-react";

import ChartComponent from "./ChartComponent";
import StatusPanel from "./StatusPanel";
import CSVUpload from "./CSVUpload";
import ManualPrediction from "./ManualPrediction";
import ChatBot from "./ChatBot";

const MAX_POINTS = 80;

/* ─────────────────────────────────────────────
   ALERT BANNER (Failure + Anomaly)
───────────────────────────────────────────── */
function AlertBanner({ probability, failureType, isAnomaly }) {
  if (probability < 0.7 && !isAnomaly) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="flex items-center gap-3 bg-red-950/60 border border-danger rounded-lg px-4 py-3 mb-4"
      >
        <motion.div
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 0.8 }}
        >
          <AlertTriangle size={18} className="text-danger" />
        </motion.div>

        <div className="flex-1">
          <p className="font-display text-danger text-sm font-bold tracking-wider">
            ⚠ ALERT — {(probability * 100).toFixed(1)}%
          </p>

          {failureType && (
            <p className="font-mono text-xs text-red-300 mt-0.5">
              Failure Type: {failureType}
            </p>
          )}

          {isAnomaly && (
            <p className="font-mono text-xs text-orange-300 mt-0.5">
              Anomaly detected (unknown pattern)
            </p>
          )}
        </div>

        <p className="font-mono text-xs text-danger/70">
          Immediate attention required
        </p>
      </motion.div>
    </AnimatePresence>
  );
}

/* ─────────────────────────────────────────────
   MAIN DASHBOARD
───────────────────────────────────────────── */
export default function Dashboard() {
  const [running, setRunning] = useState(true);
  const [speed, setSpeed] = useState(1);

  const [history, setHistory] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [latest, setLatest] = useState(null);

  const [apiError, setApiError] = useState(null);
  const [totalPoints, setTotalPoints] = useState(0);
  const [failures, setFailures] = useState(0);

  const wsRef = useRef(null);

  /* ─────────────────────────────────────────
     WEBSOCKET STREAM
  ───────────────────────────────────────── */
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setApiError(null);
    };

    ws.onmessage = (event) => {
      const { data, prediction } = JSON.parse(event.data);

      const combined = {
        ...data,
        _prob: prediction?.failure_probability ?? 0,
        _anomaly: prediction?.anomaly_score ?? 0,
        _anomaly_flag: prediction?.is_anomaly ?? false,
      };

      setLatest(data);
      setPrediction(prediction);

      setHistory((prev) => {
        const next = [...prev, combined];
        return next.length > MAX_POINTS ? next.slice(-MAX_POINTS) : next;
      });

      setTotalPoints((n) => n + 1);

      if (prediction?.failure_detected) {
        setFailures((n) => n + 1);
      }
    };

    ws.onerror = () => {
      setApiError("WebSocket error");
    };

    ws.onclose = () => {
      setApiError("Connection lost");
    };

    return () => ws.close();
  }, []);

  const prob = prediction?.failure_probability ?? 0;

  /* ───────────────────────────────────────── */


  return (
    <div className="min-h-screen bg-void p-4 lg:p-6">

      {/* ── HEADER ── */}
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-center justify-between gap-4 mb-6"
      >
        <div>
          <h1 className="font-display text-2xl font-bold text-accent tracking-widest">
            MHMS
          </h1>
          <p className="font-mono text-xs text-muted">
            Machine Health Monitoring System · v2.1
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">

          <div className="flex border border-border rounded p-1">
            {[1, 2].map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={`px-2 text-xs font-mono ${
                  speed === s ? "bg-accent text-void" : "text-muted"
                }`}
              >
                {s}×
              </button>
            ))}
          </div>

          <button
            onClick={() => setRunning((r) => !r)}
            className={running ? "btn-danger" : "btn-primary"}
          >
            {running ? <Square size={12} /> : <Play size={12} />}
          </button>
        </div>
      </motion.div>

      {/* ── ALERT (Failure + Anomaly) ── */}
      <AlertBanner
        probability={prediction?.failure_probability ?? 0}
        failureType={prediction?.failure_type}
        isAnomaly={prediction?.is_anomaly}
      />

      {/* ── STATS ── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="grid grid-cols-4 gap-3 mb-5"
      >
        {[
          { label: "Data Points", value: totalPoints, color: "#00d4ff" },
          { label: "Failures", value: failures, color: "#ff2d55" },
          {
            label: "Anomalies",
            value: history.filter((h) => h._anomaly_flag).length,
            color: "#ff8c00",
          },
          {
            label: "Uptime",
            value: `${Math.floor(totalPoints / 60)}m`,
            color: "#00ff9f",
          },
        ].map((s) => (
          <div key={s.label} className="panel p-3 text-center">
            <p className="label mb-1">{s.label}</p>
            <p
              className="font-display text-lg font-bold"
              style={{ color: s.color }}
            >
              {s.value}
            </p>
          </div>
        ))}
      </motion.div>

      {/* ── CHARTS ── */}
      <div className="flex flex-col gap-4">

        <ChartComponent
          title="Temperature · Air vs Process"
          data={history}
          lines={[
            { key: "Air_temperature__K_", name: "Air", color: "#00d4ff" },
            { key: "Process_temperature__K_", name: "Process", color: "#7c6fcd" },
          ]}
        />

        <ChartComponent
          title="Torque (Nm)"
          data={history}
          lines={[
            { key: "Torque__Nm_", name: "Torque", color: "#ffb800" }
          ]}
        />

        <ChartComponent
          title="Tool Wear (min)"
          data={history}
          lines={[
            { key: "Tool_wear__min_", name: "Wear", color: "#00ff9f" }
          ]}
        />

        {/* ✅ FIXED: TRUE TIME SERIES */}
        <ChartComponent
          title="Failure Probability"
          data={history}
          lines={[
            { key: "_prob", name: "Failure Prob", color: "#ff2d55" }
          ]}
        />

        {/* ✅ NEW: ANOMALY TRACKING */}
        <ChartComponent
          title="Anomaly Score"
          data={history}
          lines={[
            { key: "_anomaly", name: "Anomaly", color: "#ff8c00" }
          ]}
        />

      </div>

      {/* ── SIDE PANELS ── */}
      <div className="grid lg:grid-cols-3 gap-4 mt-5">
        <StatusPanel latest={latest} prediction={prediction} />
        <ManualPrediction />
        <CSVUpload />
      </div>

      {/* ── ERROR STATE ── */}
      {apiError && (
        <p className="text-red-400 mt-4 font-mono text-xs">
          Backend disconnected — ML predictions unavailable
        </p>
      )}

      <ChatBot
        latest={latest}
        prediction={prediction}
        history={history.slice(-20)}
      />
    </div>
  );
}