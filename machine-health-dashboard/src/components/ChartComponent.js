import React, { memo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceDot,
} from "recharts";
import { motion } from "framer-motion";

/* ─────────────────────────────────────────────
   THEME
───────────────────────────────────────────── */
const CHART_THEME = {
  grid: "#1a2540",
  axis: "#4a5a7a",
};

/* ─────────────────────────────────────────────
   TOOLTIP
───────────────────────────────────────────── */
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;

  const anomaly = payload?.[0]?.payload?._anomaly_flag;

  return (
    <div className="bg-panel border border-border rounded px-3 py-2 text-xs font-mono shadow-lg">
      <p className="text-muted mb-1">t={label}</p>

      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}:{" "}
          <span className="text-white">
            {typeof p.value === "number" ? p.value.toFixed(2) : p.value}
          </span>
        </p>
      ))}

      {/* 🔥 anomaly indicator */}
      {anomaly && (
        <p className="text-orange-400 mt-1">⚠ anomaly</p>
      )}
    </div>
  );
};

/* ─────────────────────────────────────────────
   COMPONENT
───────────────────────────────────────────── */
function ChartComponent({ title, data, lines, domain }) {
  // fallback tick if not provided
  const enrichedData = data.map((d, i) => ({
    _tick: d._tick ?? i,
    ...d,
  }));

  return (
    <motion.div
      className="panel p-4 h-52"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* HEADER */}
      <div className="flex items-center justify-between mb-3">
        <span className="label">{title}</span>

        <span className="flex items-center gap-2">
          {lines.map((l) => (
            <span
              key={l.key}
              className="flex items-center gap-1 text-xs font-mono"
              style={{ color: l.color }}
            >
              <span
                className="inline-block w-3 h-0.5 rounded"
                style={{ background: l.color }}
              />
              {l.name || l.key}
            </span>
          ))}
        </span>
      </div>

      <ResponsiveContainer width="100%" height="80%">
        <LineChart
          data={enrichedData}
          margin={{ top: 2, right: 4, left: -20, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />

          <XAxis
            dataKey="_tick"
            tick={{
              fill: CHART_THEME.axis,
              fontSize: 9,
              fontFamily: "monospace",
            }}
            tickLine={false}
            axisLine={{ stroke: CHART_THEME.grid }}
          />

          <YAxis
            domain={domain || ["auto", "auto"]}
            tick={{
              fill: CHART_THEME.axis,
              fontSize: 9,
              fontFamily: "monospace",
            }}
            tickLine={false}
            axisLine={false}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* SENSOR LINES */}
          {lines.map((l) => (
            <Line
              key={l.key}
              type="monotone"
              dataKey={l.key}
              stroke={l.color}
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3, fill: l.color }}
              isAnimationActive={false}
            />
          ))}

          {/* 🔥 ANOMALY POINTS */}
          {enrichedData
            .filter((d) => d._anomaly_flag)
            .map((d) => (
              <ReferenceDot
                key={`a-${d._tick}`}
                x={d._tick}
                y={d[lines?.[0]?.key]} // anchor to first line
                r={3}
                fill="#ff8c00"
                stroke="#fff"
                strokeWidth={1}
              />
            ))}

          {/* 🔥 HIGH FAILURE POINTS */}
          {enrichedData
            .filter((d) => d._prob > 0.7)
            .map((d) => (
              <ReferenceDot
                key={`f-${d._tick}`}
                x={d._tick}
                y={d[lines?.[0]?.key]}
                r={3}
                fill="#ff2d55"
              />
            ))}
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
}

export default memo(ChartComponent);