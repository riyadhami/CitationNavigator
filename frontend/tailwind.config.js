/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        cream: {
          DEFAULT: '#f4f1ea',
          50:      '#faf8f5',
          100:     '#f4f1ea',
          200:     '#e8e0d0',
        },
        bark: {
          DEFAULT: '#382110',
          400:     '#9D7150',
          500:     '#7a5534',
          600:     '#5a3e1b',
        },
        leaf: {
          DEFAULT: '#409D69',
          dark:    '#2f7a50',
        },
        // Dark theme palette — warm dark tones
        dusk: {
          900: '#121008',   // page background
          800: '#1c1912',   // card / surface
          700: '#252118',   // nested surface, hover
          600: '#3a3324',   // borders
          400: '#9d8a6a',   // muted text
          100: '#ede0c8',   // primary text
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', '"Times New Roman"', 'serif'],
      },
      typography: ({ theme }) => ({
        bark: {
          css: {
            '--tw-prose-body':          theme('colors.bark.DEFAULT'),
            '--tw-prose-headings':      theme('colors.bark.DEFAULT'),
            '--tw-prose-links':         theme('colors.leaf.DEFAULT'),
            '--tw-prose-bold':          theme('colors.bark.DEFAULT'),
            '--tw-prose-counters':      theme('colors.bark[400]'),
            '--tw-prose-bullets':       theme('colors.bark[400]'),
            '--tw-prose-hr':            theme('colors.cream[200]'),
            '--tw-prose-quotes':        theme('colors.bark[400]'),
            '--tw-prose-quote-borders': theme('colors.leaf.DEFAULT'),
            '--tw-prose-captions':      theme('colors.bark[400]'),
            '--tw-prose-code':          theme('colors.bark.DEFAULT'),
            '--tw-prose-pre-code':      theme('colors.bark.DEFAULT'),
            '--tw-prose-pre-bg':        theme('colors.cream.DEFAULT'),
            '--tw-prose-th-borders':    theme('colors.cream[200]'),
            '--tw-prose-td-borders':    theme('colors.cream[200]'),
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
