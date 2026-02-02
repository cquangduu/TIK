// services/api.ts
// API Client for DAILY KOREAN Mobile App

import axios from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== TYPES ====================

export interface VocabularyItem {
  id: number;
  word: string;
  meaning: string;
  example?: string;
  audio_url?: string;
}

export interface QuizQuestion {
  id: string;
  type: 'vocab' | 'grammar';
  target: string;
  question_ko: string;
  question_vi: string;
  options_ko: string[];
  options_vi: string[];
  correct_answer: string;
  explanation_ko: string;
  explanation_vi: string;
}

export interface NewsItem {
  id: string;
  date: string;
  content_ko: string;
  content_vi?: string;
  audio_url?: string;
}

export interface EssayData {
  topic: string;
  question: string;
  essay_ko: string;
  paragraphs: Array<{
    type: string;
    korean: string;
    analysis: string;
  }>;
}

export interface LessonData {
  date: string;
  topic: string;
  vocabulary: VocabularyItem[];
  vocab_quiz?: QuizQuestion;
  grammar_quiz?: QuizQuestion;
  news?: NewsItem;
  essay?: EssayData;
}

export interface UserProgress {
  user_id: string;
  date: string;
  quizzes_completed: number;
  correct_answers: number;
  vocabulary_learned: string[];
  streak_days: number;
}

// ==================== LESSON API ====================

export const lessonApi = {
  /**
   * Get today's complete lesson
   */
  getToday: async (): Promise<LessonData> => {
    const response = await api.get('/api/today');
    return response.data;
  },

  /**
   * Get vocabulary list with pagination
   */
  getVocabulary: async (limit = 20, offset = 0): Promise<VocabularyItem[]> => {
    const response = await api.get('/api/vocabulary', { 
      params: { limit, offset } 
    });
    return response.data;
  },

  /**
   * Get a random vocabulary item for flashcard
   */
  getRandomVocab: async (): Promise<VocabularyItem> => {
    const response = await api.get('/api/vocabulary/random');
    return response.data;
  },

  /**
   * Get specific vocabulary by ID
   */
  getVocabById: async (id: number): Promise<VocabularyItem> => {
    const response = await api.get(`/api/vocabulary/${id}`);
    return response.data;
  },

  /**
   * Get vocabulary quiz
   */
  getVocabQuiz: async (): Promise<QuizQuestion> => {
    const response = await api.get('/api/quiz/vocab');
    return response.data;
  },

  /**
   * Get grammar quiz
   */
  getGrammarQuiz: async (): Promise<QuizQuestion> => {
    const response = await api.get('/api/quiz/grammar');
    return response.data;
  },

  /**
   * Get today's news
   */
  getNews: async (): Promise<NewsItem> => {
    const response = await api.get('/api/news');
    return response.data;
  },

  /**
   * Get model essay
   */
  getEssay: async (): Promise<EssayData> => {
    const response = await api.get('/api/essay');
    return response.data;
  },

  /**
   * Get archived lesson by date
   */
  getArchive: async (date: string): Promise<LessonData> => {
    const response = await api.get(`/api/archive/${date}`);
    return response.data;
  },

  /**
   * List available archived dates
   */
  listArchive: async (limit = 30): Promise<{ dates: string[] }> => {
    const response = await api.get('/api/archive', { 
      params: { limit } 
    });
    return response.data;
  },
};

// ==================== PROGRESS API ====================

export const progressApi = {
  /**
   * Update user progress after quiz
   */
  update: async (
    userId: string, 
    quizType: string, 
    isCorrect: boolean, 
    vocabId?: number
  ): Promise<{ success: boolean; progress: UserProgress }> => {
    const response = await api.post('/api/progress', {
      user_id: userId,
      quiz_type: quizType,
      is_correct: isCorrect,
      vocabulary_id: vocabId,
    });
    return response.data;
  },

  /**
   * Get user statistics
   */
  getStats: async (userId: string): Promise<UserProgress> => {
    const response = await api.get(`/api/user/${userId}/stats`);
    return response.data;
  },
};

// ==================== HEALTH CHECK ====================

export const healthApi = {
  check: async (): Promise<{ status: string; data_available: boolean }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
