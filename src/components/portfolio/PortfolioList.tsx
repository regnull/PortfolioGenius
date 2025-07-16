'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getPortfolios, deletePortfolio, getPositions } from '@/lib/firestore';
import { Portfolio, Position } from '@/types';
import { formatCurrency, formatPercentage } from '@/lib/currency';
import { useStockPrices } from '@/hooks/useStockPrices';
import Link from 'next/link';

interface PortfolioListProps {
  onPortfolioCreated?: boolean;
}

interface PortfolioWithPositions extends Portfolio {
  positions: Position[];
}


export default function PortfolioList({ onPortfolioCreated }: PortfolioListProps) {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [portfoliosWithPositions, setPortfoliosWithPositions] = useState<PortfolioWithPositions[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const fetchPortfolios = async () => {
    if (!user) return;

    try {
      const userPortfolios = await getPortfolios(user.uid);
      setPortfolios(userPortfolios);
      
      // Fetch positions for each portfolio
      const portfoliosWithPos = await Promise.all(
        userPortfolios.map(async (portfolio) => {
          try {
            const positions = await getPositions(portfolio.id);
            return { ...portfolio, positions };
          } catch (err) {
            console.error(`Failed to fetch positions for portfolio ${portfolio.id}:`, err);
            return { ...portfolio, positions: [] };
          }
        })
      );
      
      setPortfoliosWithPositions(portfoliosWithPos);
    } catch (err) {
      setError('Failed to fetch portfolios');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolios();
  }, [user, onPortfolioCreated]);

  const handleDelete = async (portfolioId: string) => {
    if (!confirm('Are you sure you want to delete this portfolio?')) return;

    try {
      await deletePortfolio(portfolioId);
      setPortfolios(portfolios.filter(p => p.id !== portfolioId));
      setPortfoliosWithPositions(portfoliosWithPositions.filter(p => p.id !== portfolioId));
    } catch (err) {
      setError('Failed to delete portfolio');
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading portfolios...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (portfolios.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>You haven't created any portfolios yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {portfoliosWithPositions.map((portfolio) => (
        <PortfolioCard
          key={portfolio.id}
          portfolio={portfolio}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}

function PortfolioCard({ portfolio, onDelete }: { portfolio: PortfolioWithPositions; onDelete: (id: string) => void }) {
  const { positions: positionsWithPrices, loading: pricesLoading } = useStockPrices(portfolio.positions);
  
  // Calculate current portfolio metrics
  const currentTotalValue = positionsWithPrices.reduce((sum, position) => {
    if (position.status === 'open') {
      return sum + position.currentTotalValue;
    } else {
      return sum + position.totalValue;
    }
  }, 0);

  const currentGainLoss = positionsWithPrices.reduce((sum, position) => {
    if (position.status === 'open') {
      return sum + position.currentGainLoss;
    } else {
      return sum + position.gainLoss;
    }
  }, 0);

  const totalInvestment = positionsWithPrices.reduce((sum, position) => {
    return sum + (position.openPrice * position.quantity);
  }, 0);
  
  const currentGainLossPercent = totalInvestment > 0 ? (currentGainLoss / totalInvestment) * 100 : 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{portfolio.name}</h3>
            {portfolio.isPublic && (
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                Public
              </span>
            )}
            {portfolio.isBotPortfolio === true && (
              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">
                🤖 Bot
              </span>
            )}
            {pricesLoading && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                Updating...
              </span>
            )}
          </div>
          
          {portfolio.description && (
            <p className="text-gray-600 mb-3">{portfolio.description}</p>
          )}
          
          {portfolio.goal && (
            <div className="mb-3 p-3 bg-blue-50 rounded-lg">
              <h4 className="text-sm font-medium text-blue-900 mb-1">Investment Goal</h4>
              <p className="text-sm text-blue-800">{portfolio.goal}</p>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <span className="text-sm text-gray-500">Total Value</span>
              <p className="text-lg font-semibold text-gray-900">
                {formatCurrency(currentTotalValue)}
              </p>
            </div>
            
            <div>
              <span className="text-sm text-gray-500">Cash Balance</span>
              <p className="text-lg font-semibold text-gray-900">
                {formatCurrency(portfolio.cashBalance || 0)}
              </p>
            </div>
            
            <div>
              <span className="text-sm text-gray-500">Unrealized Gain/Loss</span>
              <p className={`text-lg font-semibold ${
                currentGainLoss >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(currentGainLoss)}
              </p>
            </div>
            
            <div>
              <span className="text-sm text-gray-500">Unrealized Gain/Loss %</span>
              <p className={`text-lg font-semibold ${
                currentGainLossPercent >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatPercentage(currentGainLossPercent)}
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2 ml-4">
          <Link
            href={`/portfolio/${portfolio.id}`}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
          >
            View
          </Link>
          <button
            onClick={() => onDelete(portfolio.id)}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}