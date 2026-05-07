import React, { useState } from "react";
import { motion } from "framer-motion";
import { predictManual } from "../utils/api";

/* ─────────────────────────────────────────────
   LABEL MAPPING (UI ONLY)
───────────────────────────────────────────── */
const fieldLabels = {
  Air_temperature__K_: "Air Temperature (K)",
  Process_temperature__K_: "Process Temperature (K)",
  Rotational_speed__rpm_: "Rotational Speed (RPM)",
  Torque__Nm_: "Torque (Nm)",
  Tool_wear__min_: "Tool Wear (min)",
};

/* ─────────────────────────────────────────────
   COMPONENT
───────────────────────────────────────────── */
export default function ManualPrediction() {
  const [form, setForm] = useState({
    Air_temperature__K_: 0,
    Process_temperature__K_: 0,
    Rotational_speed__rpm_: 0,
    Torque__Nm_: 0,
    Tool_wear__min_: 0,
    Type_H: 0,
    Type_L: 1,
    Type_M: 0,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /* ───────────────────────────── */
  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: Number(value),
    }));
  }

  /* ───────────────────────────── */
  function setType(type) {
    setForm((prev) => ({
      ...prev,
      Type_H: type === "H" ? 1 : 0,
      Type_L: type === "L" ? 1 : 0,
      Type_M: type === "M" ? 1 : 0,
    }));
  }

  /* ───────────────────────────── */
  async function handleSubmit() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await predictManual(form);
      setResult(res);
    } catch (err) {
      setError(err.message || "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  /* ───────────────────────────── */
  return (
    <div className="panel p-5">
      <span className="label">Custom Prediction</span>

      {/* INPUT GRID */}
      <div className="grid grid-cols-2 gap-3 mt-3 text-xs font-mono">
        {Object.keys(fieldLabels).map((key) => (
          <div key={key} className="flex flex-col gap-1">
            
            <label className="text-muted text-[10px]">
              {fieldLabels[key]}
            </label>

            <input
              name={key}
              value={form[key]}
              onChange={handleChange}
              className="bg-void border border-border px-2 py-1 rounded"
            />
          </div>
        ))}
      </div>

      {/* TYPE SELECTOR */}
      <div className="mt-3 flex gap-2">
        {["H", "L", "M"].map((t) => (
          <button
            key={t}
            onClick={() => setType(t)}
            className={`px-3 py-1 text-xs border rounded transition ${
              (t === "H" && form.Type_H) ||
              (t === "L" && form.Type_L) ||
              (t === "M" && form.Type_M)
                ? "bg-accent text-void border-accent"
                : "border-border text-muted"
            }`}
          >
            Type {t}
          </button>
        ))}
      </div>

      {/* SUBMIT */}
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="btn mt-4 w-full"
      >
        {loading ? "Predicting..." : "Run Prediction"}
      </button>

      {/* ERROR */}
      {error && (
        <p className="text-red-400 text-xs mt-2 font-mono">
          {error}
        </p>
      )}

      {/* RESULT */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 text-xs font-mono border border-border rounded p-3 bg-void space-y-2"
        >
          {/* Probability */}
          <div className="flex justify-between">
            <span className="text-muted">Failure Probability</span>
            <span className="text-accent font-bold">
              {(result.failure_probability * 100).toFixed(2)}%
            </span>
          </div>

          {/* Detection */}
          <div className="flex justify-between">
            <span className="text-muted">Failure Detected</span>
            <span
              className={
                result.failure_detected
                  ? "text-red-400 font-semibold"
                  : "text-green-400"
              }
            >
              {result.failure_detected ? "YES" : "NO"}
            </span>
          </div>

          {/* Failure Type */}
          <div className="flex justify-between">
            <span className="text-muted">Failure Type</span>
            <span className="text-muted">
              {result.failure_type || "—"}
            </span>
          </div>

          {/* Divider */}
          <div className="border-t border-border my-1" />

          {/* Anomaly */}
          <div className="flex justify-between">
            <span className="text-muted">Anomaly</span>
            <span
              className={
                result.is_anomaly
                  ? "text-orange-400 font-semibold"
                  : "text-green-400"
              }
            >
              {result.is_anomaly ? "YES ⚠️" : "NO"}
            </span>
          </div>

          {/* Anomaly Score */}
          <div className="flex justify-between">
            <span className="text-muted">Anomaly Score</span>
            <span className="text-muted">
              {result.anomaly_score?.toFixed(3)}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}