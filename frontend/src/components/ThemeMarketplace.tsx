import React, { useState, useEffect } from 'react';
import {
  MagnifyingGlassIcon,
  StarIcon,
  ArrowDownTrayIcon,
  FunnelIcon,
  HeartIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import { useTheme } from '../context/ThemeContext';
import { apiService } from '../services/api';

interface Theme {
  id: number;
  theme_id: string;
  name: string;
  description: string;
  category: string;
  author: string;
  version: string;
  download_count: number;
  average_rating: number;
  rating_count: number;
  preview_image_url?: string;
  is_approved: boolean;
  created_at: string;
}

interface ThemeDetail extends Theme {
  colors: any;
  typography: any;
  border_radius: string;
}

const ThemeMarketplace: React.FC = () => {
  const { setTheme, currentTheme } = useTheme();
  const [themes, setThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'downloads' | 'rating' | 'recent'>('downloads');
  const [selectedTheme, setSelectedTheme] = useState<ThemeDetail | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  const categories = [
    { id: 'all', name: 'All Themes', icon: '🎨' },
    { id: 'academic', name: 'Academic', icon: '📚' },
    { id: 'modern', name: 'Modern', icon: '✨' },
    { id: 'medical', name: 'Medical', icon: '⚕️' },
    { id: 'nature', name: 'Nature', icon: '🌿' },
    { id: 'minimal', name: 'Minimal', icon: '⬜' },
    { id: 'humanities', name: 'Humanities', icon: '🎭' },
    { id: 'law', name: 'Law', icon: '⚖️' },
    { id: 'technology', name: 'Technology', icon: '💻' },
    { id: 'social', name: 'Social Sciences', icon: '👥' },
    { id: 'business', name: 'Business', icon: '💼' },
    { id: 'bold', name: 'Bold', icon: '🎪' },
  ];

  useEffect(() => {
    fetchThemes();
  }, [selectedCategory, sortBy, searchQuery]);

  const fetchThemes = async () => {
    try {
      setLoading(true);
      const params: any = { sort_by: sortBy };
      if (selectedCategory !== 'all') params.category = selectedCategory;
      if (searchQuery) params.search = searchQuery;

      const response = await apiService.themes.list(params);
      setThemes(response.data);
    } catch (error) {
      console.error('Failed to fetch themes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTheme = async (themeId: number) => {
    try {
      const response = await apiService.themes.download(themeId);
      const themeData = response.data;

      // Apply theme immediately
      // In production, this would integrate with ThemeContext
      console.log('Downloaded theme:', themeData);
      alert(`Theme "${themeData.name}" downloaded successfully! Apply it from your theme settings.`);
    } catch (error) {
      console.error('Failed to download theme:', error);
      alert('Failed to download theme. Please try again.');
    }
  };

  const handlePreviewTheme = async (themeId: number) => {
    try {
      const response = await apiService.themes.getDetail(themeId);
      setSelectedTheme(response.data);
      setShowPreview(true);
    } catch (error) {
      console.error('Failed to load theme details:', error);
    }
  };

  const renderStars = (rating: number, count: number) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star}>
            {star <= Math.round(rating) ? (
              <StarIconSolid className="h-4 w-4 text-yellow-400" />
            ) : (
              <StarIcon className="h-4 w-4 text-gray-300" />
            )}
          </span>
        ))}
        <span className="text-sm text-gray-600 ml-2">
          {rating.toFixed(1)} ({count})
        </span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Theme Marketplace</h1>
          <p className="text-gray-600">
            Discover and install beautiful themes created by the community
          </p>

          {/* Search and Filter Bar */}
          <div className="mt-6 flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search themes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="downloads">Most Downloaded</option>
              <option value="rating">Highest Rated</option>
              <option value="recent">Most Recent</option>
            </select>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar - Categories */}
          <div className="lg:w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow p-4 sticky top-4">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <FunnelIcon className="h-5 w-5 mr-2" />
                Categories
              </h3>
              <div className="space-y-2">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      selectedCategory === category.id
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <span className="mr-2">{category.icon}</span>
                    {category.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content - Theme Grid */}
          <div className="flex-1">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : themes.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No themes found matching your criteria.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {themes.map((theme) => (
                  <div
                    key={theme.id}
                    className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow overflow-hidden"
                  >
                    {/* Preview Image or Color Gradient */}
                    <div
                      className="h-40 bg-gradient-to-br from-indigo-500 to-purple-600"
                      style={
                        theme.preview_image_url
                          ? { backgroundImage: `url(${theme.preview_image_url})`, backgroundSize: 'cover' }
                          : undefined
                      }
                    >
                      <div className="h-full flex items-center justify-center bg-black bg-opacity-20">
                        <h3 className="text-2xl font-bold text-white">{theme.name}</h3>
                      </div>
                    </div>

                    {/* Theme Info */}
                    <div className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="text-sm text-gray-600 mb-1">
                            by <span className="font-medium">{theme.author}</span>
                          </p>
                          <p className="text-sm text-gray-500">v{theme.version}</p>
                        </div>
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded capitalize">
                          {theme.category}
                        </span>
                      </div>

                      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                        {theme.description}
                      </p>

                      {/* Rating */}
                      <div className="mb-4">{renderStars(theme.average_rating, theme.rating_count)}</div>

                      {/* Stats */}
                      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                        <div className="flex items-center">
                          <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                          {theme.download_count.toLocaleString()} downloads
                        </div>
                        {theme.is_approved && (
                          <div className="flex items-center text-green-600">
                            <CheckCircleIcon className="h-4 w-4 mr-1" />
                            Verified
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <button
                          onClick={() => handlePreviewTheme(theme.id)}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 text-sm font-medium"
                        >
                          Preview
                        </button>
                        <button
                          onClick={() => handleDownloadTheme(theme.id)}
                          className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm font-medium flex items-center justify-center"
                        >
                          <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                          Install
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && selectedTheme && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedTheme.name}</h2>
                  <p className="text-gray-600 mt-1">{selectedTheme.description}</p>
                </div>
                <button
                  onClick={() => setShowPreview(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Preview Content */}
              <div className="space-y-6">
                {/* Color Palette */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Color Palette</h3>
                  <div className="flex gap-2 flex-wrap">
                    {selectedTheme.colors.primary && Object.entries(selectedTheme.colors.primary).map(([shade, color]) => (
                      <div key={shade} className="text-center">
                        <div
                          className="w-12 h-12 rounded border border-gray-200"
                          style={{ backgroundColor: color as string }}
                          title={`${shade}: ${color}`}
                        />
                        <span className="text-xs text-gray-500">{shade}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Typography */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Typography</h3>
                  <div className="space-y-2">
                    <p style={{ fontFamily: selectedTheme.typography.fontFamily.sans.join(', ') }}>
                      Sans-serif: {selectedTheme.typography.fontFamily.sans[0]}
                    </p>
                    <p style={{ fontFamily: selectedTheme.typography.fontFamily.serif.join(', ') }}>
                      Serif: {selectedTheme.typography.fontFamily.serif[0]}
                    </p>
                  </div>
                </div>

                {/* Stats */}
                <div className="border-t pt-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-gray-900">{selectedTheme.download_count}</div>
                      <div className="text-sm text-gray-500">Downloads</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900">{selectedTheme.average_rating.toFixed(1)}</div>
                      <div className="text-sm text-gray-500">Rating</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900">{selectedTheme.rating_count}</div>
                      <div className="text-sm text-gray-500">Reviews</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900">{selectedTheme.version}</div>
                      <div className="text-sm text-gray-500">Version</div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      handleDownloadTheme(selectedTheme.id);
                      setShowPreview(false);
                    }}
                    className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                  >
                    Install Theme
                  </button>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ThemeMarketplace;
