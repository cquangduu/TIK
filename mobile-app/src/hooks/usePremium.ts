// hooks/usePremium.ts
// Premium subscription management hook

import { useEffect, useState, useCallback } from 'react';
import * as IAP from 'expo-in-app-purchases';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

const PREMIUM_STORAGE_KEY = '@topik_premium_status';
const PREMIUM_EXPIRY_KEY = '@topik_premium_expiry';

// Product IDs - configure these in App Store Connect / Google Play Console
const PRODUCT_IDS = {
  monthly: 'topik_premium_monthly',      // $2.99/month
  yearly: 'topik_premium_yearly',        // $19.99/year
  lifetime: 'topik_premium_lifetime',    // $49.99 one-time
};

export interface PremiumProduct {
  productId: string;
  title: string;
  description: string;
  price: string;
  priceAmountMicros: string;
  priceCurrencyCode: string;
}

export interface UsePremiumReturn {
  isPremium: boolean;
  loading: boolean;
  products: PremiumProduct[];
  purchasePremium: (productId: string) => Promise<boolean>;
  restorePurchases: () => Promise<boolean>;
  checkPremiumStatus: () => Promise<boolean>;
}

export function usePremium(): UsePremiumReturn {
  const [isPremium, setIsPremium] = useState(false);
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState<PremiumProduct[]>([]);

  // Check if user has premium status
  const checkPremiumStatus = useCallback(async (): Promise<boolean> => {
    try {
      const status = await AsyncStorage.getItem(PREMIUM_STORAGE_KEY);
      const expiry = await AsyncStorage.getItem(PREMIUM_EXPIRY_KEY);
      
      if (status === 'lifetime') {
        setIsPremium(true);
        return true;
      }
      
      if (status === 'active' && expiry) {
        const expiryDate = new Date(expiry);
        if (expiryDate > new Date()) {
          setIsPremium(true);
          return true;
        } else {
          // Subscription expired
          await AsyncStorage.removeItem(PREMIUM_STORAGE_KEY);
          await AsyncStorage.removeItem(PREMIUM_EXPIRY_KEY);
          setIsPremium(false);
          return false;
        }
      }
      
      setIsPremium(false);
      return false;
    } catch (error) {
      console.error('Error checking premium status:', error);
      return false;
    }
  }, []);

  // Initialize IAP and load products
  const initializeIAP = useCallback(async () => {
    try {
      setLoading(true);
      
      // Connect to IAP
      await IAP.connectAsync();
      
      // Get available products
      const productIds = Object.values(PRODUCT_IDS);
      const { results } = await IAP.getProductsAsync(productIds);
      
      if (results) {
        setProducts(results.map(product => ({
          productId: product.productId,
          title: product.title,
          description: product.description,
          price: product.price,
          priceAmountMicros: product.priceAmountMicros,
          priceCurrencyCode: product.priceCurrencyCode,
        })));
      }

      // Set up purchase listener
      IAP.setPurchaseListener(({ responseCode, results, errorCode }) => {
        if (responseCode === IAP.IAPResponseCode.OK && results) {
          for (const purchase of results) {
            handlePurchase(purchase);
          }
        }
      });

      // Check current status
      await checkPremiumStatus();
      
    } catch (error) {
      console.error('IAP initialization error:', error);
    } finally {
      setLoading(false);
    }
  }, [checkPremiumStatus]);

  // Handle successful purchase
  const handlePurchase = async (purchase: IAP.InAppPurchase) => {
    try {
      const { productId } = purchase;
      
      // Determine subscription type
      if (productId === PRODUCT_IDS.lifetime) {
        await AsyncStorage.setItem(PREMIUM_STORAGE_KEY, 'lifetime');
      } else if (productId === PRODUCT_IDS.yearly) {
        const expiry = new Date();
        expiry.setFullYear(expiry.getFullYear() + 1);
        await AsyncStorage.setItem(PREMIUM_STORAGE_KEY, 'active');
        await AsyncStorage.setItem(PREMIUM_EXPIRY_KEY, expiry.toISOString());
      } else if (productId === PRODUCT_IDS.monthly) {
        const expiry = new Date();
        expiry.setMonth(expiry.getMonth() + 1);
        await AsyncStorage.setItem(PREMIUM_STORAGE_KEY, 'active');
        await AsyncStorage.setItem(PREMIUM_EXPIRY_KEY, expiry.toISOString());
      }
      
      setIsPremium(true);
      
      // Finish the transaction
      await IAP.finishTransactionAsync(purchase, true);
      
    } catch (error) {
      console.error('Error handling purchase:', error);
    }
  };

  // Purchase premium subscription
  const purchasePremium = async (productId: string): Promise<boolean> => {
    try {
      setLoading(true);
      await IAP.purchaseItemAsync(productId);
      return true;
    } catch (error) {
      console.error('Purchase error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Restore previous purchases
  const restorePurchases = async (): Promise<boolean> => {
    try {
      setLoading(true);
      
      const history = await IAP.getPurchaseHistoryAsync();
      
      if (history.results && history.results.length > 0) {
        // Find the most recent valid purchase
        const validPurchase = history.results.find(
          (purchase) => Object.values(PRODUCT_IDS).includes(purchase.productId)
        );
        
        if (validPurchase) {
          await handlePurchase(validPurchase);
          return true;
        }
      }
      
      return false;
    } catch (error) {
      console.error('Restore purchases error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Initialize on mount
  useEffect(() => {
    initializeIAP();
    
    return () => {
      // Cleanup
      IAP.disconnectAsync();
    };
  }, [initializeIAP]);

  return {
    isPremium,
    loading,
    products,
    purchasePremium,
    restorePurchases,
    checkPremiumStatus,
  };
}

// Helper function to format price
export function formatPrice(product: PremiumProduct): string {
  return product.price;
}

// Helper to get product by type
export function getProductByType(
  products: PremiumProduct[], 
  type: 'monthly' | 'yearly' | 'lifetime'
): PremiumProduct | undefined {
  const productId = PRODUCT_IDS[type];
  return products.find(p => p.productId === productId);
}
