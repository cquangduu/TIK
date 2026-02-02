// store/userStore.ts
// Zustand store for user data and progress tracking

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { progressApi } from '../services/api';
import * as Crypto from 'expo-crypto';

interface DailyProgress {
  date: string;
  vocabLearned: number;
  quizzesCompleted: number;
  quizzesCorrect: number;
}

interface UserState {
  // User info
  userId: string;
  displayName: string;
  isPremium: boolean;
  
  // Stats
  currentStreak: number;
  longestStreak: number;
  totalVocabLearned: number;
  totalQuizzesCompleted: number;
  totalCorrectAnswers: number;
  lastActiveDate: string | null;
  
  // Daily history (last 30 days)
  dailyHistory: DailyProgress[];
  
  // Settings
  notifications: boolean;
  showVietnamese: boolean;
  dailyGoal: number;  // vocabulary count
  
  // Actions
  initUser: () => Promise<void>;
  updateStreak: () => void;
  recordQuizResult: (quizType: string, isCorrect: boolean) => Promise<void>;
  recordVocabLearned: (vocabId: number) => Promise<void>;
  setPremium: (status: boolean) => void;
  setDisplayName: (name: string) => void;
  toggleNotifications: () => void;
  toggleVietnamese: () => void;
  setDailyGoal: (goal: number) => void;
  
  // Computed
  getWeeklyStats: () => {
    vocabLearned: number;
    quizzesCompleted: number;
    accuracy: number;
  };
  getTodayProgress: () => DailyProgress | null;
}

const generateUserId = async (): Promise<string> => {
  const uuid = await Crypto.randomUUID();
  return uuid;
};

const getTodayDate = (): string => {
  return new Date().toISOString().split('T')[0];
};

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      // Initial state
      userId: '',
      displayName: 'Learner',
      isPremium: false,
      currentStreak: 0,
      longestStreak: 0,
      totalVocabLearned: 0,
      totalQuizzesCompleted: 0,
      totalCorrectAnswers: 0,
      lastActiveDate: null,
      dailyHistory: [],
      notifications: true,
      showVietnamese: true,
      dailyGoal: 10,

      // Initialize user (call on app start)
      initUser: async () => {
        const { userId } = get();
        if (!userId) {
          const newId = await generateUserId();
          set({ userId: newId });
        }
        
        // Update streak on app open
        get().updateStreak();
      },

      // Update streak based on last active date
      updateStreak: () => {
        const { lastActiveDate, currentStreak, longestStreak } = get();
        const today = getTodayDate();
        
        if (!lastActiveDate) {
          // First time user
          set({ 
            lastActiveDate: today,
            currentStreak: 1,
            longestStreak: 1,
          });
          return;
        }
        
        if (lastActiveDate === today) {
          // Already updated today
          return;
        }
        
        const lastDate = new Date(lastActiveDate);
        const todayDate = new Date(today);
        const diffTime = todayDate.getTime() - lastDate.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
          // Consecutive day - increase streak
          const newStreak = currentStreak + 1;
          set({ 
            lastActiveDate: today,
            currentStreak: newStreak,
            longestStreak: Math.max(longestStreak, newStreak),
          });
        } else {
          // Streak broken - reset
          set({ 
            lastActiveDate: today,
            currentStreak: 1,
          });
        }
      },

      // Record quiz result
      recordQuizResult: async (quizType: string, isCorrect: boolean) => {
        const { 
          userId, 
          totalQuizzesCompleted, 
          totalCorrectAnswers,
          dailyHistory,
        } = get();
        
        const today = getTodayDate();
        
        // Update totals
        set({
          totalQuizzesCompleted: totalQuizzesCompleted + 1,
          totalCorrectAnswers: isCorrect 
            ? totalCorrectAnswers + 1 
            : totalCorrectAnswers,
        });
        
        // Update daily history
        const todayIndex = dailyHistory.findIndex(d => d.date === today);
        const updatedHistory = [...dailyHistory];
        
        if (todayIndex >= 0) {
          updatedHistory[todayIndex] = {
            ...updatedHistory[todayIndex],
            quizzesCompleted: updatedHistory[todayIndex].quizzesCompleted + 1,
            quizzesCorrect: isCorrect 
              ? updatedHistory[todayIndex].quizzesCorrect + 1
              : updatedHistory[todayIndex].quizzesCorrect,
          };
        } else {
          updatedHistory.push({
            date: today,
            vocabLearned: 0,
            quizzesCompleted: 1,
            quizzesCorrect: isCorrect ? 1 : 0,
          });
        }
        
        // Keep only last 30 days
        const last30Days = updatedHistory.slice(-30);
        set({ dailyHistory: last30Days });
        
        // Sync with server
        try {
          await progressApi.update(userId, quizType, isCorrect);
        } catch (error) {
          console.error('Failed to sync progress:', error);
        }
      },

      // Record vocabulary learned
      recordVocabLearned: async (vocabId: number) => {
        const { 
          userId, 
          totalVocabLearned,
          dailyHistory,
        } = get();
        
        const today = getTodayDate();
        
        // Update total
        set({ totalVocabLearned: totalVocabLearned + 1 });
        
        // Update daily history
        const todayIndex = dailyHistory.findIndex(d => d.date === today);
        const updatedHistory = [...dailyHistory];
        
        if (todayIndex >= 0) {
          updatedHistory[todayIndex] = {
            ...updatedHistory[todayIndex],
            vocabLearned: updatedHistory[todayIndex].vocabLearned + 1,
          };
        } else {
          updatedHistory.push({
            date: today,
            vocabLearned: 1,
            quizzesCompleted: 0,
            quizzesCorrect: 0,
          });
        }
        
        const last30Days = updatedHistory.slice(-30);
        set({ dailyHistory: last30Days });
        
        // Sync with server
        try {
          await progressApi.update(userId, 'vocab', true, vocabId);
        } catch (error) {
          console.error('Failed to sync progress:', error);
        }
      },

      // Set premium status
      setPremium: (status: boolean) => {
        set({ isPremium: status });
      },

      // Set display name
      setDisplayName: (name: string) => {
        set({ displayName: name });
      },

      // Toggle notifications
      toggleNotifications: () => {
        set({ notifications: !get().notifications });
      },

      // Toggle Vietnamese translation display
      toggleVietnamese: () => {
        set({ showVietnamese: !get().showVietnamese });
      },

      // Set daily vocabulary goal
      setDailyGoal: (goal: number) => {
        set({ dailyGoal: goal });
      },

      // Get weekly stats
      getWeeklyStats: () => {
        const { dailyHistory } = get();
        const today = new Date();
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        
        const weekHistory = dailyHistory.filter(d => {
          const date = new Date(d.date);
          return date >= weekAgo && date <= today;
        });
        
        const vocabLearned = weekHistory.reduce((sum, d) => sum + d.vocabLearned, 0);
        const quizzesCompleted = weekHistory.reduce((sum, d) => sum + d.quizzesCompleted, 0);
        const quizzesCorrect = weekHistory.reduce((sum, d) => sum + d.quizzesCorrect, 0);
        const accuracy = quizzesCompleted > 0 
          ? Math.round((quizzesCorrect / quizzesCompleted) * 100)
          : 0;
        
        return { vocabLearned, quizzesCompleted, accuracy };
      },

      // Get today's progress
      getTodayProgress: () => {
        const { dailyHistory } = get();
        const today = getTodayDate();
        return dailyHistory.find(d => d.date === today) || null;
      },
    }),
    {
      name: 'topik-user-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
