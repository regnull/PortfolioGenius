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
import { User, Portfolio, Trade } from '@/types';

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