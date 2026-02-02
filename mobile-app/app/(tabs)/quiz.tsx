// app/(tabs)/quiz.tsx
// Quiz screen with vocabulary and grammar quizzes

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useLessonStore } from '../../src/store/lessonStore';
import { useUserStore } from '../../src/store/userStore';
import QuizQuestion from '../../src/components/QuizQuestion';
import AdBanner from '../../src/components/AdBanner';
import type { QuizQuestion as QuizQuestionType } from '../../src/services/api';

type QuizMode = 'select' | 'vocab' | 'grammar' | 'complete';

export default function QuizScreen() {
  const { 
    vocabQuiz, 
    grammarQuiz, 
    isLoading,
    fetchVocabQuiz,
    fetchGrammarQuiz,
    vocabQuizCompleted,
    grammarQuizCompleted,
    setVocabQuizResult,
    setGrammarQuizResult,
  } = useLessonStore();

  const { 
    isPremium,
    showVietnamese,
    recordQuizResult,
  } = useUserStore();

  const [mode, setMode] = useState<QuizMode>('select');
  const [currentQuiz, setCurrentQuiz] = useState<QuizQuestionType | null>(null);

  useEffect(() => {
    if (!vocabQuiz) fetchVocabQuiz();
    if (!grammarQuiz) fetchGrammarQuiz();
  }, []);

  const handleStartVocabQuiz = () => {
    if (vocabQuiz) {
      setCurrentQuiz(vocabQuiz);
      setMode('vocab');
    }
  };

  const handleStartGrammarQuiz = () => {
    if (grammarQuiz) {
      setCurrentQuiz(grammarQuiz);
      setMode('grammar');
    }
  };

  const handleQuizAnswer = async (isCorrect: boolean) => {
    if (mode === 'vocab') {
      setVocabQuizResult(isCorrect);
      await recordQuizResult('vocab', isCorrect);
    } else if (mode === 'grammar') {
      setGrammarQuizResult(isCorrect);
      await recordQuizResult('grammar', isCorrect);
    }
  };

  const handleNext = () => {
    if (mode === 'vocab' && !grammarQuizCompleted && grammarQuiz) {
      setCurrentQuiz(grammarQuiz);
      setMode('grammar');
    } else {
      setMode('complete');
    }
  };

  const handleReset = () => {
    setMode('select');
    setCurrentQuiz(null);
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4A90D9" />
        <Text style={styles.loadingText}>Đang tải quiz...</Text>
      </View>
    );
  }

  // Quiz Complete Screen
  if (mode === 'complete') {
    const vocabCorrect = vocabQuizCompleted ? 1 : 0;
    const grammarCorrect = grammarQuizCompleted ? 1 : 0;
    const total = 2;
    const correct = vocabCorrect + grammarCorrect;

    return (
      <View style={styles.container}>
        <View style={styles.completeContainer}>
          <Ionicons 
            name={correct === total ? 'trophy' : 'medal'} 
            size={80} 
            color={correct === total ? '#FFD700' : '#C0C0C0'} 
          />
          <Text style={styles.completeTitle}>
            {correct === total ? 'Xuất sắc! 🎉' : 'Hoàn thành!'}
          </Text>
          <Text style={styles.completeScore}>
            {correct}/{total} câu đúng
          </Text>
          <View style={styles.resultGrid}>
            <View style={[styles.resultCard, vocabQuizCompleted && styles.resultCorrect]}>
              <Text style={styles.resultLabel}>Từ vựng</Text>
              <Ionicons 
                name={vocabQuizCompleted ? 'checkmark-circle' : 'close-circle'} 
                size={32} 
                color={vocabQuizCompleted ? '#4CAF50' : '#F44336'} 
              />
            </View>
            <View style={[styles.resultCard, grammarQuizCompleted && styles.resultCorrect]}>
              <Text style={styles.resultLabel}>Ngữ pháp</Text>
              <Ionicons 
                name={grammarQuizCompleted ? 'checkmark-circle' : 'close-circle'} 
                size={32} 
                color={grammarQuizCompleted ? '#4CAF50' : '#F44336'} 
              />
            </View>
          </View>
          <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
            <Ionicons name="arrow-back" size={20} color="#FFF" />
            <Text style={styles.resetButtonText}>Quay lại</Text>
          </TouchableOpacity>
        </View>
        <AdBanner isPremium={isPremium} />
      </View>
    );
  }

  // Quiz Question Screen
  if (mode === 'vocab' || mode === 'grammar') {
    return (
      <View style={styles.container}>
        <View style={styles.quizHeader}>
          <TouchableOpacity onPress={handleReset} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.quizTitle}>
            {mode === 'vocab' ? 'Quiz Từ Vựng' : 'Quiz Ngữ Pháp'}
          </Text>
          <View style={styles.placeholder} />
        </View>
        <ScrollView style={styles.quizContent}>
          {currentQuiz && (
            <QuizQuestion
              question={currentQuiz}
              onAnswer={handleQuizAnswer}
              showVietnamese={showVietnamese}
              onNext={handleNext}
            />
          )}
        </ScrollView>
        <AdBanner isPremium={isPremium} />
      </View>
    );
  }

  // Quiz Selection Screen
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Quiz Hôm Nay</Text>
        <Text style={styles.subtitle}>Kiểm tra kiến thức của bạn</Text>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {/* Vocab Quiz Card */}
        <TouchableOpacity 
          style={[
            styles.quizCard,
            vocabQuizCompleted && styles.quizCardCompleted
          ]}
          onPress={handleStartVocabQuiz}
          disabled={!vocabQuiz}
        >
          <View style={[styles.quizIcon, { backgroundColor: '#E3F2FD' }]}>
            <Ionicons name="book" size={32} color="#4A90D9" />
          </View>
          <View style={styles.quizInfo}>
            <Text style={styles.quizCardTitle}>Quiz Từ Vựng</Text>
            <Text style={styles.quizCardDesc}>
              {vocabQuiz ? `Từ: ${vocabQuiz.target}` : 'Đang tải...'}
            </Text>
          </View>
          {vocabQuizCompleted ? (
            <Ionicons name="checkmark-circle" size={32} color="#4CAF50" />
          ) : (
            <Ionicons name="play-circle" size={32} color="#4A90D9" />
          )}
        </TouchableOpacity>

        {/* Grammar Quiz Card */}
        <TouchableOpacity 
          style={[
            styles.quizCard,
            grammarQuizCompleted && styles.quizCardCompleted
          ]}
          onPress={handleStartGrammarQuiz}
          disabled={!grammarQuiz}
        >
          <View style={[styles.quizIcon, { backgroundColor: '#E8F5E9' }]}>
            <Ionicons name="create" size={32} color="#4CAF50" />
          </View>
          <View style={styles.quizInfo}>
            <Text style={styles.quizCardTitle}>Quiz Ngữ Pháp</Text>
            <Text style={styles.quizCardDesc}>
              {grammarQuiz ? `Ngữ pháp: ${grammarQuiz.target}` : 'Đang tải...'}
            </Text>
          </View>
          {grammarQuizCompleted ? (
            <Ionicons name="checkmark-circle" size={32} color="#4CAF50" />
          ) : (
            <Ionicons name="play-circle" size={32} color="#4CAF50" />
          )}
        </TouchableOpacity>

        {/* Progress Summary */}
        <View style={styles.progressSummary}>
          <Text style={styles.progressTitle}>Tiến độ</Text>
          <View style={styles.progressRow}>
            <View style={[styles.progressDot, vocabQuizCompleted && styles.progressDotActive]} />
            <View style={[styles.progressDot, grammarQuizCompleted && styles.progressDotActive]} />
          </View>
          <Text style={styles.progressText}>
            {(vocabQuizCompleted ? 1 : 0) + (grammarQuizCompleted ? 1 : 0)}/2 hoàn thành
          </Text>
        </View>

        {/* Tips */}
        <View style={styles.tipsCard}>
          <Ionicons name="bulb" size={24} color="#FF9800" />
          <Text style={styles.tipsText}>
            💡 Mẹo: Hoàn thành quiz hàng ngày để duy trì streak và ghi nhớ tốt hơn!
          </Text>
        </View>
      </ScrollView>

      <AdBanner isPremium={isPremium} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F7FA',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  quizCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  quizCardCompleted: {
    backgroundColor: '#F1F8E9',
    borderWidth: 1,
    borderColor: '#C5E1A5',
  },
  quizIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quizInfo: {
    flex: 1,
    marginLeft: 12,
  },
  quizCardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  quizCardDesc: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  progressSummary: {
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    marginTop: 8,
    marginBottom: 16,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  progressRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 8,
  },
  progressDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#E0E0E0',
  },
  progressDotActive: {
    backgroundColor: '#4CAF50',
  },
  progressText: {
    fontSize: 14,
    color: '#666',
  },
  tipsCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3E0',
    borderRadius: 12,
    padding: 16,
  },
  tipsText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: '#E65100',
    lineHeight: 20,
  },
  quizHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 16,
  },
  backButton: {
    padding: 8,
  },
  quizTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  placeholder: {
    width: 40,
  },
  quizContent: {
    flex: 1,
  },
  completeContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  completeTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 24,
  },
  completeScore: {
    fontSize: 18,
    color: '#666',
    marginTop: 8,
    marginBottom: 32,
  },
  resultGrid: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 32,
  },
  resultCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    minWidth: 120,
    borderWidth: 2,
    borderColor: '#FFE0E0',
  },
  resultCorrect: {
    borderColor: '#C8E6C9',
    backgroundColor: '#F1F8E9',
  },
  resultLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  resetButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4A90D9',
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 28,
    gap: 8,
  },
  resetButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
