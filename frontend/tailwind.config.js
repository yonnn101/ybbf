/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["DM Sans", "system-ui", "sans-serif"],
        display: ["Instrument Sans", "system-ui", "sans-serif"],
      },
      colors: {
        surface: {
          900: "#0c0f14",
          800: "#131922",
          700: "#1c2433",
          600: "#252f42",
        },
        accent: { DEFAULT: "#22d3ee", dim: "#0891b2" },
      },
    },
  },
  plugins: [],
};
