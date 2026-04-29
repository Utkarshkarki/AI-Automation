/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Xtract Electric Violet Palette
        brand: {
          50:  '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed', // Electric violet
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        // Pure Black Surface Palette
        surface: {
          950: '#000000', // Pure black
          900: '#0a0a0a',
          800: '#141414',
          750: '#1f1f1f',
          700: '#292929',
          600: '#333333',
          500: '#404040',
          400: '#525252',
        },
        // Accent (cyan/magenta mix)
        accent: {
          400: '#d946ef',
          500: '#c026d3',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #7c3aed 0%, #c026d3 100%)',
        'gradient-surface': 'linear-gradient(135deg, #0a0a0a 0%, #141414 100%)',
      },
      boxShadow: {
        'glow-brand': '0 0 25px rgba(124, 58, 237, 0.4)',
        'glow-accent': '0 0 25px rgba(192, 38, 211, 0.3)',
        'card': '0 4px 24px rgba(0,0,0,0.8)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
