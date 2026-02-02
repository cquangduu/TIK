// components/StreakBadge.tsx
// Streak display badge with flame animation

import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, Animated, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface StreakBadgeProps {
  streak: number;
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
  animated?: boolean;
  onPress?: () => void;
}

const SIZES = {
  small: { icon: 16, text: 12, padding: 6 },
  medium: { icon: 20, text: 14, padding: 8 },
  large: { icon: 32, text: 20, padding: 12 },
};

export default function StreakBadge({
  streak,
  size = 'medium',
  showLabel = false,
  animated = true,
  onPress,
}: StreakBadgeProps) {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;

  const sizeConfig = SIZES[size];

  useEffect(() => {
    if (!animated || streak === 0) return;

    // Pulse animation for active streak
    const pulseAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 1.1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
      ])
    );

    // Glow animation
    const glowAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(glowAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(glowAnim, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );

    if (streak >= 7) {
      pulseAnimation.start();
      glowAnimation.start();
    }

    return () => {
      pulseAnimation.stop();
      glowAnimation.stop();
    };
  }, [streak, animated, scaleAnim, glowAnim]);

  const getStreakColor = () => {
    if (streak >= 30) return '#FFD700'; // Gold
    if (streak >= 14) return '#FF6B35'; // Orange
    if (streak >= 7) return '#FF8C42';  // Light orange
    if (streak >= 1) return '#FFB347';  // Yellow orange
    return '#999'; // Gray for no streak
  };

  const glowOpacity = glowAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 0.6],
  });

  const badge = (
    <Animated.View 
      style={[
        styles.container,
        {
          transform: [{ scale: scaleAnim }],
          padding: sizeConfig.padding,
          backgroundColor: streak >= 7 ? `${getStreakColor()}20` : '#FFF5EB',
        },
      ]}
    >
      {streak >= 7 && (
        <Animated.View 
          style={[
            styles.glow,
            { 
              opacity: glowOpacity,
              backgroundColor: getStreakColor(),
            },
          ]} 
        />
      )}
      <Ionicons 
        name="flame" 
        size={sizeConfig.icon} 
        color={getStreakColor()} 
      />
      <Text 
        style={[
          styles.streakText,
          { 
            fontSize: sizeConfig.text,
            color: getStreakColor(),
          },
        ]}
      >
        {streak}
      </Text>
      {showLabel && (
        <Text style={styles.label}>ngày</Text>
      )}
    </Animated.View>
  );

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
        {badge}
      </TouchableOpacity>
    );
  }

  return badge;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 20,
    position: 'relative',
    overflow: 'hidden',
  },
  glow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: 20,
  },
  streakText: {
    fontWeight: 'bold',
    marginLeft: 4,
  },
  label: {
    fontSize: 10,
    color: '#666',
    marginLeft: 2,
  },
});
