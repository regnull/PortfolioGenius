'use client';

import { useState } from 'react';
import { addPosition } from '@/lib/firestore';
import { Position } from '@/types';

interface AddPositionFormProps {
  portfolioId: string;
  onSuccess?: (position: Position) => void;
  onCancel?: () => void;
}

export default function AddPositionForm({ portfolioId, onSuccess, onCancel }: AddPositionFormProps) {
  const [symbol, setSymbol] = useState('');
  const [name, setName] = useState('');
  const [type, setType] = useState<'stock' | 'etf' | 'crypto' | 'bond' | 'other'>('stock');
  const [quantity, setQuantity] = useState('');
  const [openPrice, setOpenPrice] = useState('');
  const [fees, setFees] = useState('');
  const [openDate, setOpenDate] = useState(() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!symbol || !name || !quantity || !openPrice) {
      setError('Please fill in all required fields');
      return;
    }

    const quantityNum = parseFloat(quantity);
    const priceNum = parseFloat(openPrice);
    const feesNum = parseFloat(fees) || 0;

    if (quantityNum <= 0 || priceNum <= 0) {
      setError('Quantity and price must be positive numbers');
      return;
    }

    if (feesNum < 0) {
      setError('Fees cannot be negative');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const positionData = {
        portfolioId,
        symbol: symbol.toUpperCase(),
        name,
        type,
        quantity: quantityNum,
        openPrice: priceNum,
        currentPrice: priceNum, // Will be updated later with real-time data
        openDate: new Date(openDate),
        status: 'open' as const,
        totalValue: quantityNum * priceNum,
        gainLoss: 0, // Will be calculated later
        gainLossPercent: 0, // Will be calculated later
        fees: feesNum,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      const positionId = await addPosition(positionData);
      
      const newPosition: Position = {
        id: positionId,
        ...positionData
      };

      // Reset form
      setSymbol('');
      setName('');
      setType('stock');
      setQuantity('');
      setOpenPrice('');
      setFees('');
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      setOpenDate(`${year}-${month}-${day}`);
      
      if (onSuccess) {
        onSuccess(newPosition);
      }
    } catch (err) {
      setError('Failed to add position');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Position</h3>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 mb-1">
              Symbol *
            </label>
            <input
              type="text"
              id="symbol"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
              placeholder="AAPL"
            />
          </div>

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Company/Asset Name *
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
              placeholder="Apple Inc."
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              id="type"
              value={type}
              onChange={(e) => setType(e.target.value as 'stock' | 'etf' | 'crypto' | 'bond' | 'other')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            >
              <option value="stock">Stock</option>
              <option value="etf">ETF</option>
              <option value="crypto">Cryptocurrency</option>
              <option value="bond">Bond</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
              Quantity *
            </label>
            <input
              type="number"
              id="quantity"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
              min="0"
              step="0.000001"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
              placeholder="100"
            />
          </div>

          <div>
            <label htmlFor="openPrice" className="block text-sm font-medium text-gray-700 mb-1">
              Open Price *
            </label>
            <input
              type="number"
              id="openPrice"
              value={openPrice}
              onChange={(e) => setOpenPrice(e.target.value)}
              required
              min="0"
              step="0.01"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
              placeholder="150.00"
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

        <div>
          <label htmlFor="openDate" className="block text-sm font-medium text-gray-700 mb-1">
            Open Date
          </label>
          <input
            type="date"
            id="openDate"
            value={openDate}
            onChange={(e) => setOpenDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900"
          />
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
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Adding...' : 'Add Position'}
          </button>
        </div>
      </form>
    </div>
  );
}