// app/_layout.tsx
// Root layout for the app

import { Stack } from 'expo-router';
import { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import * as Notifications from 'expo-notifications';
import { useUserStore } from '../src/store/userStore';

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export default function RootLayout() {
  const { initUser, notifications } = useUserStore();

  useEffect(() => {
    // Initialize user on app start
    initUser();

    // Register for push notifications
    if (notifications) {
      registerForPushNotifications();
      scheduleDailyReminder();
    }
  }, []);

  return (
    <>
      <StatusBar style="auto" />
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen 
          name="premium" 
          options={{ 
            presentation: 'modal',
            headerShown: false,
          }} 
        />
        <Stack.Screen 
          name="lesson/[date]" 
          options={{ 
            headerShown: true,
            title: 'Bài học',
          }} 
        />
      </Stack>
    </>
  );
}

async function registerForPushNotifications() {
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('Failed to get push notification permissions');
    return;
  }
}

async function scheduleDailyReminder() {
  // Cancel existing notifications
  await Notifications.cancelAllScheduledNotificationsAsync();

  // Schedule daily reminder at 8:00 AM
  await Notifications.scheduleNotificationAsync({
    content: {
      title: '📚 TOPIK Daily',
      body: 'Thời gian học tiếng Hàn! Hãy hoàn thành bài học hôm nay.',
      sound: true,
    },
    trigger: {
      type: 'daily',
      hour: 8,
      minute: 0,
    } as any,
  });
}
