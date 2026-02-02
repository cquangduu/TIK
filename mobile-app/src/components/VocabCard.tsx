// components/VocabCard.tsx
// Flashcard component with flip animation

import React, { useState, useRef } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Animated,
  Dimensions 
} from 'react-native';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import type { VocabularyItem } from '../services/api';

const { width } = Dimensions.get('window');
const CARD_WIDTH = width - 48;
const CARD_HEIGHT = 220;

interface VocabCardProps {
  vocabulary: VocabularyItem;
  onLearn?: () => void;
  onReview?: () => void;
}

export default function VocabCard({ vocabulary, onLearn, onReview }: VocabCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const flipAnim = useRef(new Animated.Value(0)).current;

  const flipCard = () => {
    Animated.spring(flipAnim, {
      toValue: isFlipped ? 0 : 1,
      friction: 8,
      tension: 10,
      useNativeDriver: true,
    }).start();
    setIsFlipped(!isFlipped);
  };

  const playAudio = async () => {
    try {
      // Cleanup previous sound
      if (sound) {
        await sound.unloadAsync();
      }

      if (vocabulary.audio_url) {
        const { sound: newSound } = await Audio.Sound.createAsync(
          { uri: vocabulary.audio_url },
          { shouldPlay: true }
        );
        setSound(newSound);
      }
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  // Interpolations for flip animation
  const frontRotate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '180deg'],
  });

  const backRotate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['180deg', '360deg'],
  });

  const frontOpacity = flipAnim.interpolate({
    inputRange: [0, 0.5, 1],
    outputRange: [1, 0, 0],
  });

  const backOpacity = flipAnim.interpolate({
    inputRange: [0, 0.5, 1],
    outputRange: [0, 0, 1],
  });

  return (
    <View style={styles.container}>
      <TouchableOpacity 
        onPress={flipCard} 
        activeOpacity={0.95}
        style={styles.cardContainer}
      >
        {/* Front Side - Korean Word */}
        <Animated.View
          style={[
            styles.card,
            styles.cardFront,
            {
              transform: [{ rotateY: frontRotate }],
              opacity: frontOpacity,
            },
          ]}
        >
          <View style={styles.cardNumber}>
            <Text style={styles.cardNumberText}>#{vocabulary.id}</Text>
          </View>
          
          <Text style={styles.word}>{vocabulary.word}</Text>
          
          <TouchableOpacity 
            onPress={(e) => {
              e.stopPropagation();
              playAudio();
            }} 
            style={styles.audioButton}
          >
            <Ionicons name="volume-high" size={28} color="#4A90D9" />
            <Text style={styles.audioText}>Nghe phát âm</Text>
          </TouchableOpacity>
          
          <Text style={styles.hint}>👆 Chạm để xem nghĩa</Text>
        </Animated.View>

        {/* Back Side - Vietnamese Meaning */}
        <Animated.View
          style={[
            styles.card,
            styles.cardBack,
            {
              transform: [{ rotateY: backRotate }],
              opacity: backOpacity,
            },
          ]}
        >
          <Text style={styles.meaning}>{vocabulary.meaning}</Text>
          
          {vocabulary.example && (
            <View style={styles.exampleContainer}>
              <Text style={styles.exampleLabel}>Ví dụ:</Text>
              <Text style={styles.example}>{vocabulary.example}</Text>
            </View>
          )}
          
          <View style={styles.actionButtons}>
            <TouchableOpacity 
              onPress={(e) => {
                e.stopPropagation();
                onReview?.();
              }} 
              style={[styles.actionButton, styles.reviewButton]}
            >
              <Ionicons name="refresh" size={20} color="#FF6B6B" />
              <Text style={styles.reviewButtonText}>Ôn lại</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              onPress={(e) => {
                e.stopPropagation();
                onLearn?.();
              }} 
              style={[styles.actionButton, styles.learnButton]}
            >
              <Ionicons name="checkmark" size={20} color="#FFFFFF" />
              <Text style={styles.learnButtonText}>Đã thuộc</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 8,
  },
  cardContainer: {
    width: CARD_WIDTH,
    height: CARD_HEIGHT,
  },
  card: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backfaceVisibility: 'hidden',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
  },
  cardFront: {
    backgroundColor: '#FFFFFF',
  },
  cardBack: {
    backgroundColor: '#4A90D9',
  },
  cardNumber: {
    position: 'absolute',
    top: 16,
    left: 16,
    backgroundColor: '#F0F4F8',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  cardNumberText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  word: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 16,
    textAlign: 'center',
  },
  audioButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0F4F8',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 24,
    marginBottom: 16,
  },
  audioText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#4A90D9',
    fontWeight: '500',
  },
  hint: {
    fontSize: 14,
    color: '#999',
  },
  meaning: {
    fontSize: 20,
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 28,
    fontWeight: '500',
  },
  exampleContainer: {
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    width: '100%',
  },
  exampleLabel: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
    marginBottom: 4,
  },
  example: {
    fontSize: 14,
    color: '#FFFFFF',
    fontStyle: 'italic',
    lineHeight: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 24,
  },
  reviewButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  reviewButtonText: {
    color: '#FFB4B4',
    fontWeight: '600',
    marginLeft: 6,
  },
  learnButton: {
    backgroundColor: '#4CAF50',
  },
  learnButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginLeft: 6,
  },
});
