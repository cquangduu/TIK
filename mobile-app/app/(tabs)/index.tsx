// app/(tabs)/index.tsx
// Home Screen - Today's lesson overview

import React, { useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useLessonStore } from '../../src/store/lessonStore';
import { useUserStore } from '../../src/store/userStore';
import AdBanner from '../../src/components/AdBanner';

export default function HomeScreen() {
  const { 
    currentLesson, 
    vocabulary,
    isLoading, 
    error,
    fetchTodayLesson,
    getTodayProgress,
  } = useLessonStore();
  
  const { 
    currentStreak, 
    isPremium,
    displayName,
    initUser,
  } = useUserStore();

  const progress = getTodayProgress();

  const onRefresh = useCallback(async () => {
    await fetchTodayLesson();
  }, [fetchTodayLesson]);

  useEffect(() => {
    initUser();
    fetchTodayLesson();
  }, []);

  if (isLoading && !currentLesson) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4A90D9" />
        <Text style={styles.loadingText}>Đang tải bài học...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="cloud-offline" size={64} color="#999" />
        <Text style={styles.errorText}>Không thể tải dữ liệu</Text>
        <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
          <Text style={styles.retryButtonText}>Thử lại</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const menuItems = [
    { 
      icon: 'book', 
      color: '#4A90D9', 
      title: 'Từ Vựng', 
      desc: `${progress.vocabLearned}/${progress.vocabTotal} từ`,
      route: '/vocabulary',
      badge: progress.vocabTotal - progress.vocabLearned,
    },
    { 
      icon: 'checkmark-circle', 
      color: '#4CAF50', 
      title: 'Quiz', 
      desc: `${progress.quizCompleted}/2 hoàn thành`,
      route: '/quiz',
      badge: 2 - progress.quizCompleted,
    },
    { 
      icon: 'newspaper', 
      color: '#FF9800', 
      title: 'Tin Tức', 
      desc: 'Đọc tin tiếng Hàn',
      route: '/news',
      badge: 0,
    },
    { 
      icon: 'create', 
      color: '#9C27B0', 
      title: 'Viết', 
      desc: 'Bài văn mẫu TOPIK',
      route: '/essay',
      badge: 0,
    },
  ];

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl 
            refreshing={isLoading} 
            onRefresh={onRefresh}
            colors={['#4A90D9']}
          />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Xin chào, {displayName}!</Text>
              <Text style={styles.date}>{currentLesson?.date || 'Hôm nay'}</Text>
            </View>
            <TouchableOpacity 
              style={styles.streakBadge}
              onPress={() => router.push('/profile')}
            >
              <Ionicons name="flame" size={20} color="#FF6B35" />
              <Text style={styles.streakText}>{currentStreak}</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.topic}>{currentLesson?.topic || 'TOPIK Daily'}</Text>
        </View>

        {/* Progress Card */}
        <View style={styles.progressCard}>
          <Text style={styles.progressTitle}>Tiến độ hôm nay</Text>
          <View style={styles.progressItems}>
            <View style={styles.progressItem}>
              <View style={styles.progressCircle}>
                <Text style={styles.progressNumber}>{progress.vocabLearned}</Text>
              </View>
              <Text style={styles.progressLabel}>Từ vựng</Text>
            </View>
            <View style={styles.progressDivider} />
            <View style={styles.progressItem}>
              <View style={styles.progressCircle}>
                <Text style={styles.progressNumber}>{progress.quizCompleted}</Text>
              </View>
              <Text style={styles.progressLabel}>Quiz</Text>
            </View>
            <View style={styles.progressDivider} />
            <View style={styles.progressItem}>
              <View style={[styles.progressCircle, styles.streakCircle]}>
                <Ionicons name="flame" size={24} color="#FF6B35" />
              </View>
              <Text style={styles.progressLabel}>{currentStreak} ngày</Text>
            </View>
          </View>
        </View>

        {/* Menu Grid */}
        <View style={styles.menuContainer}>
          {menuItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.menuCard}
              onPress={() => router.push(item.route as any)}
              activeOpacity={0.7}
            >
              <View style={[styles.iconContainer, { backgroundColor: `${item.color}20` }]}>
                <Ionicons name={item.icon as any} size={28} color={item.color} />
              </View>
              <Text style={styles.menuTitle}>{item.title}</Text>
              <Text style={styles.menuDesc}>{item.desc}</Text>
              {item.badge > 0 && (
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>{item.badge}</Text>
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>

        {/* Premium Banner (for non-premium users) */}
        {!isPremium && (
          <TouchableOpacity 
            style={styles.premiumBanner}
            onPress={() => router.push('/premium')}
          >
            <View style={styles.premiumContent}>
              <Ionicons name="star" size={24} color="#FFD700" />
              <View style={styles.premiumText}>
                <Text style={styles.premiumTitle}>Nâng cấp Premium</Text>
                <Text style={styles.premiumDesc}>Không quảng cáo + Tất cả tính năng</Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#FFF" />
          </TouchableOpacity>
        )}

        <View style={styles.bottomPadding} />
      </ScrollView>

      {/* Ad Banner */}
      <AdBanner isPremium={isPremium} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  scrollView: {
    flex: 1,
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F7FA',
    padding: 32,
  },
  errorText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 24,
    backgroundColor: '#4A90D9',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 24,
  },
  retryButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    backgroundColor: '#4A90D9',
    padding: 20,
    paddingTop: 60,
    paddingBottom: 32,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  greeting: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
  },
  date: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.6)',
    marginTop: 2,
  },
  streakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  streakText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 4,
  },
  topic: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  progressCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: 16,
    marginTop: -16,
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  progressTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    textAlign: 'center',
  },
  progressItems: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  progressItem: {
    alignItems: 'center',
  },
  progressCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  streakCircle: {
    backgroundColor: '#FFF3E0',
  },
  progressNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4A90D9',
  },
  progressLabel: {
    fontSize: 12,
    color: '#666',
  },
  progressDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#E0E0E0',
  },
  menuContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
    marginTop: 16,
  },
  menuCard: {
    width: '46%',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    margin: '2%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  menuTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  menuDesc: {
    fontSize: 12,
    color: '#999',
  },
  badge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: '#F44336',
    width: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  premiumBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#2E5A88',
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 16,
    padding: 16,
  },
  premiumContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  premiumText: {
    marginLeft: 12,
  },
  premiumTitle: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  premiumDesc: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 12,
    marginTop: 2,
  },
  bottomPadding: {
    height: 24,
  },
});
