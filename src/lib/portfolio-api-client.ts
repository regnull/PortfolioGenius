import { auth } from './firebase';
import { SuggestedTrade, PortfolioRecommendation } from '@/types';

// Firebase Cloud Function URLs
const CONSTRUCT_PORTFOLIO_URL = 'https://construct-portfolio-32rtfol3iq-uc.a.run.app';
const GET_SUGGESTED_TRADES_URL = 'https://get-suggested-trades-32rtfol3iq-uc.a.run.app';
const CONVERT_SUGGESTED_TRADE_URL = 'https://convert-suggested-trade-32rtfol3iq-uc.a.run.app';
const DISMISS_SUGGESTED_TRADE_URL = 'https://dismiss-suggested-trade-32rtfol3iq-uc.a.run.app';

export interface ConstructPortfolioRequest {
  portfolio_goal: string;
  portfolio_id?: string;
  user_id?: string;
  create_suggested_trades?: boolean;
}

export interface ConstructPortfolioResponse {
  success: boolean;
  recommendations: PortfolioRecommendation[];
  suggested_trades_created?: {
    count: number;
    trade_ids: string[];
    portfolio_id: string;
  };
  message?: string;
}

export interface GetSuggestedTradesResponse {
  success: boolean;
  suggested_trades: SuggestedTrade[];
  count: number;
}

export interface ConvertSuggestedTradeRequest {
  suggested_trade_id: string;
  quantity_override?: number;
  price_override?: number;
  notes?: string;
}

export interface ConvertSuggestedTradeResponse {
  success: boolean;
  trade_id: string;
  position_id?: string;
  message: string;
}

export interface DismissSuggestedTradeRequest {
  suggested_trade_id: string;
  reason?: string;
}

export interface DismissSuggestedTradeResponse {
  success: boolean;
  message: string;
}

export class PortfolioApiClient {
  private static instance: PortfolioApiClient;

  private constructor() {}

  static getInstance(): PortfolioApiClient {
    if (!PortfolioApiClient.instance) {
      PortfolioApiClient.instance = new PortfolioApiClient();
    }
    return PortfolioApiClient.instance;
  }

  private async getAuthToken(): Promise<string> {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('User not authenticated');
    }
    return await user.getIdToken();
  }

  async constructPortfolio(request: ConstructPortfolioRequest): Promise<ConstructPortfolioResponse> {
    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(CONSTRUCT_PORTFOLIO_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(request)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to construct portfolio');
      }

      return data;
    } catch (error) {
      console.error('Error constructing portfolio:', error);
      throw error;
    }
  }

  async getSuggestedTrades(
    portfolioId: string, 
    status?: 'pending' | 'converted' | 'dismissed'
  ): Promise<GetSuggestedTradesResponse> {
    try {
      const token = await this.getAuthToken();
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User not authenticated');
      }
      
      const params = new URLSearchParams({
        portfolio_id: portfolioId,
        user_id: user.uid
      });
      
      if (status) {
        params.append('status', status);
      }

      const response = await fetch(`${GET_SUGGESTED_TRADES_URL}?${params}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to get suggested trades');
      }

      return data;
    } catch (error) {
      console.error('Error getting suggested trades:', error);
      throw error;
    }
  }

  async convertSuggestedTrade(request: ConvertSuggestedTradeRequest): Promise<ConvertSuggestedTradeResponse> {
    try {
      const token = await this.getAuthToken();
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User not authenticated');
      }
      
      const response = await fetch(CONVERT_SUGGESTED_TRADE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...request,
          user_id: user.uid
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to convert suggested trade');
      }

      return data;
    } catch (error) {
      console.error('Error converting suggested trade:', error);
      throw error;
    }
  }

  async dismissSuggestedTrade(request: DismissSuggestedTradeRequest): Promise<DismissSuggestedTradeResponse> {
    try {
      const token = await this.getAuthToken();
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User not authenticated');
      }
      
      const response = await fetch(DISMISS_SUGGESTED_TRADE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...request,
          user_id: user.uid
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to dismiss suggested trade');
      }

      return data;
    } catch (error) {
      console.error('Error dismissing suggested trade:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const portfolioApiClient = PortfolioApiClient.getInstance(); 