import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#09111f",
        ember: "#f97316",
        mint: "#6ee7b7",
        skyglass: "#dbeafe",
      },
      boxShadow: {
        glow: "0 20px 40px rgba(14, 165, 233, 0.18)",
      },
      backgroundImage: {
        "hero-grid":
          "radial-gradient(circle at top, rgba(110, 231, 183, 0.24), transparent 32%), linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(3, 7, 18, 1))",
      },
    },
  },
  plugins: [],
} satisfies Config;

