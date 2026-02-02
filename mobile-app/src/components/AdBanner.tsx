// components/AdBanner.tsx
// AdMob banner with premium check

import React from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { 
  BannerAd, 
  BannerAdSize, 
  TestIds 
} from 'react-native-google-mobile-ads';

// Use test IDs in development, real IDs in production
const BANNER_AD_UNIT_ID = __DEV__ 
  ? TestIds.BANNER 
  : Platform.select({
      ios: 'ca-app-pub-XXXXX/YYYYY',      // Replace with your iOS ad unit
      android: 'ca-app-pub-XXXXX/ZZZZZ',   // Replace with your Android ad unit
    }) || TestIds.BANNER;

interface AdBannerProps {
  isPremium?: boolean;
  size?: BannerAdSize;
  containerStyle?: object;
}

export default function AdBanner({ 
  isPremium = false, 
  size = BannerAdSize.ANCHORED_ADAPTIVE_BANNER,
  containerStyle,
}: AdBannerProps) {
  // Don't show ads for premium users
  if (isPremium) {
    return null;
  }

  return (
    <View style={[styles.container, containerStyle]}>
      <BannerAd
        unitId={BANNER_AD_UNIT_ID}
        size={size}
        requestOptions={{
          requestNonPersonalizedAdsOnly: true,
        }}
        onAdLoaded={() => {
          console.log('Ad loaded successfully');
        }}
        onAdFailedToLoad={(error) => {
          console.error('Ad failed to load:', error);
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FAFAFA',
    paddingVertical: 4,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
});
