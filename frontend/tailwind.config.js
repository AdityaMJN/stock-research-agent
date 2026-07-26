/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        canvas: '#f8fafc',
        ink: '#0f172a',
        terminal: '#0b1120',
        accent: '#22c55e',
      },
      boxShadow: { panel: '0 1px 2px rgb(15 23 42 / 0.06), 0 8px 24px rgb(15 23 42 / 0.04)' },
    },
  },
  plugins: [],
}
