import React from "react";
import { motion, AnimatePresence } from "framer-motion";

/* ─────────────────────────────────────────────
   RISK LOGIC (FAILURE + ANOMALY)
───────────────────────────────────────────── */
function getRiskLevel(prob, isAnomaly) {
  if (prob >= 0.7)
    return {
      label: "CRITICAL",
      color: "#ff2d55",
      glow: "glow-danger",
      bg: "bg-red-950/30 border-danger",
    };

  if (isAnomaly)
    return {
      label: "ANOMALY",
      color: "#ff8c00",
      glow: "glow-warn",
      bg: "bg-orange-950/30 border-warn",
    };

  if (prob >= 0.4)
    return {
      label: "WARNING",
      color: "#ffb800",
      glow: "glow-warn",
      bg: "bg-yellow-950/30 border-warn",
    };

  return {
    label: "NOMINAL",
    color: "#00ff9f",
    glow: "glow-success",
    bg: "bg-green-950/20 border-border",
  };
}

/* ───────────────────────────────────────────── */
function Metric({ label, value, unit, color }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="label">{label}</span>
      <span className="font-mono text-sm" style={{ color }}>
        {value}
        {unit && <span className="text-muted text-xs ml-1">{unit}</span>}
      </span>
    </div>
  );
}

/* ───────────────────────────────────────────── */
export default function StatusPanel({ latest, prediction }) {
  const prob = prediction?.failure_probability ?? 0;
  const isAnomaly = prediction?.is_anomaly ?? false;

  const risk = getRiskLevel(prob, isAnomaly);
  const pct = (prob * 100).toFixed(1);

  return (
    <motion.div
      className={`panel p-5 border ${risk.bg} transition-colors duration-700`}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
    >
      {/* ── STATUS HEADER ── */}
      <div className="flex items-center justify-between mb-4">
        <span className="label">System Status</span>

        <motion.span
          key={risk.label}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="font-display text-xs font-bold px-3 py-1 rounded-full border"
          style={{
            color: risk.color,
            borderColor: risk.color,
            textShadow: `0 0 10px ${risk.color}`,
          }}
        >
          {risk.label}
        </motion.span>
      </div>

      {/* ── FAILURE PROBABILITY ── */}
      <div className="mb-4">
        <span className="label block mb-1">Failure Probability</span>

        <div className="flex items-end gap-2">
          <motion.span
            key={pct}
            className={`font-display text-4xl font-bold ${risk.glow}`}
            style={{ color: risk.color }}
          >
            {pct}
          </motion.span>

          <span className="text-muted font-mono text-lg mb-0.5">%</span>
        </div>

        {/* Progress */}
        <div className="mt-2 h-1.5 bg-border rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{
              background: risk.color,
              boxShadow: `0 0 8px ${risk.color}`,
            }}
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.4 }}
          />
        </div>
      </div>

      {/* ── ANOMALY STATUS ── */}
      <div className="mb-4 flex items-center gap-3">
        <span className="label">Anomaly</span>

        <AnimatePresence mode="wait">
          <motion.span
            key={String(isAnomaly)}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="font-mono text-sm font-bold"
            style={{
              color: isAnomaly ? "#ff8c00" : "#00ff9f",
              textShadow: isAnomaly
                ? "0 0 10px rgba(255,140,0,0.8)"
                : "0 0 10px rgba(0,255,159,0.8)",
            }}
          >
            {isAnomaly ? "YES ⚠️" : "NO"}
          </motion.span>
        </AnimatePresence>
      </div>

      {/* ── FAILURE DETECTED ── */}
      <div className="mb-4 flex items-center gap-3">
        <span className="label">Failure</span>

        <AnimatePresence mode="wait">
          <motion.span
            key={String(prediction?.failure_detected)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="font-mono text-sm font-bold"
            style={{
              color: prediction?.failure_detected ? "#ff2d55" : "#00ff9f",
            }}
          >
            {prediction?.failure_detected ? "YES" : "NO"}
          </motion.span>
        </AnimatePresence>
      </div>

      {/* ── FAILURE TYPE ── */}
      <div className="mb-5">
        <span className="label block mb-1">Failure Type</span>

        {prediction?.failure_type ? (
          <span className="font-mono text-sm text-warn">
            {prediction.failure_type}
          </span>
        ) : (
          <span className="font-mono text-sm text-muted">—</span>
        )}
      </div>

      {/* ── SENSOR DATA ── */}
      <div className="border-t border-border pt-4">
        <span className="label block mb-3">Live Sensor Data</span>

        <div className="grid grid-cols-2 gap-3">
          <Metric label="Air Temp" value={latest?.Air_temperature__K_?.toFixed(1) ?? "—"} unit="K" color="#00d4ff" />
          <Metric label="Proc Temp" value={latest?.Process_temperature__K_?.toFixed(1) ?? "—"} unit="K" color="#7c6fcd" />
          <Metric label="RPM" value={latest?.Rotational_speed__rpm_ ?? "—"} unit="rpm" color="#00d4ff" />
          <Metric label="Torque" value={latest?.Torque__Nm_?.toFixed(1) ?? "—"} unit="Nm" color="#ffb800" />
          <Metric label="Tool Wear" value={latest?.Tool_wear__min_ ?? "—"} unit="min" color={latest?.Tool_wear__min_ > 200 ? "#ff2d55" : "#00ff9f"} />
        </div>
      </div>
    </motion.div>
  );
}