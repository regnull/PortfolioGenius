import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Portfolio Genius
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Track, manage, and analyze your investment portfolios with ease. 
            Share your performance with the community or keep it private.
          </p>
          
          <div className="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
            <Link
              href="/signup"
              className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-8 rounded-lg transition-colors duration-200 inline-block"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto bg-white hover:bg-gray-50 text-gray-900 font-medium py-3 px-8 rounded-lg border border-gray-300 transition-colors duration-200 inline-block"
            >
              Sign In
            </Link>
          </div>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Track Performance
            </h3>
            <p className="text-gray-600">
              Monitor your portfolio's performance with real-time updates and detailed analytics.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Manage Trades
            </h3>
            <p className="text-gray-600">
              Easily add, edit, and track all your trades across multiple portfolios.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Share & Discover
            </h3>
            <p className="text-gray-600">
              Share your public portfolios or discover successful strategies from other investors.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
