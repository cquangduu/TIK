// app/(tabs)/news.tsx
// News reader screen with Korean news

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { lessonApi, NewsItem } from '../../src/services/api';
import { useUserStore } from '../../src/store/userStore';
import AdBanner from '../../src/components/AdBanner';

export default function NewsScreen() {
  const { isPremium, showVietnamese } = useUserStore();
  
  const [news, setNews] = useState<NewsItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);

  useEffect(() => {
    fetchNews();
    return () => {
      // Cleanup audio
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, []);

  const fetchNews = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await lessonApi.getNews();
      setNews(data);
    } catch (err) {
      setError('Không thể tải tin tức');
      console.error('Error fetching news:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleAudio = async () => {
    if (!news?.audio_url) return;

    try {
      if (sound) {
        if (isPlaying) {
          await sound.pauseAsync();
          setIsPlaying(false);
        } else {
          await sound.playAsync();
          setIsPlaying(true);
        }
      } else {
        const { sound: newSound } = await Audio.Sound.createAsync(
          { uri: news.audio_url },
          { shouldPlay: true },
          onPlaybackStatusUpdate
        );
        setSound(newSound);
        setIsPlaying(true);
      }
    } catch (err) {
      console.error('Error playing audio:', err);
    }
  };

  const onPlaybackStatusUpdate = (status: any) => {
    if (status.didJustFinish) {
      setIsPlaying(false);
    }
  };

  const formatKoreanText = (text: string) => {
    // Split into sentences for better readability
    return text.split('.').filter(s => s.trim()).map((sentence, index) => (
      <Text key={index} style={styles.sentence}>
        {sentence.trim()}.{'\n\n'}
      </Text>
    ));
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4A90D9" />
        <Text style={styles.loadingText}>Đang tải tin tức...</Text>
      </View>
    );
  }

  if (error || !news) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="newspaper-outline" size={64} color="#999" />
        <Text style={styles.errorText}>{error || 'Không có tin tức'}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchNews}>
          <Text style={styles.retryButtonText}>Thử lại</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Tin Tức Hàn Quốc</Text>
          <Text style={styles.date}>{news.date}</Text>
        </View>

        {/* Audio Player */}
        {news.audio_url && (
          <View style={styles.audioCard}>
            <TouchableOpacity 
              style={styles.playButton}
              onPress={toggleAudio}
            >
              <Ionicons 
                name={isPlaying ? 'pause' : 'play'} 
                size={32} 
                color="#FFF" 
              />
            </TouchableOpacity>
            <View style={styles.audioInfo}>
              <Text style={styles.audioTitle}>Nghe đọc tin</Text>
              <Text style={styles.audioDesc}>Luyện nghe tiếng Hàn</Text>
            </View>
            <TouchableOpacity style={styles.speedButton}>
              <Text style={styles.speedText}>1x</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Korean News Content */}
        <View style={styles.contentCard}>
          <View style={styles.contentHeader}>
            <View style={styles.langTag}>
              <Text style={styles.langTagText}>🇰🇷 한국어</Text>
            </View>
          </View>
          <View style={styles.koreanContent}>
            {formatKoreanText(news.content_ko)}
          </View>
        </View>

        {/* Translation Toggle */}
        <TouchableOpacity 
          style={styles.translationToggle}
          onPress={() => setShowTranslation(!showTranslation)}
        >
          <Ionicons 
            name={showTranslation ? 'eye-off' : 'eye'} 
            size={20} 
            color="#4A90D9" 
          />
          <Text style={styles.translationToggleText}>
            {showTranslation ? 'Ẩn bản dịch' : 'Xem bản dịch'}
          </Text>
        </TouchableOpacity>

        {/* Vietnamese Translation (if available) */}
        {showTranslation && news.content_vi && (
          <View style={styles.translationCard}>
            <View style={styles.contentHeader}>
              <View style={[styles.langTag, styles.viLangTag]}>
                <Text style={styles.langTagText}>🇻🇳 Tiếng Việt</Text>
              </View>
            </View>
            <Text style={styles.translationText}>{news.content_vi}</Text>
          </View>
        )}

        {/* Tips */}
        <View style={styles.tipsCard}>
          <Ionicons name="bulb" size={20} color="#FF9800" />
          <Text style={styles.tipsText}>
            Mẹo: Đọc to theo để luyện phát âm! Bạn có thể nghe đi nghe lại nhiều lần.
          </Text>
        </View>

        <View style={styles.bottomPadding} />
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
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  date: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  audioCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4A90D9',
    marginHorizontal: 16,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  playButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  audioInfo: {
    flex: 1,
    marginLeft: 16,
  },
  audioTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFF',
  },
  audioDesc: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 2,
  },
  speedButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  speedText: {
    color: '#FFF',
    fontWeight: '600',
  },
  contentCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  contentHeader: {
    marginBottom: 16,
  },
  langTag: {
    alignSelf: 'flex-start',
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  viLangTag: {
    backgroundColor: '#FFEBEE',
  },
  langTagText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  koreanContent: {
    lineHeight: 32,
  },
  sentence: {
    fontSize: 18,
    color: '#333',
    lineHeight: 32,
  },
  translationToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 16,
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#FFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  translationToggleText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#4A90D9',
    fontWeight: '500',
  },
  translationCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#FFCDD2',
  },
  translationText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 26,
  },
  tipsCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FFF3E0',
    marginHorizontal: 16,
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
  bottomPadding: {
    height: 24,
  },
});
