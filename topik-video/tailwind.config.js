/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // Quét các file trong thư mục src
    "./public/**/*.html",         // Quét các file HTML trong public
  ],
  theme: {
    extend: {}, // Tuỳ chỉnh theme tại đây nếu cần
  },
  plugins: [],
};