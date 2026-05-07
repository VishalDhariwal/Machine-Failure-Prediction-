// ─── CSVUpload.js ─────────────────────────────────────────────────────────────
import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { predictCSV } from "../utils/api";
import { Upload, Download, AlertCircle, CheckCircle, X } from "lucide-react";

function getRiskColor(prob) {
  if (prob >= 0.7) return "#ff2d55";
  if (prob >= 0.4) return "#ffb800";
  return "#00ff9f";
}

function getRiskLabel(prob) {
  if (prob >= 0.7) return "CRITICAL";
  if (prob >= 0.4) return "WARNING";
  return "OK";
}

export default function CSVUpload() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef();

  async function handleFile(file) {
    if (!file || !file.name.endsWith(".csv")) {
      setError("Please upload a valid .csv file.");
      return;
    }
    setFileName(file.name);
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await predictCSV(file);
      setResults(Array.isArray(data) ? data : [data]);
    } catch (err) {
      setError(err.message || "Upload failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function downloadCSV() {
    if (!results?.length) return;
    const keys = Object.keys(results[0]);
    const rows = [keys.join(","), ...results.map((r) => keys.map((k) => r[k]).join(","))];
    const blob = new Blob([rows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "predictions.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  const criticalCount = results?.filter((r) => (r.failure_probability ?? 0) >= 0.7).length ?? 0;
  const warningCount = results?.filter((r) => {
    const p = r.failure_probability ?? 0;
    return p >= 0.4 && p < 0.7;
  }).length ?? 0;

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between mb-4">
        <span className="label">Batch CSV Analysis</span>
        {results && (
          <button onClick={downloadCSV} className="btn-muted btn flex items-center gap-1">
            <Download size={12} /> Export
          </button>
        )}
      </div>

      {/* Drop Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200
          ${dragOver ? "border-accent bg-accent/5" : "border-border hover:border-muted"}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <Upload
          size={24}
          className={`mx-auto mb-2 ${dragOver ? "text-accent" : "text-muted"}`}
        />
        <p className="font-mono text-xs text-muted">
          {loading
            ? "Analyzing..."
            : fileName
            ? `Loaded: ${fileName}`
            : "Drop CSV or click to upload"}
        </p>
        {loading && (
          <div className="mt-2 flex justify-center">
            <div className="w-24 h-0.5 bg-border rounded overflow-hidden">
              <motion.div
                className="h-full bg-accent"
                animate={{ x: ["-100%", "200%"] }}
                transition={{ repeat: Infinity, duration: 1, ease: "easeInOut" }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 flex items-center gap-2 text-xs font-mono text-danger border border-danger/30 rounded px-3 py-2 bg-red-950/20"
          >
            <AlertCircle size={12} />
            {error}
            <button onClick={() => setError(null)} className="ml-auto">
              <X size={12} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Summary */}
      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            {/* Stats row */}
            <div className="flex gap-3 mb-3">
              <div className="flex-1 bg-void rounded border border-border p-2 text-center">
                <p className="font-display text-lg text-accent">{results.length}</p>
                <p className="label text-xs">Total</p>
              </div>
              <div className="flex-1 bg-void rounded border border-danger/30 p-2 text-center">
                <p className="font-display text-lg text-danger">{criticalCount}</p>
                <p className="label text-xs">Critical</p>
              </div>
              <div className="flex-1 bg-void rounded border border-warn/30 p-2 text-center">
                <p className="font-display text-lg text-warn">{warningCount}</p>
                <p className="label text-xs">Warning</p>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-auto max-h-48 rounded border border-border">
              <table className="w-full text-xs font-mono">
                <thead className="sticky top-0 bg-panel">
                  <tr>
                    <th className="text-left px-3 py-2 text-muted border-b border-border">#</th>
                    <th className="text-left px-3 py-2 text-muted border-b border-border">Prob %</th>
                    <th className="text-left px-3 py-2 text-muted border-b border-border">Detected</th>
                    <th className="text-left px-3 py-2 text-muted border-b border-border">Type</th>
                    <th className="text-left px-3 py-2 text-muted border-b border-border">Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, i) => {
                    const prob = r.failure_probability ?? 0;
                    const color = getRiskColor(prob);
                    return (
                      <tr
                        key={i}
                        className="border-b border-border/50 hover:bg-white/2 transition-colors"
                      >
                        <td className="px-3 py-1.5 text-muted">{i + 1}</td>
                        <td className="px-3 py-1.5" style={{ color }}>
                          {(prob * 100).toFixed(1)}%
                        </td>
                        <td className="px-3 py-1.5" style={{ color: r.failure_detected ? "#ff2d55" : "#00ff9f" }}>
                          {r.failure_detected ? "YES" : "NO"}
                        </td>
                        <td className="px-3 py-1.5 text-slate-300">{r.failure_type || "—"}</td>
                        <td className="px-3 py-1.5">
                          <span
                            className="px-2 py-0.5 rounded text-xs font-bold"
                            style={{
                              color,
                              background: `${color}18`,
                              border: `1px solid ${color}40`,
                            }}
                          >
                            {getRiskLabel(prob)}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
