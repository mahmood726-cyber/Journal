import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const PublicLayout: React.FC = () => {
  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Articles', href: '/articles' },
    { name: 'About', href: '/about' },
    { name: 'For Authors', href: '/author-guidelines' },
    { name: 'Contact', href: '/contact' },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center">
              <div className="h-10 w-10 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-xl font-bold text-white">J</span>
              </div>
              <span className="ml-3 text-xl font-bold text-gray-900">Diamond OA Journal</span>
            </Link>

            {/* Desktop navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-gray-700 hover:text-indigo-600 font-medium transition-colors duration-150"
                >
                  {item.name}
                </Link>
              ))}
            </div>

            {/* Right side buttons */}
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-500">
                <MagnifyingGlassIcon className="h-5 w-5" />
              </button>
              <Link
                to="/login"
                className="text-gray-700 hover:text-indigo-600 font-medium transition-colors duration-150"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700 transition-colors duration-150"
              >
                Get Started
              </Link>
            </div>
          </div>
        </nav>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">About</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="/about" className="hover:text-white">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link to="/editorial-board" className="hover:text-white">
                    Editorial Board
                  </Link>
                </li>
                <li>
                  <Link to="/policies" className="hover:text-white">
                    Policies
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">For Authors</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="/author-guidelines" className="hover:text-white">
                    Author Guidelines
                  </Link>
                </li>
                <li>
                  <Link to="/submission-process" className="hover:text-white">
                    Submission Process
                  </Link>
                </li>
                <li>
                  <Link to="/faq" className="hover:text-white">
                    FAQ
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="/articles" className="hover:text-white">
                    Browse Articles
                  </Link>
                </li>
                <li>
                  <Link to="/search" className="hover:text-white">
                    Search
                  </Link>
                </li>
                <li>
                  <Link to="/indexing" className="hover:text-white">
                    Indexing
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="/contact" className="hover:text-white">
                    Contact Us
                  </Link>
                </li>
                <li>
                  <a href="mailto:info@journal.org" className="hover:text-white">
                    info@journal.org
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-800 text-center text-gray-400">
            <p>&copy; 2025 Diamond Open Access Journal. All content is CC BY 4.0 licensed.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PublicLayout;
