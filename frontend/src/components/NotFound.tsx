import React from 'react';
import { Link } from 'react-router-dom';
import { HomeIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-lg w-full text-center">
        {/* 404 Illustration */}
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
            404
          </h1>
          <div className="relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="h-32 w-32 bg-indigo-100 rounded-full opacity-50 animate-pulse"></div>
            </div>
            <svg
              className="relative h-32 w-32 mx-auto text-indigo-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>

        {/* Message */}
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Page Not Found</h2>
        <p className="text-lg text-gray-600 mb-8">
          Sorry, we couldn't find the page you're looking for. It might have been moved or deleted.
        </p>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/"
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <HomeIcon className="h-5 w-5 mr-2" />
            Go Home
          </Link>
          <Link
            to="/search"
            className="inline-flex items-center justify-center px-6 py-3 border-2 border-indigo-600 text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50 transition-all duration-200"
          >
            <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
            Search Articles
          </Link>
        </div>

        {/* Helpful Links */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500 mb-4">You might be looking for:</p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link
              to="/articles"
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Browse Articles
            </Link>
            <span className="text-gray-300">•</span>
            <Link
              to="/dashboard"
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Dashboard
            </Link>
            <span className="text-gray-300">•</span>
            <Link
              to="/author-guidelines"
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Author Guidelines
            </Link>
            <span className="text-gray-300">•</span>
            <Link
              to="/contact"
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Contact Us
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
