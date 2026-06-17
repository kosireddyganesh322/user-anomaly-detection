/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#f0f4ff",
          500: "#3b5bdb",
          700: "#2f4ac2",
          900: "#1e3a8a",
        },
        danger:  "#ef4444",
        warning: "#f59e0b",
        safe:    "#22c55e",
      },
    },
  },
  plugins: [],
};
