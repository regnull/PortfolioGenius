'use client';

import { useState, useEffect } from 'react';
import { SuggestedTrade, Portfolio } from '@/types';
import { portfolioApiClient } from '@/lib/portfolio-api-client';
import { formatCurrency } from '@/lib/currency';

interface SuggestedTradesProps {
  portfolio: Portfolio;
  onTradeConverted?: () => void;
}

export default function SuggestedTrades({ portfolio, onTradeConverted }: SuggestedTradesProps) {
  const [suggestedTrades, setSuggestedTrades] = useState<SuggestedTrade[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'converted' | 'dismissed'>('pending');

  const fetchSuggestedTrades = async () => {
    setLoading(true);
    setError('');
    
    try {
      console.log(`Fetching suggested trades for portfolio ${portfolio.id} with filter: ${filter}`);
      const response = await portfolioApiClient.getSuggestedTrades(
        portfolio.id,
        filter === 'all' ? undefined : filter
      );
      console.log(`Received ${response.suggested_trades.length} suggested trades:`, response.suggested_trades);
      setSuggestedTrades(response.suggested_trades);
    } catch (err) {
      console.error('Error fetching suggested trades:', err);
      setError(`Failed to fetch suggested trades: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const clearAllPendingTrades = async () => {
    setLoading(true);
    setError('');
    
    try {
      console.log('Manually clearing all pending trades...');
      const existingTrades = await portfolioApiClient.getSuggestedTrades(portfolio.id, 'pending');
      console.log('Found pending trades to clear:', existingTrades.suggested_trades);
      
      if (existingTrades.suggested_trades.length > 0) {
        const dismissPromises = existingTrades.suggested_trades.map(async (trade) => {
          try {
            console.log(`Manually dismissing trade ${trade.id} (${trade.symbol})`);
            await portfolioApiClient.dismissSuggestedTrade({
              suggested_trade_id: trade.id,
              reason: 'Manually cleared by user'
            });
            console.log(`Successfully dismissed trade ${trade.id}`);
          } catch (err) {
            console.error(`Failed to dismiss trade ${trade.id}:`, err);
            throw err;
          }
        });
        
        await Promise.all(dismissPromises);
        console.log('Manually cleared all pending trades');
        
        // Refresh the list
        await fetchSuggestedTrades();
      }
    } catch (err) {
      console.error('Error clearing trades:', err);
      setError(`Failed to clear trades: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const generateSuggestedTrades = async () => {
    if (!portfolio.goal) {
      setError('Portfolio needs an investment goal to generate suggestions');
      return;
    }

    setGenerating(true);
    setError('');
    
    try {
      // First, clear ALL existing suggested trades (not just pending)
      console.log('Fetching ALL existing trades to clear...');
      const allExistingTrades = await portfolioApiClient.getSuggestedTrades(portfolio.id, undefined);
      console.log('All existing trades:', allExistingTrades);
      
      // Filter to only pending trades for dismissal
      const pendingTrades = allExistingTrades.suggested_trades.filter(trade => trade.status === 'pending');
      
      if (pendingTrades.length > 0) {
        console.log(`Clearing ${pendingTrades.length} existing pending trades`);
        
        // Dismiss all existing pending trades
        const dismissPromises = pendingTrades.map(async (trade) => {
          try {
            console.log(`Dismissing trade ${trade.id} (${trade.symbol})`);
            await portfolioApiClient.dismissSuggestedTrade({
              suggested_trade_id: trade.id,
              reason: 'Auto-dismissed to generate new AI suggestions'
            });
            console.log(`Successfully dismissed trade ${trade.id}`);
          } catch (err) {
            console.error(`Failed to dismiss trade ${trade.id}:`, err);
            throw err;
          }
        });
        
        await Promise.all(dismissPromises);
        console.log('Cleared all existing pending trades');
        
        // Wait a moment for the dismissals to be processed
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      // Now generate new suggested trades
      console.log('Generating new suggested trades...');
      const response = await portfolioApiClient.constructPortfolio({
        portfolio_goal: portfolio.goal,
        portfolio_id: portfolio.id,
        user_id: portfolio.userId,
        create_suggested_trades: true
      });
      
      // Debug logging to understand the response
      console.log('Construct portfolio response:', response);
      
      // Check if the response indicates success
      // The response is successful if it has recommendations or suggested_trades_created
      const isSuccessful = response.success === true || 
                          response.recommendations?.length > 0 || 
                          (response.suggested_trades_created?.count ?? 0) > 0;
      
      if (isSuccessful) {
        // Always refresh the suggested trades list after a successful call
        await fetchSuggestedTrades();
        
        // Provide feedback about what happened
        if (response.suggested_trades_created && response.suggested_trades_created.count > 0) {
          // Success with trades created
          console.log(`Successfully created ${response.suggested_trades_created.count} suggested trades`);
        } else if (response.recommendations && response.recommendations.length > 0) {
          // Success with recommendations but maybe no trades created yet
          console.log(`Received ${response.recommendations.length} recommendations`);
        } else {
          // Success but no meaningful content
          setError('Portfolio analysis completed but no specific trade recommendations were generated. This could be because your portfolio already aligns well with your goals.');
        }
      } else {
        setError(response.message || 'Failed to generate portfolio recommendations');
      }
    } catch (err) {
      setError(`Failed to generate suggestions: ${err instanceof Error ? err.message : 'Unknown error'}`);
      console.error('Error generating suggestions:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleConvertTrade = async (trade: SuggestedTrade) => {
    try {
      await portfolioApiClient.convertSuggestedTrade({
        suggested_trade_id: trade.id
      });
      
      // Refresh the suggested trades list
      await fetchSuggestedTrades();
      
      // Notify parent component to refresh portfolio data
      if (onTradeConverted) {
        onTradeConverted();
      }
    } catch (err) {
      setError(`Failed to convert trade: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const handleDismissTrade = async (trade: SuggestedTrade) => {
    const reason = prompt('Reason for dismissing this trade suggestion (optional):');
    
    try {
      await portfolioApiClient.dismissSuggestedTrade({
        suggested_trade_id: trade.id,
        reason: reason || undefined
      });
      
      // Refresh the suggested trades list
      await fetchSuggestedTrades();
    } catch (err) {
      setError(`Failed to dismiss trade: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  useEffect(() => {
    fetchSuggestedTrades();
  }, [filter]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-blue-100 text-blue-800';
      case 'converted': return 'bg-green-100 text-green-800';
      case 'dismissed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredTrades = suggestedTrades;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">AI Trade Suggestions</h2>
        <div className="flex items-center space-x-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'pending' | 'converted' | 'dismissed')}
            className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="pending">Pending</option>
            <option value="all">All</option>
            <option value="converted">Converted</option>
            <option value="dismissed">Dismissed</option>
          </select>
          <button
            onClick={generateSuggestedTrades}
            disabled={generating || !portfolio.goal}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 transition-colors text-sm"
            title={!portfolio.goal ? 'Portfolio needs an investment goal to generate suggestions' : ''}
          >
            {generating ? 'Generating...' : '🤖 Generate AI Suggestions'}
          </button>
          <button
            onClick={clearAllPendingTrades}
            disabled={loading}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 transition-colors text-sm"
            title="Clear all pending trade suggestions"
          >
            {loading ? 'Clearing...' : 'Clear All Pending'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {!portfolio.goal && (
        <div className="mb-4 p-3 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
          <p className="font-medium">Investment Goal Required</p>
          <p className="text-sm">Add an investment goal to your portfolio to generate AI trade suggestions.</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading suggestions...</p>
        </div>
      ) : filteredTrades.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No {filter === 'all' ? '' : filter} trade suggestions</p>
          <p className="text-sm mt-2">
            {filter === 'pending' 
              ? 'Click "Generate AI Suggestions" to get personalized trade recommendations'
              : `No ${filter} trade suggestions found`
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTrades.map((trade) => (
            <div key={trade.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {trade.action.toUpperCase()} {trade.symbol}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(trade.priority)}`}>
                      {trade.priority} priority
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(trade.status)}`}>
                      {trade.status}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">{trade.name}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <span className="text-xs text-gray-500">Quantity</span>
                      <p className="font-medium">{trade.quantity}</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Est. Price</span>
                      <p className="font-medium">{formatCurrency(trade.estimatedPrice)}</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Est. Total</span>
                      <p className="font-medium">{formatCurrency(trade.quantity * trade.estimatedPrice)}</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Type</span>
                      <p className="font-medium capitalize">{trade.type}</p>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-1">AI Rationale</h4>
                    <p className="text-sm text-gray-600 bg-blue-50 p-2 rounded">{trade.rationale}</p>
                  </div>
                  
                  {trade.notes && (
                    <div className="mb-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Notes</h4>
                      <p className="text-sm text-gray-600">{trade.notes}</p>
                    </div>
                  )}

                  {trade.status === 'dismissed' && trade.dismissedReason && (
                    <div className="mb-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Dismissal Reason</h4>
                      <p className="text-sm text-gray-600">{trade.dismissedReason}</p>
                    </div>
                  )}
                </div>
                
                {trade.status === 'pending' && (
                  <div className="flex flex-col space-y-2 ml-4">
                    <button
                      onClick={() => handleConvertTrade(trade)}
                      className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
                    >
                      Execute Trade
                    </button>
                    <button
                      onClick={() => handleDismissTrade(trade)}
                      className="px-3 py-1 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700 transition-colors"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 