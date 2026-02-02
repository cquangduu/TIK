// src/constants/index.ts
// App-wide constants and configuration

export const APP_NAME = 'TOPIK Daily';
export const APP_VERSION = '1.0.0';

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 10000,
};

// Theme Colors
export const COLORS = {
  primary: '#4A90D9',
  secondary: '#9C27B0',
  success: '#4CAF50',
  warning: '#FF9800',
  danger: '#F44336',
  info: '#2196F3',
  
  // Grays
  white: '#FFFFFF',
  background: '#F5F7FA',
  surface: '#FFFFFF',
  border: '#E0E0E0',
  textPrimary: '#333333',
  textSecondary: '#666666',
  textMuted: '#999999',
  
  // Feature colors
  vocab: '#4A90D9',
  grammar: '#9C27B0',
  news: '#FF9800',
  essay: '#4CAF50',
  streak: '#FF6B35',
  premium: '#FFD700',
};

// Typography
export const FONTS = {
  sizes: {
    xs: 10,
    sm: 12,
    md: 14,
    lg: 16,
    xl: 18,
    xxl: 24,
    xxxl: 32,
  },
  weights: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
};

// Spacing
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

// Border Radius
export const RADIUS = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  round: 9999,
};

// Ad Configuration
export const ADS = {
  BANNER_ID_IOS: 'ca-app-pub-XXXXX/YYYYY',
  BANNER_ID_ANDROID: 'ca-app-pub-XXXXX/ZZZZZ',
  INTERSTITIAL_ID_IOS: 'ca-app-pub-XXXXX/AAAAA',
  INTERSTITIAL_ID_ANDROID: 'ca-app-pub-XXXXX/BBBBB',
};

// Premium Products
export const PREMIUM_PRODUCTS = {
  monthly: 'topik_premium_monthly',
  yearly: 'topik_premium_yearly',
  lifetime: 'topik_premium_lifetime',
};

// Storage Keys
export const STORAGE_KEYS = {
  USER_DATA: '@topik_user_data',
  LESSON_DATA: '@topik_lesson_data',
  PREMIUM_STATUS: '@topik_premium_status',
  PREMIUM_EXPIRY: '@topik_premium_expiry',
  SETTINGS: '@topik_settings',
  ONBOARDING: '@topik_onboarding_complete',
};

// Daily Goals
export const DAILY_GOALS = {
  MIN_VOCAB: 5,
  DEFAULT_VOCAB: 10,
  MAX_VOCAB: 50,
  MIN_QUIZZES: 1,
  DEFAULT_QUIZZES: 2,
};

// Animation Durations
export const ANIMATION = {
  fast: 150,
  normal: 300,
  slow: 500,
};
