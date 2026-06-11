/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        podium: {
          50: "#f0f4ff",
          100: "#dce6fe",
          500: "#4f6ef7",
          600: "#3b55e6",
          700: "#2d43c8",
          900: "#1a2580",
        },
      },
    },
  },
  plugins: [],
};
