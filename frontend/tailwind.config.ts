import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0E1116",      // near-black with a blue undertone, not pure #000
        surface: "#151A21",
        surfaceRaised: "#1C222B",
        border: "#262E38",
        ink: "#E7ECF2",
        inkMuted: "#8B96A5",
        signal: "#5EE6B0",      // phosphor-green accent: "signal" = a healthy reading, ties to the product's health metrics
        signalMuted: "#2E4A40",
        risk: "#F2725A",
      },
      fontFamily: {
        display: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      borderRadius: {
        DEFAULT: "6px",
      },
    },
  },
  plugins: [],
};
export default config;
