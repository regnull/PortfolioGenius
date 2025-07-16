'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { getPortfolio, getPositions, deletePosition } from '@/lib/firestore';
import { Portfolio, Position } from '@/types';
import AddPositionForm from '@/components/portfolio/AddPositionForm';
import ClosePositionForm from '@/components/portfolio/ClosePositionForm';
import Link from 'next/link';

export default function PortfolioPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [positionToClose, setPositionToClose] = useState<Position | null>(null);

  const fetchPositions = async () => {
    if (!params.id) return;
    try {
      const positionData = await getPositions(params.id as string);
      setPositions(positionData);
    } catch (err) {
      console.error('Failed to fetch positions:', err);
    }
  };

  useEffect(() => {
    const fetchPortfolio = async () => {
      if (!user || !params.id) return;

      try {
        const portfolioData = await getPortfolio(params.id as string);
        
        if (!portfolioData) {
          setError('Portfolio not found');
          return;
        }

        // Check if user owns this portfolio or if it's public
        if (portfolioData.userId !== user.uid && !portfolioData.isPublic) {
          setError('You do not have permission to view this portfolio');
          return;
        }

        setPortfolio(portfolioData);
        
        // Fetch positions for this portfolio
        await fetchPositions();
      } catch (err) {
        setError('Failed to load portfolio');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [user, params.id]);

  const handleDeletePosition = async (positionId: string) => {
    if (!confirm('Are you sure you want to delete this position?')) return;
    
    try {
      await deletePosition(positionId);
      setPositions(positions.filter(p => p.id !== positionId));
    } catch (err) {
      alert('Failed to delete position');
    }
  };

  const renderPositionsTable = (filteredPositions: Position[], type: 'open' | 'closed') => {
    if (filteredPositions.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No {type} positions</p>
          {type === 'open' && (
            <p className="text-sm mt-2">Start building your portfolio by adding your first position.</p>
          )}
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Open Price</th>
              {type === 'closed' && (
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Close Price</th>
              )}
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Total Value</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Gain/Loss</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredPositions.map((position) => (
              <tr key={position.id} className="hover:bg-gray-50">
                <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {position.symbol}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                  {position.name}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                    {position.type}
                  </span>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                  {position.quantity}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${position.openPrice.toFixed(2)}
                </td>
                {type === 'closed' && (
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${position.closePrice?.toFixed(2) || 'N/A'}
                  </td>
                )}
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${position.totalValue.toFixed(2)}
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm">
                  <span className={`font-medium ${
                    position.gainLoss >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${position.gainLoss.toFixed(2)} ({position.gainLossPercent.toFixed(2)}%)
                  </span>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm space-x-2">
                  {type === 'open' && (
                    <button
                      onClick={() => setPositionToClose(position)}
                      className="text-orange-600 hover:text-orange-900 font-medium"
                    >
                      Close
                    </button>
                  )}
                  <button
                    onClick={() => handleDeletePosition(position.id)}
                    className="text-red-600 hover:text-red-900 font-medium"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Error</h2>
            <p>{error}</p>
            <Link
              href="/dashboard"
              className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Portfolio not found</h2>
          <Link
            href="/dashboard"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <Link
                href="/dashboard"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium mb-2 inline-block"
              >
                ← Back to Dashboard
              </Link>
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold text-gray-900">{portfolio.name}</h1>
                {portfolio.isPublic && (
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
                    Public
                  </span>
                )}
              </div>
              {portfolio.description && (
                <p className="mt-2 text-gray-600">{portfolio.description}</p>
              )}
            </div>
          </div>
        </div>

        {/* Portfolio Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Value</h3>
            <p className="text-3xl font-bold text-gray-900">
              ${portfolio.totalValue.toFixed(2)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Gain/Loss</h3>
            <p className={`text-3xl font-bold ${
              portfolio.totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              ${portfolio.totalGainLoss.toFixed(2)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Gain/Loss %</h3>
            <p className={`text-3xl font-bold ${
              portfolio.totalGainLossPercent >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {portfolio.totalGainLossPercent.toFixed(2)}%
            </p>
          </div>
        </div>

        {/* Close Position Modal */}
        {positionToClose && (
          <ClosePositionForm
            position={positionToClose}
            onSuccess={() => {
              // Refresh positions after closing
              fetchPositions();
              setPositionToClose(null);
            }}
            onCancel={() => setPositionToClose(null)}
          />
        )}

        {/* Add Position Form */}
        {showAddForm && (
          <div className="mb-8">
            <AddPositionForm
              portfolioId={portfolio.id}
              onSuccess={(position) => {
                setPositions([position, ...positions]);
                setShowAddForm(false);
              }}
              onCancel={() => setShowAddForm(false)}
            />
          </div>
        )}

        {/* Open Positions Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Open Positions</h2>
            <button 
              onClick={() => setShowAddForm(!showAddForm)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              {showAddForm ? 'Cancel' : 'Add Position'}
            </button>
          </div>
          
          {renderPositionsTable(positions.filter(p => p.status === 'open'), 'open')}
        </div>

        {/* Closed Positions Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Closed Positions</h2>
          </div>
          
          {renderPositionsTable(positions.filter(p => p.status === 'closed'), 'closed')}
        </div>

        {/* Portfolio Info */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Created:</span>
              <span className="ml-2 text-gray-900">
                {portfolio.createdAt.toDate().toLocaleDateString()}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Last Updated:</span>
              <span className="ml-2 text-gray-900">
                {portfolio.updatedAt.toDate().toLocaleDateString()}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Visibility:</span>
              <span className="ml-2 text-gray-900">
                {portfolio.isPublic ? 'Public' : 'Private'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}