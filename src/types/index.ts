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
  isPublic: boolean;
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
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  date: Date;
  fees?: number;
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
  createdAt: Date;
  updatedAt: Date;
}