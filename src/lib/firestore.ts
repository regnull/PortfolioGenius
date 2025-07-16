import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  addDoc, 
  updateDoc, 
  deleteDoc, 
  query, 
  where, 
  orderBy, 
  limit,
  serverTimestamp
} from 'firebase/firestore';
import { db } from './firebase';
import { User, Portfolio, Trade, Position } from '@/types';

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
      return { id: portfolioDoc.id, ...portfolioDoc.data() } as Portfolio;
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
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    } as Portfolio));
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
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    } as Portfolio));
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

export const addTrade = async (tradeData: Omit<Trade, 'id'>) => {
  try {
    const docRef = await addDoc(collection(db, 'trades'), {
      ...tradeData,
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
      collection(db, 'trades'),
      where('portfolioId', '==', portfolioId),
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

export const updateTrade = async (tradeId: string, updates: Partial<Trade>) => {
  try {
    await updateDoc(doc(db, 'trades', tradeId), updates);
  } catch (error) {
    console.error('Error updating trade:', error);
    throw error;
  }
};

export const deleteTrade = async (tradeId: string) => {
  try {
    await deleteDoc(doc(db, 'trades', tradeId));
  } catch (error) {
    console.error('Error deleting trade:', error);
    throw error;
  }
};

export const addPosition = async (positionData: Omit<Position, 'id'>) => {
  try {
    const docRef = await addDoc(collection(db, 'positions'), {
      ...positionData,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
    return docRef.id;
  } catch (error) {
    console.error('Error adding position:', error);
    throw error;
  }
};

export const getPositions = async (portfolioId: string): Promise<Position[]> => {
  try {
    const q = query(
      collection(db, 'positions'),
      where('portfolioId', '==', portfolioId),
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

export const updatePosition = async (positionId: string, updates: Partial<Position>) => {
  try {
    await updateDoc(doc(db, 'positions', positionId), {
      ...updates,
      updatedAt: serverTimestamp()
    });
  } catch (error) {
    console.error('Error updating position:', error);
    throw error;
  }
};

export const closePosition = async (positionId: string, closePrice: number, quantityToClose?: number) => {
  try {
    const positionDoc = await getDoc(doc(db, 'positions', positionId));
    if (!positionDoc.exists()) {
      throw new Error('Position not found');
    }
    
    const position = positionDoc.data() as Position;
    const closeQuantity = quantityToClose || position.quantity;
    
    if (closeQuantity > position.quantity) {
      throw new Error('Cannot close more than the available quantity');
    }
    
    const gainLoss = (closePrice - position.openPrice) * closeQuantity;
    const gainLossPercent = ((closePrice - position.openPrice) / position.openPrice) * 100;
    
    if (closeQuantity === position.quantity) {
      // Full close - update the existing position
      await updateDoc(doc(db, 'positions', positionId), {
        status: 'closed',
        closePrice,
        closeDate: serverTimestamp(),
        gainLoss,
        gainLossPercent,
        totalValue: closePrice * closeQuantity,
        updatedAt: serverTimestamp()
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
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      // Remove the id from the data to avoid conflicts
      delete (closedPositionData as any).id;
      
      // Create new closed position
      await addDoc(collection(db, 'positions'), {
        ...closedPositionData,
        closeDate: serverTimestamp(),
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      });
      
      // Update original position with remaining quantity
      const remainingQuantity = position.quantity - closeQuantity;
      const remainingTotalValue = position.openPrice * remainingQuantity;
      
      await updateDoc(doc(db, 'positions', positionId), {
        quantity: remainingQuantity,
        totalValue: remainingTotalValue,
        updatedAt: serverTimestamp()
      });
    }
  } catch (error) {
    console.error('Error closing position:', error);
    throw error;
  }
};

export const deletePosition = async (positionId: string) => {
  try {
    await deleteDoc(doc(db, 'positions', positionId));
  } catch (error) {
    console.error('Error deleting position:', error);
    throw error;
  }
};