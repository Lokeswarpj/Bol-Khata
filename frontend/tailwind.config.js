/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: '#050505',
        paper: '#EBEBEB',
        emerald: {
          500: '#10B981',
          400: '#34D399',
          600: '#059669',
        }
      },
      fontFamily: {
        serif: ['Newsreader', '"Noto Serif Devanagari"', 'serif'],
        sans: ['Inter', '"Noto Sans Devanagari"', 'system-ui', 'sans-serif'],
        tech: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
      },
      transitionTimingFunction: {
        weighted: 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      borderRadius: {
        '3xl': '1.5rem',
        '2xl': '1rem',
      }
    },
  },
  plugins: [],
}
