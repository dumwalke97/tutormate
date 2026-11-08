/** @type {import('tailwindcss').Config} */
// Marketing pages only. www/app/ still loads Tailwind from the CDN because its
// class names are partly constructed at runtime and would not survive a static
// content scan. That page is noindex, so its performance is not an SEO concern.
module.exports = {
  content: [
    './www/index.html',
    './www/privacy/index.html',
    './www/about/index.html',
    './www/homework-help/index.html',
    './www/quiz-generator/index.html',
    './www/algebra/index.html',
    './www/biology/index.html',
    './www/written-answers/index.html',
    './www/vs/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#EEF1F8',
          200: '#B9C4DE',
          400: '#5B6B96',
          500: '#3C4A72',
          600: '#2A3760',
          700: '#202B52',
          800: '#1B2447',
          900: '#131A35',
        },
      },
      fontFamily: {
        title: ['Nunito', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
