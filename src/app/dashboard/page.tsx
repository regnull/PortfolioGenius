'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import CreatePortfolioForm from '@/components/portfolio/CreatePortfolioForm';
import PortfolioList from '@/components/portfolio/PortfolioList';
import { migrateUserData } from '@/lib/firestore';

export default function Dashboard() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [portfolioCreated, setPortfolioCreated] = useState(false);
  const [migrating, setMigrating] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  const handlePortfolioCreated = (portfolioId: string) => {
    setShowCreateForm(false);
    setPortfolioCreated(!portfolioCreated);
  };

  const handleMigrate = async () => {
    if (!user) return;
    setMigrating(true);
    try {
      await migrateUserData(user.uid);
      alert('Migration complete');
    } catch (err) {
      console.error('Migration failed', err);
      alert('Migration failed');
    } finally {
      setMigrating(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold text-gray-900">Portfolio Genius</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.displayName || user.email}!</span>
              <button
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Your Portfolios</h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                {showCreateForm ? 'Cancel' : 'Create Portfolio'}
              </button>
              <button
                onClick={handleMigrate}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                {migrating ? 'Migrating...' : 'Migrate Data'}
              </button>
            </div>
          </div>

          {showCreateForm && (
            <div className="mb-6">
              <CreatePortfolioForm
                onSuccess={handlePortfolioCreated}
                onCancel={() => setShowCreateForm(false)}
              />
            </div>
          )}

          <PortfolioList onPortfolioCreated={portfolioCreated} />
        </div>
      </main>
    </div>
  );
}