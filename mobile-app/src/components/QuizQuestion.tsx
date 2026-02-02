// components/QuizQuestion.tsx
// Interactive quiz component with answer feedback

import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Animated,
  Dimensions 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { QuizQuestion as QuizQuestionType } from '../services/api';

const { width } = Dimensions.get('window');

interface QuizQuestionProps {
  question: QuizQuestionType;
  onAnswer: (isCorrect: boolean) => void;
  showVietnamese?: boolean;
  onNext?: () => void;
}

export default function QuizQuestion({ 
  question, 
  onAnswer, 
  showVietnamese = true,
  onNext,
}: QuizQuestionProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const fadeAnim = new Animated.Value(0);

  const handleAnswer = (answer: string) => {
    if (showResult) return;
    
    setSelectedAnswer(answer);
    setShowResult(true);
    
    // Animate explanation in
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
    
    const isCorrect = answer === question.correct_answer;
    onAnswer(isCorrect);
  };

  const getOptionStyle = (option: string) => {
    const baseStyle = [styles.option];
    
    if (!showResult) {
      return baseStyle;
    }
    
    if (option === question.correct_answer) {
      return [...baseStyle, styles.correctOption];
    }
    
    if (option === selectedAnswer && option !== question.correct_answer) {
      return [...baseStyle, styles.wrongOption];
    }
    
    return [...baseStyle, styles.disabledOption];
  };

  const getOptionIcon = (option: string) => {
    if (!showResult) return null;
    
    if (option === question.correct_answer) {
      return <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />;
    }
    
    if (option === selectedAnswer && option !== question.correct_answer) {
      return <Ionicons name="close-circle" size={24} color="#F44336" />;
    }
    
    return null;
  };

  const options = showVietnamese ? question.options_vi : question.options_ko;
  const questionText = showVietnamese ? question.question_vi : question.question_ko;
  const isCorrect = selectedAnswer === question.correct_answer;

  return (
    <View style={styles.container}>
      {/* Question Header */}
      <View style={styles.header}>
        <View style={styles.typeTag}>
          <Text style={styles.typeText}>
            {question.type === 'vocab' ? '📚 Từ vựng' : '📝 Ngữ pháp'}
          </Text>
        </View>
      </View>

      {/* Target Word/Grammar */}
      <View style={styles.targetContainer}>
        <Text style={styles.target}>{question.target}</Text>
      </View>

      {/* Question Text */}
      <View style={styles.questionContainer}>
        <Text style={styles.question}>{questionText}</Text>
      </View>

      {/* Options */}
      <View style={styles.optionsContainer}>
        {options.map((option, index) => (
          <TouchableOpacity
            key={index}
            style={getOptionStyle(option)}
            onPress={() => handleAnswer(option)}
            disabled={showResult}
            activeOpacity={0.7}
          >
            <View style={styles.optionLabelContainer}>
              <Text style={styles.optionLabel}>
                {String.fromCharCode(65 + index)}
              </Text>
            </View>
            <Text style={styles.optionText}>{option}</Text>
            <View style={styles.optionIcon}>
              {getOptionIcon(option)}
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* Result & Explanation */}
      {showResult && (
        <Animated.View 
          style={[
            styles.explanationContainer,
            { opacity: fadeAnim },
            isCorrect ? styles.correctExplanation : styles.wrongExplanation,
          ]}
        >
          <View style={styles.resultHeader}>
            <Ionicons 
              name={isCorrect ? 'trophy' : 'sad'} 
              size={32} 
              color={isCorrect ? '#FFC107' : '#FF6B6B'} 
            />
            <Text style={styles.resultTitle}>
              {isCorrect ? 'Chính xác! 🎉' : 'Chưa đúng!'}
            </Text>
          </View>
          
          <Text style={styles.correctAnswerLabel}>Đáp án đúng:</Text>
          <Text style={styles.correctAnswerText}>{question.correct_answer}</Text>
          
          <View style={styles.divider} />
          
          <Text style={styles.explanationLabel}>Giải thích:</Text>
          <Text style={styles.explanationText}>
            {showVietnamese ? question.explanation_vi : question.explanation_ko}
          </Text>
          
          {onNext && (
            <TouchableOpacity style={styles.nextButton} onPress={onNext}>
              <Text style={styles.nextButtonText}>Tiếp tục</Text>
              <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
            </TouchableOpacity>
          )}
        </Animated.View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  typeTag: {
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  typeText: {
    fontSize: 14,
    color: '#1976D2',
    fontWeight: '600',
  },
  targetContainer: {
    backgroundColor: '#4A90D9',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
  },
  target: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
  },
  questionContainer: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  question: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    lineHeight: 24,
  },
  optionsContainer: {
    gap: 12,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
    borderColor: '#E0E0E0',
  },
  correctOption: {
    borderColor: '#4CAF50',
    backgroundColor: '#E8F5E9',
  },
  wrongOption: {
    borderColor: '#F44336',
    backgroundColor: '#FFEBEE',
  },
  disabledOption: {
    opacity: 0.5,
  },
  optionLabelContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#4A90D9',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  optionLabel: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  optionText: {
    flex: 1,
    fontSize: 16,
    color: '#333',
    lineHeight: 22,
  },
  optionIcon: {
    marginLeft: 8,
  },
  explanationContainer: {
    marginTop: 24,
    borderRadius: 16,
    padding: 20,
  },
  correctExplanation: {
    backgroundColor: '#E8F5E9',
    borderWidth: 1,
    borderColor: '#A5D6A7',
  },
  wrongExplanation: {
    backgroundColor: '#FFF3E0',
    borderWidth: 1,
    borderColor: '#FFCC80',
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 8,
    color: '#333',
  },
  correctAnswerLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  correctAnswerText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4CAF50',
    marginBottom: 12,
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(0,0,0,0.1)',
    marginVertical: 12,
  },
  explanationLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  explanationText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 22,
  },
  nextButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4A90D9',
    borderRadius: 24,
    paddingVertical: 14,
    marginTop: 20,
  },
  nextButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
});
