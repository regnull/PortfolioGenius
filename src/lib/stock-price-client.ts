import { auth } from './firebase';

export interface StockPrice {
  price: number;
  currency: string;
  timestamp: string;
  provider: string;
  ticker: string;
  company_name: string;
  market_cap?: number;
  volume?: number;
}

export interface StockPriceResponse {
  success: boolean;
  data: StockPrice;
  user_id: string;
  timestamp: string;
}

export interface StockPriceError {
  error: string;
  message: string;
}

const STOCK_PRICE_FUNCTION_URL = 'https://get-stock-price-32rtfol3iq-uc.a.run.app';

export class StockPriceClient {
  private static instance: StockPriceClient;
  private cache: Map<string, { data: StockPrice; timestamp: number }> = new Map();
  private readonly cacheTimeout = 5 * 60 * 1000; // 5 minutes

  private constructor() {}

  static getInstance(): StockPriceClient {
    if (!StockPriceClient.instance) {
      StockPriceClient.instance = new StockPriceClient();
    }
    return StockPriceClient.instance;
  }

  private async getAuthToken(): Promise<string> {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('User not authenticated');
    }
    return await user.getIdToken();
  }

  private isCacheValid(timestamp: number): boolean {
    return Date.now() - timestamp < this.cacheTimeout;
  }

  private getCacheKey(ticker: string): string {
    return ticker.toUpperCase();
  }

  async getStockPrice(ticker: string, useCache: boolean = true): Promise<StockPrice> {
    const cacheKey = this.getCacheKey(ticker);
    
    // Check cache first
    if (useCache && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey)!;
      if (this.isCacheValid(cached.timestamp)) {
        return cached.data;
      }
    }

    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(STOCK_PRICE_FUNCTION_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ ticker })
      });

      const data = await response.json();

      if (!response.ok) {
        const error = data as StockPriceError;
        throw new Error(`${error.error}: ${error.message}`);
      }

      const stockPriceResponse = data as StockPriceResponse;
      
      if (!stockPriceResponse.success) {
        throw new Error('Failed to fetch stock price');
      }

      // Cache the result
      this.cache.set(cacheKey, {
        data: stockPriceResponse.data,
        timestamp: Date.now()
      });

      return stockPriceResponse.data;
    } catch (error) {
      console.error(`Error fetching stock price for ${ticker}:`, error);
      throw error;
    }
  }

  async getMultipleStockPrices(tickers: string[], useCache: boolean = true): Promise<Map<string, StockPrice | Error>> {
    const results = new Map<string, StockPrice | Error>();
    
    // Process requests in parallel with some rate limiting
    const batchSize = 5;
    const batches = [];
    
    for (let i = 0; i < tickers.length; i += batchSize) {
      batches.push(tickers.slice(i, i + batchSize));
    }

    for (const batch of batches) {
      const batchPromises = batch.map(async (ticker) => {
        try {
          const price = await this.getStockPrice(ticker, useCache);
          return { ticker, result: price };
        } catch (error) {
          return { ticker, result: error as Error };
        }
      });

      const batchResults = await Promise.all(batchPromises);
      
      for (const { ticker, result } of batchResults) {
        results.set(ticker, result);
      }

      // Small delay between batches to avoid rate limiting
      if (batches.length > 1) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    return results;
  }

  clearCache(): void {
    this.cache.clear();
  }

  clearCacheForTicker(ticker: string): void {
    const cacheKey = this.getCacheKey(ticker);
    this.cache.delete(cacheKey);
  }
}

// Export singleton instance
export const stockPriceClient = StockPriceClient.getInstance();