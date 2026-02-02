// app/(tabs)/profile.tsx
// User profile and settings screen

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useUserStore } from '../../src/store/userStore';
import { usePremium } from '../../src/hooks/usePremium';
import AdBanner from '../../src/components/AdBanner';

export default function ProfileScreen() {
  const {
    displayName,
    currentStreak,
    longestStreak,
    totalVocabLearned,
    totalQuizzesCompleted,
    totalCorrectAnswers,
    notifications,
    showVietnamese,
    dailyGoal,
    toggleNotifications,
    toggleVietnamese,
    getWeeklyStats,
  } = useUserStore();

  const { isPremium, restorePurchases } = usePremium();

  const weeklyStats = getWeeklyStats();
  const accuracy = totalQuizzesCompleted > 0 
    ? Math.round((totalCorrectAnswers / totalQuizzesCompleted) * 100) 
    : 0;

  const handleRestorePurchases = async () => {
    const restored = await restorePurchases();
    if (restored) {
      Alert.alert('Thành công', 'Đã khôi phục gói Premium của bạn!');
    } else {
      Alert.alert('Không tìm thấy', 'Không tìm thấy giao dịch Premium nào.');
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <Ionicons name="person-circle" size={80} color="#4A90D9" />
            {isPremium && (
              <View style={styles.premiumBadge}>
                <Ionicons name="star" size={16} color="#FFD700" />
              </View>
            )}
          </View>
          <Text style={styles.displayName}>{displayName}</Text>
          {isPremium && (
            <View style={styles.premiumTag}>
              <Ionicons name="star" size={12} color="#FFD700" />
              <Text style={styles.premiumTagText}>Premium</Text>
            </View>
          )}
        </View>

        {/* Streak Card */}
        <View style={styles.streakCard}>
          <View style={styles.streakMain}>
            <Ionicons name="flame" size={48} color="#FF6B35" />
            <Text style={styles.streakNumber}>{currentStreak}</Text>
            <Text style={styles.streakLabel}>ngày liên tiếp</Text>
          </View>
          <View style={styles.streakDivider} />
          <View style={styles.streakBest}>
            <Text style={styles.streakBestLabel}>Kỷ lục</Text>
            <Text style={styles.streakBestNumber}>{longestStreak} ngày</Text>
          </View>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{totalVocabLearned}</Text>
            <Text style={styles.statLabel}>Từ đã học</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{totalQuizzesCompleted}</Text>
            <Text style={styles.statLabel}>Quiz đã làm</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{accuracy}%</Text>
            <Text style={styles.statLabel}>Độ chính xác</Text>
          </View>
        </View>

        {/* Weekly Stats */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tuần này</Text>
          <View style={styles.weeklyStats}>
            <View style={styles.weeklyStat}>
              <Text style={styles.weeklyStatNumber}>{weeklyStats.vocabLearned}</Text>
              <Text style={styles.weeklyStatLabel}>Từ vựng</Text>
            </View>
            <View style={styles.weeklyStatDivider} />
            <View style={styles.weeklyStat}>
              <Text style={styles.weeklyStatNumber}>{weeklyStats.quizzesCompleted}</Text>
              <Text style={styles.weeklyStatLabel}>Quiz</Text>
            </View>
            <View style={styles.weeklyStatDivider} />
            <View style={styles.weeklyStat}>
              <Text style={styles.weeklyStatNumber}>{weeklyStats.accuracy}%</Text>
              <Text style={styles.weeklyStatLabel}>Chính xác</Text>
            </View>
          </View>
        </View>

        {/* Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cài đặt</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Ionicons name="notifications" size={24} color="#4A90D9" />
              <Text style={styles.settingLabel}>Thông báo hàng ngày</Text>
            </View>
            <Switch
              value={notifications}
              onValueChange={toggleNotifications}
              trackColor={{ false: '#E0E0E0', true: '#81C784' }}
              thumbColor={notifications ? '#4CAF50' : '#FFF'}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Ionicons name="language" size={24} color="#4A90D9" />
              <Text style={styles.settingLabel}>Hiện bản dịch tiếng Việt</Text>
            </View>
            <Switch
              value={showVietnamese}
              onValueChange={toggleVietnamese}
              trackColor={{ false: '#E0E0E0', true: '#81C784' }}
              thumbColor={showVietnamese ? '#4CAF50' : '#FFF'}
            />
          </View>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Ionicons name="flag" size={24} color="#4A90D9" />
              <Text style={styles.settingLabel}>Mục tiêu hàng ngày</Text>
            </View>
            <View style={styles.settingValue}>
              <Text style={styles.settingValueText}>{dailyGoal} từ</Text>
              <Ionicons name="chevron-forward" size={20} color="#999" />
            </View>
          </TouchableOpacity>
        </View>

        {/* Premium Section */}
        {!isPremium && (
          <View style={styles.section}>
            <TouchableOpacity 
              style={styles.premiumBanner}
              onPress={() => router.push('/premium')}
            >
              <View style={styles.premiumBannerContent}>
                <Ionicons name="star" size={32} color="#FFD700" />
                <View style={styles.premiumBannerText}>
                  <Text style={styles.premiumBannerTitle}>Nâng cấp Premium</Text>
                  <Text style={styles.premiumBannerDesc}>
                    Không quảng cáo • Tất cả tính năng • Archive 30+ ngày
                  </Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#FFF" />
            </TouchableOpacity>
          </View>
        )}

        {/* Other Options */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.menuItem} onPress={handleRestorePurchases}>
            <Ionicons name="refresh" size={24} color="#666" />
            <Text style={styles.menuLabel}>Khôi phục mua hàng</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem}>
            <Ionicons name="help-circle" size={24} color="#666" />
            <Text style={styles.menuLabel}>Trợ giúp & FAQ</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem}>
            <Ionicons name="star-outline" size={24} color="#666" />
            <Text style={styles.menuLabel}>Đánh giá ứng dụng</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem}>
            <Ionicons name="share-social" size={24} color="#666" />
            <Text style={styles.menuLabel}>Chia sẻ với bạn bè</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem}>
            <Ionicons name="document-text" size={24} color="#666" />
            <Text style={styles.menuLabel}>Chính sách bảo mật</Text>
          </TouchableOpacity>
        </View>

        {/* App Version */}
        <View style={styles.footer}>
          <Text style={styles.version}>TOPIK Daily v1.0.0</Text>
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
  scrollView: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 24,
    backgroundColor: '#FFF',
  },
  avatarContainer: {
    position: 'relative',
  },
  premiumBadge: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  displayName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 12,
  },
  premiumTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3E0',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 8,
  },
  premiumTagText: {
    marginLeft: 4,
    fontSize: 12,
    color: '#FF9800',
    fontWeight: '600',
  },
  streakCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  streakMain: {
    flex: 1,
    alignItems: 'center',
  },
  streakNumber: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FF6B35',
    marginTop: 8,
  },
  streakLabel: {
    fontSize: 14,
    color: '#666',
  },
  streakDivider: {
    width: 1,
    backgroundColor: '#E0E0E0',
    marginHorizontal: 16,
  },
  streakBest: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  streakBestLabel: {
    fontSize: 12,
    color: '#666',
  },
  streakBestNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4A90D9',
    marginTop: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    paddingHorizontal: 8,
    marginTop: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 8,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90D9',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  section: {
    marginTop: 24,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  weeklyStats: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
  },
  weeklyStat: {
    flex: 1,
    alignItems: 'center',
  },
  weeklyStatNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4A90D9',
  },
  weeklyStatLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  weeklyStatDivider: {
    width: 1,
    backgroundColor: '#E0E0E0',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
    marginLeft: 12,
  },
  settingValue: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingValueText: {
    fontSize: 14,
    color: '#666',
    marginRight: 4,
  },
  premiumBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#2E5A88',
    borderRadius: 16,
    padding: 16,
  },
  premiumBannerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  premiumBannerText: {
    marginLeft: 12,
    flex: 1,
  },
  premiumBannerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFF',
  },
  premiumBannerDesc: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 2,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
  },
  menuLabel: {
    fontSize: 16,
    color: '#333',
    marginLeft: 12,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  version: {
    fontSize: 12,
    color: '#999',
  },
});
