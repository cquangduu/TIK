// components/ErrorView.tsx
// Error display component with retry button

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

type ErrorType = 'network' | 'server' | 'auth' | 'notfound' | 'generic';

interface ErrorViewProps {
  type?: ErrorType;
  message?: string;
  onRetry?: () => void;
  onGoBack?: () => void;
  fullScreen?: boolean;
}

const ERROR_CONFIG: Record<ErrorType, { icon: string; title: string; defaultMessage: string }> = {
  network: {
    icon: 'cloud-offline',
    title: 'Không có kết nối',
    defaultMessage: 'Vui lòng kiểm tra kết nối internet và thử lại.',
  },
  server: {
    icon: 'server',
    title: 'Lỗi máy chủ',
    defaultMessage: 'Đã xảy ra lỗi từ máy chủ. Vui lòng thử lại sau.',
  },
  auth: {
    icon: 'lock-closed',
    title: 'Không có quyền truy cập',
    defaultMessage: 'Bạn cần đăng nhập để xem nội dung này.',
  },
  notfound: {
    icon: 'search',
    title: 'Không tìm thấy',
    defaultMessage: 'Nội dung bạn tìm kiếm không tồn tại.',
  },
  generic: {
    icon: 'alert-circle',
    title: 'Đã xảy ra lỗi',
    defaultMessage: 'Đã xảy ra lỗi không xác định. Vui lòng thử lại.',
  },
};

export default function ErrorView({
  type = 'generic',
  message,
  onRetry,
  onGoBack,
  fullScreen = true,
}: ErrorViewProps) {
  const config = ERROR_CONFIG[type];

  const content = (
    <View style={styles.content}>
      <Ionicons 
        name={config.icon as any} 
        size={80} 
        color="#999" 
      />
      <Text style={styles.title}>{config.title}</Text>
      <Text style={styles.message}>
        {message || config.defaultMessage}
      </Text>
      
      <View style={styles.buttons}>
        {onRetry && (
          <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
            <Ionicons name="refresh" size={20} color="#FFF" />
            <Text style={styles.retryButtonText}>Thử lại</Text>
          </TouchableOpacity>
        )}
        
        {onGoBack && (
          <TouchableOpacity style={styles.backButton} onPress={onGoBack}>
            <Ionicons name="arrow-back" size={20} color="#666" />
            <Text style={styles.backButtonText}>Quay lại</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  if (fullScreen) {
    return <View style={styles.fullScreen}>{content}</View>;
  }

  return content;
}

const styles = StyleSheet.create({
  fullScreen: {
    flex: 1,
    backgroundColor: '#F5F7FA',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  content: {
    alignItems: 'center',
    padding: 24,
  },
  title: {
    fontSize: 22,
    fontWeight: '600',
    color: '#333',
    marginTop: 24,
    textAlign: 'center',
  },
  message: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
    lineHeight: 20,
    maxWidth: 280,
  },
  buttons: {
    flexDirection: 'row',
    marginTop: 32,
    gap: 12,
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4A90D9',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    gap: 8,
  },
  retryButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E0E0E0',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    gap: 8,
  },
  backButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
});
