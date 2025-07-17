export interface User {
  id: string;
  email: string;
  displayName: string;
  photoURL?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Portfolio {
  id: string;
  userId: string;
  name: string;
  description?: string;
  goal?: string;
  isPublic: boolean;
  isBotPortfolio?: boolean;
  cashBalance: number;
  createdAt: Date;
  updatedAt: Date;
  totalValue: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
}

export interface Trade {
  id: string;
  portfolioId: string;
  symbol: string;
  type: 'BuyToOpen' | 'SellToClose';
  quantity: number;
  price: number;
  date: Date;
  fees?: number;
  positionId?: string;
  notes?: string;
}

export interface Position {
  id: string;
  portfolioId: string;
  symbol: string;
  name: string;
  type: 'stock' | 'etf' | 'crypto' | 'bond' | 'other';
  quantity: number;
  openPrice: number;
  currentPrice: number;
  openDate: Date;
  closeDate?: Date;
  closePrice?: number;
  status: 'open' | 'closed';
  totalValue: number;
  gainLoss: number;
  gainLossPercent: number;
  fees?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface SuggestedTrade {
  id: string;
  portfolioId: string;
  userId: string;
  symbol: string;
  name: string;
  type: 'stock' | 'etf' | 'crypto' | 'bond' | 'other';
  action: 'buy' | 'sell';
  quantity: number;
  estimatedPrice: number;
  priority: 'low' | 'medium' | 'high';
  rationale: string;
  notes?: string;
  status: 'pending' | 'converted' | 'dismissed';
  createdAt: Date;
  updatedAt: Date;
  convertedToTradeId?: string;
  dismissedReason?: string;
  dismissedAt?: Date;
}

export interface PortfolioRecommendation {
  ticker_symbol: string;
  allocation_percent: number;
  rationale: string;
  notes?: string;
}