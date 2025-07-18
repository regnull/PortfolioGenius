'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { createPortfolio } from '@/lib/firestore';
import { Portfolio } from '@/types';

interface CreatePortfolioFormProps {
  onSuccess?: (portfolioId: string) => void;
  onCancel?: () => void;
}

export default function CreatePortfolioForm({ onSuccess, onCancel }: CreatePortfolioFormProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [goal, setGoal] = useState('Design a moderate-risk investment portfolio aimed at achieving steady long-term growth through a diversified mix of asset classes, balancing capital appreciation with risk mitigation. The portfolio should target above-inflation returns while maintaining resilience during market volatility, avoiding highly speculative assets and minimizing large drawdowns.');
  const [initialCashBalance, setInitialCashBalance] = useState('10000');
  const [isPublic, setIsPublic] = useState(false);
  const [isBotPortfolio, setIsBotPortfolio] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setLoading(true);
    setError('');

    try {
      const cashBalance = parseFloat(initialCashBalance);
      
      // Validate cash balance
      if (isNaN(cashBalance) || cashBalance < 0) {
        setError('Initial cash balance must be a non-negative number');
        setLoading(false);
        return;
      }

      // Build portfolio data object, only including description if it has a value
      const portfolioData: Omit<Portfolio, 'id'> = {
        userId: user.uid,
        name,
        goal: goal.trim(),
        isPublic,
        isBotPortfolio: isBotPortfolio || false,
        cashBalance: cashBalance,
        initialCashBalance: cashBalance,
        totalValue: 0,
        totalGainLoss: 0,
        totalGainLossPercent: 0,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      // Only add description if it's not empty
      if (description.trim()) {
        portfolioData.description = description.trim();
      }

      const portfolioId = await createPortfolio(portfolioData);

      setName('');
      setDescription('');
      setGoal('Design a moderate-risk investment portfolio aimed at achieving steady long-term growth through a diversified mix of asset classes, balancing capital appreciation with risk mitigation. The portfolio should target above-inflation returns while maintaining resilience during market volatility, avoiding highly speculative assets and minimizing large drawdowns.');
      setInitialCashBalance('10000');
      setIsPublic(false);
      setIsBotPortfolio(false);
      
      if (onSuccess) {
        onSuccess(portfolioId);
      }
    } catch (err) {
      setError('Failed to create portfolio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Portfolio</h3>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Portfolio Name *
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            placeholder="My Investment Portfolio"
          />
        </div>

        <div>
          <label htmlFor="goal" className="block text-sm font-medium text-gray-700 mb-1">
            Investment Goal *
          </label>
          <textarea
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            required
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            placeholder="Define your investment goal and strategy..."
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            placeholder="Optional description of your portfolio strategy..."
          />
        </div>

        <div>
          <label htmlFor="initialCashBalance" className="block text-sm font-medium text-gray-700 mb-1">
            Initial Cash Balance *
          </label>
          <input
            type="number"
            id="initialCashBalance"
            value={initialCashBalance}
            onChange={(e) => setInitialCashBalance(e.target.value)}
            required
            min="0"
            step="0.01"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            placeholder="10000"
          />
          <p className="mt-1 text-sm text-gray-500">
            Starting cash amount available for investments
          </p>
        </div>

        <div className="space-y-3">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="isPublic"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="isPublic" className="ml-2 block text-sm text-gray-900">
              Make this portfolio public
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="isBotPortfolio"
              checked={isBotPortfolio}
              onChange={(e) => setIsBotPortfolio(e.target.checked)}
              className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            />
            <label htmlFor="isBotPortfolio" className="ml-2 block text-sm text-gray-900">
              This is a bot portfolio
            </label>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={loading || !name.trim() || !goal.trim() || !initialCashBalance.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Creating...' : 'Create Portfolio'}
          </button>
        </div>
      </form>
    </div>
  );
}