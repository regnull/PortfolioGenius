'use client';

import { useState } from 'react';
import { closePosition } from '@/lib/firestore';
import { Position } from '@/types';
import { formatCurrency, formatPercentage } from '@/lib/currency';

interface ClosePositionFormProps {
  position: Position;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function ClosePositionForm({ position, onSuccess, onCancel }: ClosePositionFormProps) {
  const [closePrice, setClosePrice] = useState('');
  const [quantity, setQuantity] = useState(position.quantity.toString());
  const [fees, setFees] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!closePrice || !quantity) {
      setError('Please enter both closing price and quantity');
      return;
    }

    const priceNum = parseFloat(closePrice);
    const quantityNum = parseFloat(quantity);
    const feesNum = parseFloat(fees) || 0;
    
    if (priceNum <= 0) {
      setError('Closing price must be a positive number');
      return;
    }
    
    if (quantityNum <= 0 || quantityNum > position.quantity) {
      setError(`Quantity must be between 1 and ${position.quantity}`);
      return;
    }

    if (feesNum < 0) {
      setError('Fees cannot be negative');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await closePosition(position.id, priceNum, quantityNum, feesNum);
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setError('Failed to close position');
    } finally {
      setLoading(false);
    }
  };

  const projectedQuantity = quantity ? parseFloat(quantity) : 0;
  const projectedGainLoss = closePrice && quantity
    ? (parseFloat(closePrice) - position.openPrice) * projectedQuantity
    : 0;
  
  const projectedGainLossPercent = closePrice 
    ? ((parseFloat(closePrice) - position.openPrice) / position.openPrice) * 100 
    : 0;
    
  const isPartialClose = projectedQuantity > 0 && projectedQuantity < position.quantity;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Close Position</h3>
          
          <div className="mb-4 p-3 bg-gray-50 rounded-md">
            <p className="text-sm text-gray-600">
              <span className="font-medium">{position.symbol}</span> - {position.name}
            </p>
            <p className="text-sm text-gray-600">
              Quantity: {position.quantity} @ {formatCurrency(position.openPrice)}
            </p>
            <p className="text-sm text-gray-600">
              Current Value: {formatCurrency(position.openPrice * position.quantity)}
            </p>
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity to Close *
                </label>
                <input
                  type="number"
                  id="quantity"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  required
                  min="1"
                  max={position.quantity}
                  step="0.000001"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                  placeholder={position.quantity.toString()}
                />
                <p className="text-xs text-gray-500 mt-1">Max: {position.quantity}</p>
              </div>
              
              <div>
                <label htmlFor="closePrice" className="block text-sm font-medium text-gray-700 mb-1">
                  Closing Price *
                </label>
                <input
                  type="number"
                  id="closePrice"
                  value={closePrice}
                  onChange={(e) => setClosePrice(e.target.value)}
                  required
                  min="0"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div>
              <label htmlFor="fees" className="block text-sm font-medium text-gray-700 mb-1">
                Transaction Fees
              </label>
              <input
                type="number"
                id="fees"
                value={fees}
                onChange={(e) => setFees(e.target.value)}
                min="0"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                placeholder="0.00"
              />
            </div>

            {closePrice && quantity && (
              <div className="space-y-3">
                {isPartialClose && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <h4 className="text-sm font-medium text-yellow-800 mb-1">Partial Close</h4>
                    <p className="text-sm text-yellow-700">
                      This will split your position into:
                    </p>
                    <ul className="text-sm text-yellow-700 mt-1 ml-4 list-disc">
                      <li>Closed: {projectedQuantity} shares</li>
                      <li>Remaining open: {position.quantity - projectedQuantity} shares</li>
                    </ul>
                  </div>
                )}
                
                <div className="p-3 bg-blue-50 rounded-md">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Projected Results for Closed Portion:</h4>
                  <p className="text-sm text-gray-600">
                    Closing Value: {formatCurrency(parseFloat(closePrice) * projectedQuantity)}
                  </p>
                  <p className={`text-sm font-medium ${
                    projectedGainLoss >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    Gain/Loss: {formatCurrency(projectedGainLoss)} ({formatPercentage(projectedGainLossPercent)})
                  </p>
                </div>
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !closePrice || !quantity}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Closing...' : (isPartialClose ? 'Partially Close Position' : 'Close Position')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}