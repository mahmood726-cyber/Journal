import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  DocumentTextIcon,
  SparklesIcon,
  UserGroupIcon,
  GlobeAltIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  LightBulbIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { api } from '../../services/api';

interface FeaturedArticle {
  id: number;
  manuscriptId: string;
  title: string;
  abstract: string;
  authors: string;
  publishedAt: string;
  views: number;
}

interface JournalStats {
  totalArticles: number;
  totalAuthors: number;
  countries: number;
  avgReviewTime: number;
}

const Home: React.FC = () => {
  const { data: featuredArticles } = useQuery<FeaturedArticle[]>(
    'featured-articles',
    () => api.get('/articles/featured').then((res) => res.data),
    { initialData: [] }
  );

  const { data: stats } = useQuery<JournalStats>(
    'journal-stats',
    () => api.get('/stats').then((res) => res.data),
    {
      initialData: {
        totalArticles: 0,
        totalAuthors: 0,
        countries: 0,
        avgReviewTime: 21,
      },
    }
  );

  const features = [
    {
      icon: SparklesIcon,
      title: 'Diamond Open Access',
      description:
        'No fees for authors or readers. Free to publish, free to read. We believe knowledge should be accessible to all.',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      icon: GlobeAltIcon,
      title: 'Global Reach',
      description:
        'Indexed in PubMed, Scopus, and Web of Science. Your research reaches the widest possible audience.',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      icon: UserGroupIcon,
      title: 'Rigorous Peer Review',
      description:
        'Expert reviewers selected using AI-powered matching ensure high-quality, constructive feedback.',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      icon: LightBulbIcon,
      title: 'Fast Publication',
      description:
        'Average review time of 21 days. Published articles appear immediately with full DOI registration.',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
  ];

  const benefits = [
    'No Article Processing Charges (APCs)',
    'Fast peer review (average 21 days)',
    'Indexed in major databases',
    'Creative Commons CC BY 4.0 license',
    'Full DOI registration',
    'ORCID integration',
    'Comprehensive citation metrics',
    'Video abstract support',
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-indigo-600 to-purple-700 text-white overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-700 mix-blend-multiply" />
          <div className="absolute inset-0 opacity-20">
            <svg className="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2" width="800" height="800" viewBox="0 0 800 800">
              <circle cx="400" cy="400" r="400" fill="white" opacity="0.1" />
            </svg>
            <svg className="absolute bottom-0 left-0 transform -translate-x-1/2 translate-y-1/2" width="600" height="600" viewBox="0 0 600 600">
              <circle cx="300" cy="300" r="300" fill="white" opacity="0.1" />
            </svg>
          </div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-extrabold mb-6 leading-tight">
              Diamond Open Access
              <br />
              <span className="text-indigo-200">Academic Publishing</span>
            </h1>
            <p className="text-xl md:text-2xl text-indigo-100 mb-8 max-w-3xl mx-auto">
              Publish your research with no fees. Free for authors, free for readers.
              Peer-reviewed excellence meets modern technology.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard/manuscripts/submit"
                className="inline-flex items-center justify-center px-8 py-4 border border-transparent text-lg font-medium rounded-md text-indigo-700 bg-white hover:bg-indigo-50 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Submit Your Manuscript
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Link>
              <Link
                to="/articles"
                className="inline-flex items-center justify-center px-8 py-4 border-2 border-white text-lg font-medium rounded-md text-white hover:bg-white hover:text-indigo-700 transition-all duration-200"
              >
                Browse Articles
              </Link>
            </div>
          </div>
        </div>

        {/* Wave Separator */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="white"/>
          </svg>
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold text-indigo-600">{stats?.totalArticles || 0}+</div>
            <div className="text-sm text-gray-600 mt-2">Published Articles</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-indigo-600">{stats?.totalAuthors || 0}+</div>
            <div className="text-sm text-gray-600 mt-2">Contributing Authors</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-indigo-600">{stats?.countries || 0}+</div>
            <div className="text-sm text-gray-600 mt-2">Countries</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-indigo-600">{stats?.avgReviewTime || 21}</div>
            <div className="text-sm text-gray-600 mt-2">Avg. Review Days</div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Why Publish With Us?</h2>
            <p className="text-xl text-gray-600">
              World-class publishing infrastructure powered by advanced technology
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-shadow duration-200 border-2 border-gray-100 hover:border-indigo-500"
              >
                <div className={`${feature.bgColor} rounded-full p-3 w-fit mb-4`}>
                  <feature.icon className={`h-8 w-8 ${feature.color}`} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Articles */}
      {featuredArticles && featuredArticles.length > 0 && (
        <div className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-12">
              <div>
                <h2 className="text-4xl font-bold text-gray-900 mb-2">Featured Articles</h2>
                <p className="text-xl text-gray-600">Latest research from our community</p>
              </div>
              <Link
                to="/articles"
                className="text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
              >
                View all articles
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {featuredArticles.slice(0, 3).map((article) => (
                <Link
                  key={article.id}
                  to={`/article/${article.manuscriptId}`}
                  className="bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-200 overflow-hidden border border-gray-200 hover:border-indigo-500"
                >
                  <div className="p-6">
                    <div className="flex items-center text-sm text-gray-500 mb-3">
                      <DocumentTextIcon className="h-4 w-4 mr-1" />
                      {new Date(article.publishedAt).toLocaleDateString()}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                      {article.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-3">{article.abstract}</p>
                    <div className="text-xs text-gray-500 mb-4">{article.authors}</div>
                    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                      <span className="text-xs text-gray-500">{article.views} views</span>
                      <span className="text-indigo-600 font-medium text-sm flex items-center">
                        Read more
                        <ArrowRightIcon className="ml-1 h-4 w-4" />
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Benefits Section */}
      <div className="bg-indigo-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Everything You Need to Publish Great Research
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Our platform provides a comprehensive suite of tools and services to ensure your
                research reaches its full potential.
              </p>
              <ul className="space-y-4">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link
                  to="/author-guidelines"
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors duration-200"
                >
                  View Author Guidelines
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </Link>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-xl p-8 border-2 border-indigo-200">
              <div className="flex items-center mb-6">
                <ChartBarIcon className="h-8 w-8 text-indigo-600 mr-3" />
                <h3 className="text-2xl font-bold text-gray-900">Submission Process</h3>
              </div>
              <div className="space-y-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-100 text-indigo-600 font-bold">
                      1
                    </div>
                  </div>
                  <div className="ml-4">
                    <h4 className="text-lg font-semibold text-gray-900">Submit Manuscript</h4>
                    <p className="text-sm text-gray-600">
                      Easy online submission with guided wizard
                    </p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-100 text-indigo-600 font-bold">
                      2
                    </div>
                  </div>
                  <div className="ml-4">
                    <h4 className="text-lg font-semibold text-gray-900">Editorial Review</h4>
                    <p className="text-sm text-gray-600">
                      Initial screening within 3-5 business days
                    </p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-100 text-indigo-600 font-bold">
                      3
                    </div>
                  </div>
                  <div className="ml-4">
                    <h4 className="text-lg font-semibold text-gray-900">Peer Review</h4>
                    <p className="text-sm text-gray-600">
                      Expert reviewers provide feedback (avg. 21 days)
                    </p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-100 text-indigo-600 font-bold">
                      4
                    </div>
                  </div>
                  <div className="ml-4">
                    <h4 className="text-lg font-semibold text-gray-900">Publication</h4>
                    <p className="text-sm text-gray-600">
                      Immediate online publication with DOI
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Share Your Research?</h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Join thousands of researchers publishing their work in our diamond open access journal.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-md text-indigo-700 bg-white hover:bg-indigo-50 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Create Free Account
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">About</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/about" className="hover:text-white">About Us</Link></li>
                <li><Link to="/editorial-board" className="hover:text-white">Editorial Board</Link></li>
                <li><Link to="/policies" className="hover:text-white">Policies</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">For Authors</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/author-guidelines" className="hover:text-white">Author Guidelines</Link></li>
                <li><Link to="/submission-fees" className="hover:text-white">Submission Fees</Link></li>
                <li><Link to="/faq" className="hover:text-white">FAQ</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/articles" className="hover:text-white">Browse Articles</Link></li>
                <li><Link to="/search" className="hover:text-white">Search</Link></li>
                <li><Link to="/indexing" className="hover:text-white">Indexing</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/contact" className="hover:text-white">Contact Us</Link></li>
                <li><a href="mailto:info@journal.org" className="hover:text-white">info@journal.org</a></li>
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

export default Home;
