// app/(tabs)/vocabulary.tsx
// Vocabulary flashcard screen with swipe functionality

import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Swiper from 'react-native-deck-swiper';
import { useLessonStore } from '../../src/store/lessonStore';
import { useUserStore } from '../../src/store/userStore';
import VocabCard from '../../src/components/VocabCard';
import AdBanner from '../../src/components/AdBanner';
import type { VocabularyItem } from '../../src/services/api';

const { width, height } = Dimensions.get('window');

export default function VocabularyScreen() {
  const { 
    vocabulary, 
    isLoading, 
    fetchVocabulary,
    markVocabLearned,
    learnedVocabIds,
  } = useLessonStore();
  
  const { 
    isPremium,
    recordVocabLearned,
  } = useUserStore();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [finished, setFinished] = useState(false);
  const swiperRef = useRef<Swiper<VocabularyItem>>(null);

  useEffect(() => {
    if (vocabulary.length === 0) {
      fetchVocabulary();
    }
  }, []);

  const handleSwipeRight = (index: number) => {
    // User knows this word
    const vocab = vocabulary[index];
    markVocabLearned(vocab.id);
    recordVocabLearned(vocab.id);
  };

  const handleSwipeLeft = (index: number) => {
    // User needs to review - add to end of deck (in a real app)
    console.log('Review later:', vocabulary[index].word);
  };

  const handleSwiped = (index: number) => {
    setCurrentIndex(index + 1);
    if (index + 1 >= vocabulary.length) {
      setFinished(true);
    }
  };

  const resetDeck = () => {
    setCurrentIndex(0);
    setFinished(false);
    swiperRef.current?.jumpToCardIndex(0);
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4A90D9" />
        <Text style={styles.loadingText}>Đang tải từ vựng...</Text>
      </View>
    );
  }

  if (finished) {
    return (
      <View style={styles.finishedContainer}>
        <View style={styles.finishedContent}>
          <Ionicons name="trophy" size={80} color="#FFD700" />
          <Text style={styles.finishedTitle}>Hoàn thành! 🎉</Text>
          <Text style={styles.finishedText}>
            Bạn đã học xong {vocabulary.length} từ vựng hôm nay
          </Text>
          <View style={styles.statsRow}>
            <View style={styles.statBox}>
              <Text style={styles.statNumber}>{learnedVocabIds.length}</Text>
              <Text style={styles.statLabel}>Đã thuộc</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statNumber}>{vocabulary.length - learnedVocabIds.length}</Text>
              <Text style={styles.statLabel}>Cần ôn</Text>
            </View>
          </View>
          <TouchableOpacity style={styles.resetButton} onPress={resetDeck}>
            <Ionicons name="refresh" size={20} color="#FFF" />
            <Text style={styles.resetButtonText}>Học lại</Text>
          </TouchableOpacity>
        </View>
        <AdBanner isPremium={isPremium} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Từ Vựng Hôm Nay</Text>
        <Text style={styles.progress}>
          {currentIndex + 1} / {vocabulary.length}
        </Text>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressBarContainer}>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill, 
              { width: `${((currentIndex) / vocabulary.length) * 100}%` }
            ]} 
          />
        </View>
      </View>

      {/* Instructions */}
      <View style={styles.instructions}>
        <View style={styles.instructionItem}>
          <Ionicons name="arrow-back" size={16} color="#FF6B6B" />
          <Text style={styles.instructionText}>Ôn lại</Text>
        </View>
        <View style={styles.instructionItem}>
          <Ionicons name="arrow-forward" size={16} color="#4CAF50" />
          <Text style={styles.instructionText}>Đã thuộc</Text>
        </View>
      </View>

      {/* Swiper */}
      <View style={styles.swiperContainer}>
        {vocabulary.length > 0 && (
          <Swiper
            ref={swiperRef}
            cards={vocabulary}
            renderCard={(card) => (
              <VocabCard 
                vocabulary={card}
                onLearn={() => swiperRef.current?.swipeRight()}
                onReview={() => swiperRef.current?.swipeLeft()}
              />
            )}
            onSwipedRight={handleSwipeRight}
            onSwipedLeft={handleSwipeLeft}
            onSwiped={handleSwiped}
            cardIndex={0}
            backgroundColor="transparent"
            stackSize={3}
            stackSeparation={12}
            stackScale={5}
            infinite={false}
            animateOverlayLabelsOpacity
            overlayLabels={{
              left: {
                title: 'ÔN LẠI',
                style: {
                  label: {
                    backgroundColor: '#FF6B6B',
                    color: '#FFF',
                    fontSize: 14,
                    fontWeight: 'bold',
                    borderRadius: 8,
                    padding: 8,
                  },
                  wrapper: {
                    flexDirection: 'column',
                    alignItems: 'flex-end',
                    justifyContent: 'flex-start',
                    marginTop: 24,
                    marginLeft: -24,
                  },
                },
              },
              right: {
                title: 'ĐÃ THUỘC',
                style: {
                  label: {
                    backgroundColor: '#4CAF50',
                    color: '#FFF',
                    fontSize: 14,
                    fontWeight: 'bold',
                    borderRadius: 8,
                    padding: 8,
                  },
                  wrapper: {
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    justifyContent: 'flex-start',
                    marginTop: 24,
                    marginLeft: 24,
                  },
                },
              },
            }}
          />
        )}
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity 
          style={[styles.actionButton, styles.reviewButton]}
          onPress={() => swiperRef.current?.swipeLeft()}
        >
          <Ionicons name="close" size={32} color="#FF6B6B" />
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.actionButton, styles.learnButton]}
          onPress={() => swiperRef.current?.swipeRight()}
        >
          <Ionicons name="checkmark" size={32} color="#4CAF50" />
        </TouchableOpacity>
      </View>

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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  progress: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  progressBarContainer: {
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#E0E0E0',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4A90D9',
    borderRadius: 3,
  },
  instructions: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 32,
    marginBottom: 8,
  },
  instructionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  instructionText: {
    fontSize: 12,
    color: '#666',
  },
  swiperContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 48,
    paddingVertical: 16,
  },
  actionButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  reviewButton: {
    backgroundColor: '#FFF',
    borderWidth: 2,
    borderColor: '#FF6B6B',
  },
  learnButton: {
    backgroundColor: '#FFF',
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  finishedContainer: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  finishedContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  finishedTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 24,
    marginBottom: 8,
  },
  finishedText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 32,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 24,
    marginBottom: 32,
  },
  statBox: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    minWidth: 100,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4A90D9',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
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
