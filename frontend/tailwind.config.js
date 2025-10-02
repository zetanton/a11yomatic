/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5e5e5',
          100: '#e6cccc',
          200: '#cc9999',
          300: '#b36666',
          400: '#993333',
          500: '#800000',
          600: '#500000',
          700: '#400000',
          800: '#300000',
          900: '#200000',
        },
        maroon: {
          DEFAULT: '#500000',
          light: '#800000',
          dark: '#300000',
        },
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['Open Sans', 'Arial', 'system-ui', 'sans-serif'],
        mono: ['monospace'],
      },
    },
  },
  plugins: [],
}


