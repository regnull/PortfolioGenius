import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  addDoc, 
  updateDoc, 
  deleteDoc,
  setDoc,
  query, 
  where, 
  orderBy, 
  limit,
  serverTimestamp,
  onSnapshot,
  Unsubscribe,
  Timestamp
} from 'firebase/firestore';
import { db } from './firebase';
import { User, Portfolio, Trade, Position, SuggestedTrade } from '@/types';

// Helper function to convert Firestore data to Portfolio with proper Date objects
const convertFirestoreToPortfolio = (id: string, data: Record<string, unknown>): Portfolio => {
  return {
    id,
    ...data,
    initialCashBalance: data.initialCashBalance as number,
    createdAt: data.createdAt instanceof Timestamp ? data.createdAt.toDate() : new Date(data.createdAt as string),
    updatedAt: data.updatedAt instanceof Timestamp ? data.updatedAt.toDate() : new Date(data.updatedAt as string),
  } as Portfolio;
};

export const createUser = async (userId: string, userData: Omit<User, 'id'>) => {
  try {
    await updateDoc(doc(db, 'users', userId), {
      ...userData,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

export const getUser = async (userId: string): Promise<User | null> => {
  try {
    const userDoc = await getDoc(doc(db, 'users', userId));
    if (userDoc.exists()) {
      return { id: userDoc.id, ...userDoc.data() } as User;
    }
    return null;
  } catch (error) {
    console.error('Error getting user:', error);
    throw error;
  }
};

export const createPortfolio = async (portfolioData: Omit<Portfolio, 'id'>) => {
  try {
    const docRef = await addDoc(collection(db, 'portfolios'), {
      ...portfolioData,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
    return docRef.id;
  } catch (error) {
    console.error('Error creating portfolio:', error);
    throw error;
  }
};

export const getPortfolio = async (portfolioId: string): Promise<Portfolio | null> => {
  try {
    const portfolioDoc = await getDoc(doc(db, 'portfolios', portfolioId));
    if (portfolioDoc.exists()) {
      return convertFirestoreToPortfolio(portfolioDoc.id, portfolioDoc.data());
    }
    return null;
  } catch (error) {
    console.error('Error getting portfolio:', error);
    throw error;
  }
};

export const getPortfolios = async (userId: string): Promise<Portfolio[]> => {
  try {
    const q = query(
      collection(db, 'portfolios'),
      where('userId', '==', userId),
      orderBy('createdAt', 'desc')
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => convertFirestoreToPortfolio(doc.id, doc.data()));
  } catch (error) {
    console.error('Error getting portfolios:', error);
    throw error;
  }
};

export const getPublicPortfolios = async (): Promise<Portfolio[]> => {
  try {
    const q = query(
      collection(db, 'portfolios'),
      where('isPublic', '==', true),
      orderBy('createdAt', 'desc'),
      limit(50)
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => convertFirestoreToPortfolio(doc.id, doc.data()));
  } catch (error) {
    console.error('Error getting public portfolios:', error);
    throw error;
  }
};

export const updatePortfolio = async (portfolioId: string, updates: Partial<Portfolio>) => {
  try {
    await updateDoc(doc(db, 'portfolios', portfolioId), {
      ...updates,
      updatedAt: serverTimestamp()
    });
  } catch (error) {
    console.error('Error updating portfolio:', error);
    throw error;
  }
};

export const deletePortfolio = async (portfolioId: string) => {
  try {
    await deleteDoc(doc(db, 'portfolios', portfolioId));
  } catch (error) {
    console.error('Error deleting portfolio:', error);
    throw error;
  }
};

export const addTrade = async (portfolioId: string, tradeData: Omit<Trade, 'id' | 'portfolioId'>) => {
  try {
    const docRef = await addDoc(collection(db, 'portfolios', portfolioId, 'trades'), {
      ...tradeData,
      portfolioId,
      date: serverTimestamp()
    });
    return docRef.id;
  } catch (error) {
    console.error('Error adding trade:', error);
    throw error;
  }
};

export const getTrades = async (portfolioId: string): Promise<Trade[]> => {
  try {
    const q = query(
      collection(db, 'portfolios', portfolioId, 'trades'),
      orderBy('date', 'desc')
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    } as Trade));
  } catch (error) {
    console.error('Error getting trades:', error);
    throw error;
  }
};

export const updateTrade = async (portfolioId: string, tradeId: string, updates: Partial<Trade>) => {
  try {
    await updateDoc(doc(db, 'portfolios', portfolioId, 'trades', tradeId), updates);
  } catch (error) {
    console.error('Error updating trade:', error);
    throw error;
  }
};

export const deleteTrade = async (portfolioId: string, tradeId: string) => {
  try {
    await deleteDoc(doc(db, 'portfolios', portfolioId, 'trades', tradeId));
  } catch (error) {
    console.error('Error deleting trade:', error);
    throw error;
  }
};

export const recalculateCashBalance = async (portfolioId: string) => {
  try {
    // Fetch portfolio to get initial cash
    const portfolioRef = doc(db, 'portfolios', portfolioId);
    const portfolioSnap = await getDoc(portfolioRef);
    if (!portfolioSnap.exists()) {
      throw new Error('Portfolio not found');
    }

    const portfolioData = portfolioSnap.data();
    const initialCash = portfolioData.initialCashBalance || 0;

    // Sum up all trades to compute cash impact
    const trades = await getTrades(portfolioId);

    let cash = initialCash;
    trades.forEach((trade) => {
      const total = (trade.price * trade.quantity) + (trade.fees || 0);
      if (trade.type === 'BuyToOpen') {
        cash -= total;
      } else if (trade.type === 'SellToClose') {
        cash += (trade.price * trade.quantity) - (trade.fees || 0);
      }
    });

    await updateDoc(portfolioRef, {
      cashBalance: cash,
      updatedAt: serverTimestamp(),
    });

    return cash;
  } catch (error) {
    console.error('Error recalculating cash balance:', error);
    throw error;
  }
};

export const addPosition = async (positionData: Omit<Position, 'id'>) => {
  try {
    const docRef = await addDoc(
      collection(db, 'portfolios', positionData.portfolioId, 'positions'),
      {
        ...positionData,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      }
    );
    
    // Create BuyToOpen trade record
    await addTrade(positionData.portfolioId, {
      symbol: positionData.symbol,
      type: 'BuyToOpen',
      quantity: positionData.quantity,
      price: positionData.openPrice,
      fees: positionData.fees,
      positionId: docRef.id,
      notes: `Opened position in ${positionData.name || positionData.symbol}`
    });
    
    // Update portfolio cash balance (decrease cash for purchase)
    const portfolioRef = doc(db, 'portfolios', positionData.portfolioId);
    const portfolioDoc = await getDoc(portfolioRef);
    
    if (portfolioDoc.exists()) {
      const portfolioData = portfolioDoc.data();
      const currentCash = portfolioData.cashBalance || 0;
      const totalCost = (positionData.totalValue || 0) + (positionData.fees || 0);
      
      await updateDoc(portfolioRef, {
        cashBalance: currentCash - totalCost,
        updatedAt: serverTimestamp()
      });
    }
    
    // Update portfolio totals after adding position
    await updatePortfolioTotals(positionData.portfolioId);
    
    return docRef.id;
  } catch (error) {
    console.error('Error adding position:', error);
    throw error;
  }
};

export const getPositions = async (portfolioId: string): Promise<Position[]> => {
  try {
    const q = query(
      collection(db, 'portfolios', portfolioId, 'positions'),
      orderBy('createdAt', 'desc')
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    } as Position));
  } catch (error) {
    console.error('Error getting positions:', error);
    throw error;
  }
};

export const updatePosition = async (
  portfolioId: string,
  positionId: string,
  updates: Partial<Position>
) => {
  try {
    await updateDoc(doc(db, 'portfolios', portfolioId, 'positions', positionId), {
      ...updates,
      updatedAt: serverTimestamp()
    });
  } catch (error) {
    console.error('Error updating position:', error);
    throw error;
  }
};

export const closePosition = async (
  portfolioId: string,
  positionId: string,
  closePrice: number,
  quantityToClose?: number,
  closeFees?: number
) => {
  try {
    const positionDoc = await getDoc(doc(db, 'portfolios', portfolioId, 'positions', positionId));
    if (!positionDoc.exists()) {
      throw new Error('Position not found');
    }
    
    const position = positionDoc.data() as Position;
    const closeQuantity = quantityToClose || position.quantity;
    const fees = closeFees || 0;
    
    if (closeQuantity > position.quantity) {
      throw new Error('Cannot close more than the available quantity');
    }
    
    const gainLoss = (closePrice - position.openPrice) * closeQuantity;
    const gainLossPercent = ((closePrice - position.openPrice) / position.openPrice) * 100;
    
    // Calculate cash received from closing position (proceeds minus fees)
    const cashReceived = (closePrice * closeQuantity) - fees;
    
    if (closeQuantity === position.quantity) {
      // Full close - update the existing position
      await updateDoc(doc(db, 'portfolios', portfolioId, 'positions', positionId), {
        status: 'closed',
        closePrice,
        closeDate: serverTimestamp(),
        gainLoss,
        gainLossPercent,
        totalValue: closePrice * closeQuantity,
        fees: fees,
        updatedAt: serverTimestamp()
      });
      
      // Create SellToClose trade record for full close
      await addTrade(position.portfolioId, {
        symbol: position.symbol,
        type: 'SellToClose',
        quantity: closeQuantity,
        price: closePrice,
        fees: fees,
        positionId: positionId,
        notes: `Closed full position in ${position.name || position.symbol}`
      });
    } else {
      // Partial close - create a new closed position and update the original
      const closedPositionData = {
        ...position,
        quantity: closeQuantity,
        status: 'closed' as const,
        closePrice,
        closeDate: new Date(),
        gainLoss,
        gainLossPercent,
        totalValue: closePrice * closeQuantity,
        fees: fees,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      // Remove the id from the data to avoid conflicts
      const { id: _, ...positionDataWithoutId } = closedPositionData;
      
      // Create new closed position
      const newClosedPositionDoc = await addDoc(
        collection(db, 'portfolios', portfolioId, 'positions'),
        {
          ...positionDataWithoutId,
          closeDate: serverTimestamp(),
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp()
        }
      );
      
      // Create SellToClose trade record for partial close
      await addTrade(position.portfolioId, {
        symbol: position.symbol,
        type: 'SellToClose',
        quantity: closeQuantity,
        price: closePrice,
        fees: fees,
        positionId: newClosedPositionDoc.id,
        notes: `Closed partial position in ${position.name || position.symbol}`
      });
      
      // Update original position with remaining quantity
      const remainingQuantity = position.quantity - closeQuantity;
      const remainingTotalValue = position.openPrice * remainingQuantity;
      
      await updateDoc(doc(db, 'portfolios', portfolioId, 'positions', positionId), {
        quantity: remainingQuantity,
        totalValue: remainingTotalValue,
        updatedAt: serverTimestamp()
      });
    }

    // Update portfolio cash balance (increase cash for sale proceeds)
    const portfolioRef = doc(db, 'portfolios', position.portfolioId);
    const portfolioDoc = await getDoc(portfolioRef);
    
    if (portfolioDoc.exists()) {
      const portfolioData = portfolioDoc.data();
      const currentCash = portfolioData.cashBalance || 0;
      
      await updateDoc(portfolioRef, {
        cashBalance: currentCash + cashReceived,
        updatedAt: serverTimestamp()
      });
    }

    // Update portfolio totals after closing position
    await updatePortfolioTotals(portfolioId);
  } catch (error) {
    console.error('Error closing position:', error);
    throw error;
  }
};

export const calculatePortfolioTotals = async (portfolioId: string) => {
  try {
    const positions = await getPositions(portfolioId);
    
    let totalValue = 0;
    let totalGainLoss = 0;
    let totalInvestment = 0;
    
    positions.forEach(position => {
      if (position.status === 'closed') {
        // For closed positions, use the actual closing values
        totalValue += position.totalValue;
        totalGainLoss += position.gainLoss;
        totalInvestment += position.openPrice * position.quantity;
      } else {
        // For open positions, use current values (assuming current price equals open price for now)
        totalValue += position.totalValue;
        totalGainLoss += position.gainLoss;
        totalInvestment += position.openPrice * position.quantity;
      }
    });
    
    const totalGainLossPercent = totalInvestment > 0 ? (totalGainLoss / totalInvestment) * 100 : 0;
    
    return {
      totalValue,
      totalGainLoss,
      totalGainLossPercent
    };
  } catch (error) {
    console.error('Error calculating portfolio totals:', error);
    throw error;
  }
};

export const updatePortfolioTotals = async (portfolioId: string) => {
  try {
    const totals = await calculatePortfolioTotals(portfolioId);
    
    await updateDoc(doc(db, 'portfolios', portfolioId), {
      totalValue: totals.totalValue,
      totalGainLoss: totals.totalGainLoss,
      totalGainLossPercent: totals.totalGainLossPercent,
      updatedAt: serverTimestamp()
    });
  } catch (error) {
    console.error('Error updating portfolio totals:', error);
    throw error;
  }
};

export const getClosedPositions = async (
  portfolioId: string
): Promise<Position[]> => {
  try {
    const q = query(
      collection(db, 'portfolios', portfolioId, 'positions'),
      where('status', '==', 'closed'),
      orderBy('closeDate', 'desc')
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    } as Position));
  } catch (error) {
    console.error('Error getting closed positions:', error);
    throw error;
  }
};

export const getOpenPositions = async (
  portfolioId: string
): Promise<Position[]> => {
  try {
    const q = query(
      collection(db, 'portfolios', portfolioId, 'positions'),
      where('status', '==', 'open'),
      orderBy('createdAt', 'desc')
    );
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    } as Position));
  } catch (error) {
    console.error('Error getting open positions:', error);
    throw error;
  }
};

