// hooks/useNetwork.ts
// Network connectivity and error handling hook

import { useState, useEffect, useCallback } from 'react';
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';

interface UseNetworkReturn {
  isConnected: boolean;
  isInternetReachable: boolean | null;
  connectionType: string | null;
  checkConnection: () => Promise<boolean>;
}

export function useNetwork(): UseNetworkReturn {
  const [isConnected, setIsConnected] = useState(true);
  const [isInternetReachable, setIsInternetReachable] = useState<boolean | null>(null);
  const [connectionType, setConnectionType] = useState<string | null>(null);

  useEffect(() => {
    // Subscribe to network state updates
    const unsubscribe = NetInfo.addEventListener((state: NetInfoState) => {
      setIsConnected(state.isConnected ?? true);
      setIsInternetReachable(state.isInternetReachable);
      setConnectionType(state.type);
    });

    // Check initial state
    NetInfo.fetch().then((state) => {
      setIsConnected(state.isConnected ?? true);
      setIsInternetReachable(state.isInternetReachable);
      setConnectionType(state.type);
    });

    return () => unsubscribe();
  }, []);

  const checkConnection = useCallback(async (): Promise<boolean> => {
    const state = await NetInfo.fetch();
    return state.isConnected ?? false;
  }, []);

  return {
    isConnected,
    isInternetReachable,
    connectionType,
    checkConnection,
  };
}

// Simplified version without NetInfo dependency
export function useSimpleNetwork(): { isOnline: boolean } {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    // For React Native, we'll assume online by default
    // This can be enhanced with actual NetInfo when the package is installed
    setIsOnline(true);
  }, []);

  return { isOnline };
}
