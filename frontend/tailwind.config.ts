import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        unravel: {
          teal: "#1F6F6E",
          tealDark: "#164F4E",
          tealLight: "#2D8B89",
          mint: "#E8F4F3",
          cream: "#F7F3EE",
          ink: "#201B17",
          inkSoft: "#5B564F",
          red: "#B93A3A",
          redSoft: "#F3E1E1",
          amber: "#C9822E",
          amberSoft: "#F5E6D3",
          border: "#E4DFD5",
        },
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(32, 27, 23, 0.06), 0 1px 8px rgba(32, 27, 23, 0.04)",
        panel: "-4px 0 24px rgba(32, 27, 23, 0.06)",
      },
      letterSpacing: {
        widest2: "0.18em",
      },
    },
  },
  plugins: [],
};

export default config;
