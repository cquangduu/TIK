// store/lessonStore.ts
// Zustand store for lesson data management

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { lessonApi, LessonData, VocabularyItem, QuizQuestion } from '../services/api';

interface LessonState {
  // Data
  currentLesson: LessonData | null;
  vocabulary: VocabularyItem[];
  vocabQuiz: QuizQuestion | null;
  grammarQuiz: QuizQuestion | null;
  
  // Loading states
  isLoading: boolean;
  error: string | null;
  
  // User progress
  learnedVocabIds: number[];
  vocabQuizCompleted: boolean;
  grammarQuizCompleted: boolean;
  vocabQuizCorrect: boolean;
  grammarQuizCorrect: boolean;
  
  // Actions
  fetchTodayLesson: () => Promise<void>;
  fetchVocabulary: () => Promise<void>;
  fetchVocabQuiz: () => Promise<void>;
  fetchGrammarQuiz: () => Promise<void>;
  
  markVocabLearned: (vocabId: number) => void;
  setVocabQuizResult: (correct: boolean) => void;
  setGrammarQuizResult: (correct: boolean) => void;
  resetDailyProgress: () => void;
  
  // Computed
  getTodayProgress: () => {
    vocabLearned: number;
    vocabTotal: number;
    quizCompleted: number;
    quizTotal: number;
  };
}

export const useLessonStore = create<LessonState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentLesson: null,
      vocabulary: [],
      vocabQuiz: null,
      grammarQuiz: null,
      isLoading: false,
      error: null,
      learnedVocabIds: [],
      vocabQuizCompleted: false,
      grammarQuizCompleted: false,
      vocabQuizCorrect: false,
      grammarQuizCorrect: false,

      // Fetch today's complete lesson
      fetchTodayLesson: async () => {
        set({ isLoading: true, error: null });
        try {
          const lesson = await lessonApi.getToday();
          set({ 
            currentLesson: lesson,
            vocabulary: lesson.vocabulary,
            vocabQuiz: lesson.vocab_quiz || null,
            grammarQuiz: lesson.grammar_quiz || null,
            isLoading: false,
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to fetch lesson',
            isLoading: false,
          });
        }
      },

      // Fetch vocabulary list
      fetchVocabulary: async () => {
        set({ isLoading: true, error: null });
        try {
          const vocabulary = await lessonApi.getVocabulary(50, 0);
          set({ vocabulary, isLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to fetch vocabulary',
            isLoading: false,
          });
        }
      },

      // Fetch vocab quiz
      fetchVocabQuiz: async () => {
        set({ isLoading: true, error: null });
        try {
          const quiz = await lessonApi.getVocabQuiz();
          set({ vocabQuiz: quiz, isLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to fetch quiz',
            isLoading: false,
          });
        }
      },

      // Fetch grammar quiz
      fetchGrammarQuiz: async () => {
        set({ isLoading: true, error: null });
        try {
          const quiz = await lessonApi.getGrammarQuiz();
          set({ grammarQuiz: quiz, isLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to fetch quiz',
            isLoading: false,
          });
        }
      },

      // Mark vocabulary as learned
      markVocabLearned: (vocabId: number) => {
        const { learnedVocabIds } = get();
        if (!learnedVocabIds.includes(vocabId)) {
          set({ learnedVocabIds: [...learnedVocabIds, vocabId] });
        }
      },

      // Set vocab quiz result
      setVocabQuizResult: (correct: boolean) => {
        set({ 
          vocabQuizCompleted: true,
          vocabQuizCorrect: correct,
        });
      },

      // Set grammar quiz result
      setGrammarQuizResult: (correct: boolean) => {
        set({ 
          grammarQuizCompleted: true,
          grammarQuizCorrect: correct,
        });
      },

      // Reset daily progress (call at midnight or new day)
      resetDailyProgress: () => {
        set({
          learnedVocabIds: [],
          vocabQuizCompleted: false,
          grammarQuizCompleted: false,
          vocabQuizCorrect: false,
          grammarQuizCorrect: false,
        });
      },

      // Get today's progress summary
      getTodayProgress: () => {
        const state = get();
        const quizCompleted = 
          (state.vocabQuizCompleted ? 1 : 0) + 
          (state.grammarQuizCompleted ? 1 : 0);
        
        return {
          vocabLearned: state.learnedVocabIds.length,
          vocabTotal: state.vocabulary.length,
          quizCompleted,
          quizTotal: 2,
        };
      },
    }),
    {
      name: 'topik-lesson-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        learnedVocabIds: state.learnedVocabIds,
        vocabQuizCompleted: state.vocabQuizCompleted,
        grammarQuizCompleted: state.grammarQuizCompleted,
        vocabQuizCorrect: state.vocabQuizCorrect,
        grammarQuizCorrect: state.grammarQuizCorrect,
      }),
    }
  )
);
