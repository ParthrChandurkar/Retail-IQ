import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        surface: "var(--surface)",
        border: "var(--border)",
        primary: "var(--primary)",
        accent: "var(--accent)",
        success: "var(--success)",
        danger: "var(--danger)",
        ink: "var(--text-primary)",
        muted: "var(--text-secondary)",
      },
      borderRadius: { card: "var(--radius)", control: "0.5rem" },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        lift: "0 10px 30px color-mix(in srgb, var(--text-primary) 8%, transparent)",
      },
    },
  },
  plugins: [],
};
export default config;
