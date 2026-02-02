// app/premium.tsx
// Premium subscription screen

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { usePremium, PremiumProduct } from '../src/hooks/usePremium';
import { SafeAreaView } from 'react-native-safe-area-context';

const FEATURES = [
  {
    icon: 'ban',
    title: 'Không quảng cáo',
    description: 'Trải nghiệm học tập không bị gián đoạn',
  },
  {
    icon: 'infinite',
    title: 'Truy cập không giới hạn',
    description: 'Xem tất cả bài học, kể cả archive 30+ ngày',
  },
  {
    icon: 'cloud-download',
    title: 'Tải offline',
    description: 'Học mọi lúc, mọi nơi không cần internet',
  },
  {
    icon: 'analytics',
    title: 'Thống kê chi tiết',
    description: 'Theo dõi tiến độ với biểu đồ nâng cao',
  },
  {
    icon: 'headset',
    title: 'Hỗ trợ ưu tiên',
    description: 'Phản hồi nhanh trong 24 giờ',
  },
  {
    icon: 'rocket',
    title: 'Tính năng sớm',
    description: 'Dùng thử các tính năng mới trước tiên',
  },
];

const PLANS = [
  {
    id: 'topik_premium_monthly',
    name: 'Hàng tháng',
    price: '$2.99',
    period: '/tháng',
    savings: null,
  },
  {
    id: 'topik_premium_yearly',
    name: 'Hàng năm',
    price: '$19.99',
    period: '/năm',
    savings: 'Tiết kiệm 44%',
    popular: true,
  },
  {
    id: 'topik_premium_lifetime',
    name: 'Vĩnh viễn',
    price: '$49.99',
    period: 'một lần',
    savings: 'Mua một lần, dùng mãi mãi',
  },
];