export const deletePosition = async (
  portfolioId: string,
  positionId: string
) => {
  try {
    // Verify position exists before attempting to delete
    const positionRef = doc(db, 'portfolios', portfolioId, 'positions', positionId);
    const positionDoc = await getDoc(positionRef);
    if (!positionDoc.exists()) {
      throw new Error('Position not found');
    }

    // Delete all trades associated with this position
    const tradesQuery = query(
      collection(db, 'portfolios', portfolioId, 'trades'),
      where('positionId', '==', positionId)
    );
    const tradesSnap = await getDocs(tradesQuery);
    const deleteTradePromises = tradesSnap.docs.map((trade) =>
      deleteDoc(doc(db, 'portfolios', portfolioId, 'trades', trade.id))
    );
    await Promise.all(deleteTradePromises);

    // Delete the position itself
    await deleteDoc(positionRef);

    // Recalculate cash balance after removing trades
    await recalculateCashBalance(portfolioId);

    // Update portfolio totals after deleting position
    await updatePortfolioTotals(portfolioId);
  } catch (error) {
    console.error('Error deleting position:', error);
    throw error;
  }
};

export const updateSuggestedTradeStatus = async (
  portfolioId: string,
  tradeId: string,
  status: 'pending' | 'converted' | 'dismissed'
) => {
  try {
    const updateData: any = {
      status,
      updatedAt: serverTimestamp()
    };

    if (status === 'converted') {
      updateData.convertedAt = serverTimestamp();
    } else if (status === 'dismissed') {
      updateData.dismissedAt = serverTimestamp();
    }

    await updateDoc(
      doc(db, 'portfolios', portfolioId, 'suggestedTrades', tradeId),
      updateData
    );
  } catch (error) {
    console.error('Error updating suggested trade status:', error);
    throw error;
  }
};

