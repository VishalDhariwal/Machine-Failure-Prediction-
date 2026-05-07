/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      fontFamily: {
        mono: ["'Share Tech Mono'", "monospace"],
        display: ["'Orbitron'", "monospace"],
        body: ["'DM Sans'", "sans-serif"],
      },
      colors: {
        void: "#050810",
        panel: "#0a0f1e",
        border: "#1a2540",
        accent: "#00d4ff",
        success: "#00ff9f",
        warn: "#ffb800",
        danger: "#ff2d55",
        muted: "#4a5a7a",
      },
      animation: {
        pulse_danger: "pulse_danger 1s ease-in-out infinite",
        scanline: "scanline 3s linear infinite",
      },
      keyframes: {
        pulse_danger: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(255,45,85,0.7)" },
          "50%": { boxShadow: "0 0 0 12px rgba(255,45,85,0)" },
        },
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
      },
    },
  },
  plugins: [],
};
