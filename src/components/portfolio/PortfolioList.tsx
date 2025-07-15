'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getPortfolios, deletePortfolio } from '@/lib/firestore';
import { Portfolio } from '@/types';
import Link from 'next/link';

interface PortfolioListProps {
  onPortfolioCreated?: boolean;
}

export default function PortfolioList({ onPortfolioCreated }: PortfolioListProps) {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const fetchPortfolios = async () => {
    if (!user) return;

    try {
      const userPortfolios = await getPortfolios(user.uid);
      setPortfolios(userPortfolios);
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
      {portfolios.map((portfolio) => (
        <div key={portfolio.id} className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{portfolio.name}</h3>
                {portfolio.isPublic && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                    Public
                  </span>
                )}
              </div>
              
              {portfolio.description && (
                <p className="text-gray-600 mb-3">{portfolio.description}</p>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <span className="text-sm text-gray-500">Total Value</span>
                  <p className="text-lg font-semibold text-gray-900">
                    ${portfolio.totalValue.toFixed(2)}
                  </p>
                </div>
                
                <div>
                  <span className="text-sm text-gray-500">Gain/Loss</span>
                  <p className={`text-lg font-semibold ${
                    portfolio.totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${portfolio.totalGainLoss.toFixed(2)}
                  </p>
                </div>
                
                <div>
                  <span className="text-sm text-gray-500">Gain/Loss %</span>
                  <p className={`text-lg font-semibold ${
                    portfolio.totalGainLossPercent >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {portfolio.totalGainLossPercent.toFixed(2)}%
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
                onClick={() => handleDelete(portfolio.id)}
                className="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}