export const subscribeSuggestedTrades = (
  portfolioId: string,
  userId: string,
  callback: (trades: SuggestedTrade[]) => void,
  status?: 'pending' | 'converted' | 'dismissed'
): Unsubscribe => {
  try {
    let q = query(
      collection(db, 'portfolios', portfolioId, 'suggestedTrades'),
      where('userId', '==', userId),
      orderBy('createdAt', 'desc')
    );

    // Add status filter if provided
    if (status) {
      q = query(
        collection(db, 'portfolios', portfolioId, 'suggestedTrades'),
        where('userId', '==', userId),
        where('status', '==', status),
        orderBy('createdAt', 'desc')
      );
    }

    return onSnapshot(q, (snapshot) => {
      const trades: SuggestedTrade[] = [];
      snapshot.forEach((doc) => {
        const data = doc.data();
        trades.push({
          id: doc.id,
          ...data,
          // Convert Firestore timestamps to Date objects
          createdAt: data.createdAt?.toDate() || new Date(),
          updatedAt: data.updatedAt?.toDate() || new Date(),
          dismissedAt: data.dismissedAt?.toDate() || undefined,
        } as SuggestedTrade);
      });
      callback(trades);
    });
  } catch (error) {
    console.error('Error setting up suggested trades listener:', error);
    throw error;
  }
};
