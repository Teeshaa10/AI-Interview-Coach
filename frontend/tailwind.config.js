/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          200: "#b8d0ff",
          300: "#8bb0ff",
          400: "#5b87ff",
          500: "#3661f5",
          600: "#2444d6",
          700: "#1e35ab",
          800: "#1c2f88",
          900: "#1b2a6b",
          950: "#0f1743",
        },
        surface: {
          950: "#05070f",
          900: "#0a0e1a",
          800: "#111729",
          700: "#1a2236",
          600: "#242e46",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(91,135,255,0.15), 0 8px 30px -8px rgba(54,97,245,0.35)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: 0, transform: "translateY(4px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.25s ease-out",
      },
    },
  },
  plugins: [],
};
