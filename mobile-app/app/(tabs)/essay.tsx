// app/(tabs)/essay.tsx
// Model Essay screen for TOPIK writing practice

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useUserStore } from '../../src/store/userStore';
import { lessonApi, EssayData } from '../../src/services/api';
import AdBanner from '../../src/components/AdBanner';

const PARAGRAPH_TYPES: Record<string, { icon: string; color: string; label: string }> = {
  intro: { icon: 'flag', color: '#4A90D9', label: 'Mở bài' },
  body: { icon: 'document-text', color: '#9C27B0', label: 'Thân bài' },
  conclusion: { icon: 'checkmark-done', color: '#4CAF50', label: 'Kết bài' },
};

export default function EssayScreen() {
  const [essay, setEssay] = useState<EssayData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAnalysis, setShowAnalysis] = useState<Record<number, boolean>>({});
  const [showVietnamese, setShowVietnamese] = useState(true);

  const { isPremium, showVietnamese: defaultShowViet } = useUserStore();

  useEffect(() => {
    setShowVietnamese(defaultShowViet);
    fetchEssay();
  }, []);

  const fetchEssay = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await lessonApi.getEssay();
      setEssay(data);
    } catch (err) {
      setError('Không thể tải bài văn mẫu. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAnalysis = (index: number) => {
    setShowAnalysis((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#9C27B0" />
        <Text style={styles.loadingText}>Đang tải bài văn mẫu...</Text>
      </View>
    );
  }

  if (error || !essay) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="document-text" size={64} color="#999" />
        <Text style={styles.errorText}>{error || 'Không có bài văn hôm nay'}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchEssay}>
          <Text style={styles.retryButtonText}>Thử lại</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerIcon}>
            <Ionicons name="create" size={32} color="#9C27B0" />
          </View>
          <Text style={styles.title}>Bài Văn Mẫu TOPIK</Text>
          <Text style={styles.subtitle}>Học cách viết văn chuẩn format thi</Text>
        </View>

        {/* Topic Card */}
        <View style={styles.topicCard}>
          <Text style={styles.topicLabel}>📝 Đề bài hôm nay</Text>
          <Text style={styles.topicText}>{essay.topic}</Text>
          {essay.question && (
            <Text style={styles.questionText}>{essay.question}</Text>
          )}
        </View>

        {/* Toggle */}
        <View style={styles.toggleContainer}>
          <TouchableOpacity
            style={[styles.toggleButton, !showVietnamese && styles.toggleButtonActive]}
            onPress={() => setShowVietnamese(false)}
          >
            <Text style={[styles.toggleText, !showVietnamese && styles.toggleTextActive]}>
              🇰🇷 Tiếng Hàn
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.toggleButton, showVietnamese && styles.toggleButtonActive]}
            onPress={() => setShowVietnamese(true)}
          >
            <Text style={[styles.toggleText, showVietnamese && styles.toggleTextActive]}>
              🇻🇳 Song ngữ
            </Text>
          </TouchableOpacity>
        </View>

        {/* Full Essay (Korean only) */}
        <View style={styles.essayCard}>
          <Text style={styles.essayLabel}>📖 Bài văn mẫu</Text>
          <Text style={styles.essayText}>{essay.essay_ko}</Text>
        </View>

        {/* Paragraph Analysis */}
        <View style={styles.analysisSection}>
          <Text style={styles.sectionTitle}>📚 Phân tích từng đoạn</Text>
          
          {essay.paragraphs.map((paragraph, index) => {
            const typeConfig = PARAGRAPH_TYPES[paragraph.type] || PARAGRAPH_TYPES.body;
            const isExpanded = showAnalysis[index];
            
            return (
              <View key={index} style={styles.paragraphCard}>
                <TouchableOpacity 
                  style={styles.paragraphHeader}
                  onPress={() => toggleAnalysis(index)}
                  activeOpacity={0.7}
                >
                  <View style={styles.paragraphType}>
                    <View style={[styles.typeIcon, { backgroundColor: `${typeConfig.color}20` }]}>
                      <Ionicons name={typeConfig.icon as any} size={18} color={typeConfig.color} />
                    </View>
                    <Text style={[styles.typeLabel, { color: typeConfig.color }]}>
                      {typeConfig.label}
                    </Text>
                  </View>
                  <Ionicons 
                    name={isExpanded ? 'chevron-up' : 'chevron-down'} 
                    size={20} 
                    color="#666" 
                  />
                </TouchableOpacity>

                <View style={styles.paragraphContent}>
                  <Text style={styles.koreanText}>{paragraph.korean}</Text>
                </View>

                {isExpanded && (
                  <View style={styles.analysisContent}>
                    <View style={styles.analysisHeader}>
                      <Ionicons name="bulb" size={16} color="#FF9800" />
                      <Text style={styles.analysisLabel}>Phân tích & Giải thích</Text>
                    </View>
                    <Text style={styles.analysisText}>{paragraph.analysis}</Text>
                  </View>
                )}
              </View>
            );
          })}
        </View>

        {/* Writing Tips */}
        <View style={styles.tipsCard}>
          <Text style={styles.tipsTitle}>💡 Mẹo viết văn TOPIK</Text>
          <View style={styles.tipItem}>
            <Ionicons name="checkmark-circle" size={16} color="#4CAF50" />
            <Text style={styles.tipText}>Luôn có 3 phần: Mở bài - Thân bài - Kết bài</Text>
          </View>
          <View style={styles.tipItem}>
            <Ionicons name="checkmark-circle" size={16} color="#4CAF50" />
            <Text style={styles.tipText}>Sử dụng các cấu trúc nối câu phổ biến</Text>
          </View>
          <View style={styles.tipItem}>
            <Ionicons name="checkmark-circle" size={16} color="#4CAF50" />
            <Text style={styles.tipText}>Đưa ra ý kiến rõ ràng và có dẫn chứng</Text>
          </View>
          <View style={styles.tipItem}>
            <Ionicons name="checkmark-circle" size={16} color="#4CAF50" />
            <Text style={styles.tipText}>Kiểm tra lỗi chính tả trước khi nộp</Text>
          </View>
        </View>

        {/* Bottom Spacing */}
        <View style={{ height: 100 }} />
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F7FA',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F7FA',
    padding: 24,
  },
  errorText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 24,
    backgroundColor: '#9C27B0',
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 12,
  },
  retryButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 24,
    backgroundColor: '#FFF',
  },
  headerIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#F3E5F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  topicCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 16,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#9C27B0',
  },
  topicLabel: {
    fontSize: 12,
    color: '#9C27B0',
    fontWeight: '600',
    marginBottom: 8,
  },
  topicText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    lineHeight: 26,
  },
  questionText: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    fontStyle: 'italic',
  },
  toggleContainer: {
    flexDirection: 'row',
    marginHorizontal: 16,
    marginTop: 16,
    backgroundColor: '#E0E0E0',
    borderRadius: 12,
    padding: 4,
  },
  toggleButton: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
  },
  toggleButtonActive: {
    backgroundColor: '#FFF',
  },
  toggleText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  toggleTextActive: {
    color: '#333',
  },
  essayCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 16,
    padding: 20,
  },
  essayLabel: {
    fontSize: 12,
    color: '#9C27B0',
    fontWeight: '600',
    marginBottom: 12,
  },
  essayText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 28,
  },
  analysisSection: {
    marginTop: 24,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  paragraphCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    marginBottom: 12,
    overflow: 'hidden',
  },
  paragraphHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  paragraphType: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typeIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  typeLabel: {
    fontSize: 14,
    fontWeight: '600',
  },
  paragraphContent: {
    padding: 16,
    paddingTop: 12,
  },
  koreanText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 26,
  },
  analysisContent: {
    backgroundColor: '#FFFBF0',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#FFE0B2',
  },
  analysisHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  analysisLabel: {
    fontSize: 12,
    color: '#FF9800',
    fontWeight: '600',
    marginLeft: 6,
  },
  analysisText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  tipsCard: {
    backgroundColor: '#E8F5E9',
    marginHorizontal: 16,
    marginTop: 24,
    borderRadius: 16,
    padding: 20,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 12,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#333',
    marginLeft: 8,
    flex: 1,
  },
});
