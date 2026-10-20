/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0a192f',
          800: '#112240',
          700: '#1a365d',
        },
        slate: {
          850: '#1e293b',
        },
      },
    },
  },
  plugins: [],
}