export default function PremiumScreen() {
  const { isPremium, loading, products, purchasePremium, restorePurchases } = usePremium();
  const [selectedPlan, setSelectedPlan] = useState('topik_premium_yearly');
  const [purchasing, setPurchasing] = useState(false);

  // If already premium, show confirmation
  if (isPremium) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.successContainer}>
          <View style={styles.successIcon}>
            <Ionicons name="star" size={64} color="#FFD700" />
          </View>
          <Text style={styles.successTitle}>Bạn đã là Premium!</Text>
          <Text style={styles.successText}>
            Cảm ơn bạn đã ủng hộ. Bạn có quyền truy cập tất cả tính năng premium.
          </Text>
          <TouchableOpacity 
            style={styles.successButton}
            onPress={() => router.back()}
          >
            <Text style={styles.successButtonText}>Quay lại học tập</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const handlePurchase = async () => {
    setPurchasing(true);
    try {
      const success = await purchasePremium(selectedPlan);
      if (success) {
        Alert.alert(
          'Thành công! 🎉',
          'Chào mừng bạn đến với Premium! Bạn có thể truy cập tất cả tính năng ngay bây giờ.',
          [{ text: 'OK', onPress: () => router.back() }]
        );
      }
    } catch (error) {
      Alert.alert('Lỗi', 'Không thể hoàn tất giao dịch. Vui lòng thử lại.');
    } finally {
      setPurchasing(false);
    }
  };

  const handleRestore = async () => {
    setPurchasing(true);
    try {
      const restored = await restorePurchases();
      if (restored) {
        Alert.alert('Thành công', 'Đã khôi phục gói Premium của bạn!', [
          { text: 'OK', onPress: () => router.back() }
        ]);
      } else {
        Alert.alert('Không tìm thấy', 'Không tìm thấy giao dịch Premium nào.');
      }
    } finally {
      setPurchasing(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.closeButton} 
          onPress={() => router.back()}
        >
          <Ionicons name="close" size={28} color="#333" />
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Hero */}
        <View style={styles.hero}>
          <View style={styles.heroIcon}>
            <Ionicons name="star" size={48} color="#FFD700" />
          </View>
          <Text style={styles.heroTitle}>TOPIK Daily Premium</Text>
          <Text style={styles.heroSubtitle}>
            Mở khóa tất cả tính năng để học hiệu quả hơn
          </Text>
        </View>

        {/* Features */}
        <View style={styles.features}>
          {FEATURES.map((feature, index) => (
            <View key={index} style={styles.featureItem}>
              <View style={styles.featureIcon}>
                <Ionicons name={feature.icon as any} size={24} color="#4A90D9" />
              </View>
              <View style={styles.featureText}>
                <Text style={styles.featureTitle}>{feature.title}</Text>
                <Text style={styles.featureDesc}>{feature.description}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Plans */}
        <View style={styles.plans}>
          <Text style={styles.plansTitle}>Chọn gói của bạn</Text>
          {PLANS.map((plan) => (
            <TouchableOpacity
              key={plan.id}
              style={[
                styles.planCard,
                selectedPlan === plan.id && styles.planCardSelected,
                plan.popular && styles.planCardPopular,
              ]}
              onPress={() => setSelectedPlan(plan.id)}
            >
              {plan.popular && (
                <View style={styles.popularBadge}>
                  <Text style={styles.popularBadgeText}>Phổ biến</Text>
                </View>
              )}
              <View style={styles.planRadio}>
                <View style={[
                  styles.radioOuter,
                  selectedPlan === plan.id && styles.radioOuterSelected,
                ]}>
                  {selectedPlan === plan.id && (
                    <View style={styles.radioInner} />
                  )}
                </View>
              </View>
              <View style={styles.planInfo}>
                <Text style={styles.planName}>{plan.name}</Text>
                {plan.savings && (
                  <Text style={styles.planSavings}>{plan.savings}</Text>
                )}
              </View>
              <View style={styles.planPrice}>
                <Text style={styles.priceAmount}>{plan.price}</Text>
                <Text style={styles.pricePeriod}>{plan.period}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Guarantee */}
        <View style={styles.guarantee}>
          <Ionicons name="shield-checkmark" size={20} color="#4CAF50" />
          <Text style={styles.guaranteeText}>
            Đảm bảo hoàn tiền 7 ngày nếu không hài lòng
          </Text>
        </View>
      </ScrollView>

      {/* Bottom CTA */}
      <View style={styles.bottomCta}>
        <TouchableOpacity
          style={[styles.purchaseButton, purchasing && styles.purchaseButtonDisabled]}
          onPress={handlePurchase}
          disabled={purchasing}
        >
          {purchasing ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <>
              <Ionicons name="star" size={20} color="#FFF" />
              <Text style={styles.purchaseButtonText}>Nâng cấp Premium</Text>
            </>
          )}
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.restoreButton}
          onPress={handleRestore}
          disabled={purchasing}
        >
          <Text style={styles.restoreButtonText}>Khôi phục mua hàng</Text>
        </TouchableOpacity>
        
        <Text style={styles.termsText}>
          Bằng cách tiếp tục, bạn đồng ý với Điều khoản dịch vụ và Chính sách bảo mật
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    padding: 16,
  },
  closeButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  hero: {
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingBottom: 32,
  },
  heroIcon: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#FFF5E0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  heroSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  features: {
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    borderRadius: 16,
    padding: 16,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  featureIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#E8F4FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  featureText: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  featureDesc: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  plans: {
    padding: 16,
  },
  plansTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  planCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#E0E0E0',
    position: 'relative',
    overflow: 'hidden',
  },
  planCardSelected: {
    borderColor: '#4A90D9',
    backgroundColor: '#F8FBFF',
  },
  planCardPopular: {
    borderColor: '#FFB347',
  },
  popularBadge: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: '#FFB347',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderBottomLeftRadius: 12,
  },
  popularBadgeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFF',
  },
  planRadio: {
    marginRight: 16,
  },
  radioOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#CCC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioOuterSelected: {
    borderColor: '#4A90D9',
  },
  radioInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#4A90D9',
  },
  planInfo: {
    flex: 1,
  },
  planName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  planSavings: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '500',
    marginTop: 2,
  },
  planPrice: {
    alignItems: 'flex-end',
  },
  priceAmount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  pricePeriod: {
    fontSize: 12,
    color: '#666',
  },
  guarantee: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    gap: 8,
  },
  guaranteeText: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '500',
  },
  bottomCta: {
    backgroundColor: '#FFF',
    padding: 16,
    paddingBottom: 32,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  purchaseButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4A90D9',
    borderRadius: 16,
    padding: 18,
    gap: 8,
  },
  purchaseButtonDisabled: {
    backgroundColor: '#A0C4E8',
  },
  purchaseButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFF',
  },
  restoreButton: {
    alignItems: 'center',
    padding: 12,
    marginTop: 8,
  },
  restoreButtonText: {
    fontSize: 14,
    color: '#4A90D9',
    fontWeight: '500',
  },
  termsText: {
    fontSize: 10,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
  },
  // Success state styles
  successContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  successIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#FFF5E0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  successTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  successText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  successButton: {
    marginTop: 32,
    backgroundColor: '#4A90D9',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 16,
  },
  successButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFF',
  },
});
