import { useState, useEffect, useCallback } from 'react';
import { stockPriceClient } from '@/lib/stock-price-client';
import { Position } from '@/types';

export interface PositionWithCurrentPrice extends Position {
  currentPrice: number;
  currentGainLoss: number;
  currentGainLossPercent: number;
  currentTotalValue: number;
  priceUpdateTime?: string;
}

export interface UseStockPricesResult {
  positions: PositionWithCurrentPrice[];
  loading: boolean;
  error: string | null;
  lastUpdate: Date | null;
  refreshPrices: () => void;
}

export const useStockPrices = (initialPositions: Position[]): UseStockPricesResult => {
  const [positions, setPositions] = useState<PositionWithCurrentPrice[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const calculatePositionMetrics = useCallback((position: Position, currentPrice: number): PositionWithCurrentPrice => {
    const currentTotalValue = currentPrice * position.quantity;
    const currentGainLoss = currentTotalValue - (position.openPrice * position.quantity);
    const currentGainLossPercent = ((currentPrice - position.openPrice) / position.openPrice) * 100;

    return {
      ...position,
      currentPrice,
      currentGainLoss,
      currentGainLossPercent,
      currentTotalValue,
      priceUpdateTime: new Date().toISOString()
    };
  }, []);

  const fetchPrices = useCallback(async (useCache: boolean = true) => {
    if (initialPositions.length === 0) {
      setPositions([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Get unique tickers for open positions only
      const openPositions = initialPositions.filter(p => p.status === 'open');
      const uniqueTickers = [...new Set(openPositions.map(p => p.symbol))];

      if (uniqueTickers.length === 0) {
        // No open positions, just return positions with existing prices
        setPositions(initialPositions.map(p => ({
          ...p,
          currentPrice: p.closePrice || p.openPrice,
          currentGainLoss: p.gainLoss,
          currentGainLossPercent: p.gainLossPercent,
          currentTotalValue: p.totalValue
        })));
        setLastUpdate(new Date());
        return;
      }

      // Fetch prices for all unique tickers
      const priceResults = await stockPriceClient.getMultipleStockPrices(uniqueTickers, useCache);

      // Create a map of ticker to current price
      const priceMap = new Map<string, number>();
      const errors: string[] = [];

      priceResults.forEach((result, ticker) => {
        if (result instanceof Error) {
          errors.push(`${ticker}: ${result.message}`);
        } else {
          priceMap.set(ticker, result.price);
        }
      });

      // Update positions with current prices
      const updatedPositions = initialPositions.map(position => {
        if (position.status === 'closed') {
          // For closed positions, use the close price
          return {
            ...position,
            currentPrice: position.closePrice || position.openPrice,
            currentGainLoss: position.gainLoss,
            currentGainLossPercent: position.gainLossPercent,
            currentTotalValue: position.totalValue
          };
        } else {
          // For open positions, use the fetched current price
          const currentPrice = priceMap.get(position.symbol);
          if (currentPrice !== undefined) {
            return calculatePositionMetrics(position, currentPrice);
          } else {
            // Fallback to stored price if fetch failed
            return {
              ...position,
              currentPrice: position.currentPrice || position.openPrice,
              currentGainLoss: position.gainLoss,
              currentGainLossPercent: position.gainLossPercent,
              currentTotalValue: position.totalValue
            };
          }
        }
      });

      setPositions(updatedPositions);
      setLastUpdate(new Date());

      if (errors.length > 0) {
        setError(`Failed to fetch prices for: ${errors.join(', ')}`);
      }
    } catch (err) {
      setError(`Failed to fetch stock prices: ${err instanceof Error ? err.message : 'Unknown error'}`);
      // Fallback to original positions
      setPositions(initialPositions.map(p => ({
        ...p,
        currentPrice: p.currentPrice || p.openPrice,
        currentGainLoss: p.gainLoss,
        currentGainLossPercent: p.gainLossPercent,
        currentTotalValue: p.totalValue
      })));
    } finally {
      setLoading(false);
    }
  }, [initialPositions, calculatePositionMetrics]);

  const refreshPrices = useCallback(() => {
    fetchPrices(false); // Force refresh without cache
  }, [fetchPrices]);

  // Fetch prices when positions change
  useEffect(() => {
    fetchPrices(true);
  }, [fetchPrices]);

  // Auto-refresh every 5 minutes for open positions
  useEffect(() => {
    const hasOpenPositions = initialPositions.some(p => p.status === 'open');
    if (!hasOpenPositions) return;

    const interval = setInterval(() => {
      fetchPrices(true);
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [initialPositions, fetchPrices]);

  return {
    positions,
    loading,
    error,
    lastUpdate,
    refreshPrices
  };
};