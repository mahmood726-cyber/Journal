import React from 'react';
import {
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

interface DashboardStats {
  totalManuscripts: number;
  underReview: number;
  accepted: number;
  rejected: number;
  recentActivity: Array<{
    id: number;
    type: string;
    message: string;
    date: string;
  }>;
}

const AuthorDashboard: React.FC = () => {
  const { data: stats, isLoading } = useQuery<DashboardStats>(
    'dashboard-stats',
    () => api.get('/manuscripts/stats').then((res) => res.data)
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const stats_data = stats || {
    totalManuscripts: 0,
    underReview: 0,
    accepted: 0,
    rejected: 0,
    recentActivity: [],
  };

  const statCards = [
    {
      name: 'Total Manuscripts',
      value: stats_data.totalManuscripts,
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Under Review',
      value: stats_data.underReview,
      icon: ClockIcon,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Accepted',
      value: stats_data.accepted,
      icon: CheckCircleIcon,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Rejected',
      value: stats_data.rejected,
      icon: XCircleIcon,
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome Back!</h1>
        <p className="text-indigo-100 mb-6">
          Manage your manuscripts, track reviews, and publish your research.
        </p>
        <Link
          to="/dashboard/manuscripts/submit"
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-white hover:bg-indigo-50 transition-colors duration-200"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Submit New Manuscript
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div
            key={stat.name}
            className={`${stat.bgColor} rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden`}
          >
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`${stat.color} rounded-full p-3`}>
                  <stat.icon className="h-8 w-8 text-white" />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Link
            to="/dashboard/manuscripts/submit"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all duration-200 group"
          >
            <div className="flex-shrink-0">
              <PlusIcon className="h-8 w-8 text-indigo-600 group-hover:scale-110 transition-transform duration-200" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">New Submission</p>
              <p className="text-xs text-gray-500">Submit a manuscript</p>
            </div>
          </Link>

          <Link
            to="/dashboard/manuscripts"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all duration-200 group"
          >
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-8 w-8 text-indigo-600 group-hover:scale-110 transition-transform duration-200" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">My Manuscripts</p>
              <p className="text-xs text-gray-500">View all submissions</p>
            </div>
          </Link>

          <Link
            to="/dashboard/reviews"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all duration-200 group"
          >
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-indigo-600 group-hover:scale-110 transition-transform duration-200" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">My Reviews</p>
              <p className="text-xs text-gray-500">Review requests</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
        {stats_data.recentActivity.length > 0 ? (
          <div className="flow-root">
            <ul className="-mb-8">
              {stats_data.recentActivity.map((activity, idx) => (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {idx !== stats_data.recentActivity.length - 1 && (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    )}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center ring-8 ring-white">
                          <DocumentTextIcon className="h-5 w-5 text-white" />
                        </span>
                      </div>
                      <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                        <div>
                          <p className="text-sm text-gray-900">{activity.message}</p>
                        </div>
                        <div className="whitespace-nowrap text-right text-sm text-gray-500">
                          {activity.date}
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No activity yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by submitting your first manuscript.
            </p>
            <div className="mt-6">
              <Link
                to="/dashboard/manuscripts/submit"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Submit Manuscript
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Helpful Tips */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">💡 Helpful Tips</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start">
            <span className="text-indigo-600 mr-2">•</span>
            <span>
              Ensure your manuscript follows our{' '}
              <a href="/author-guidelines" className="text-indigo-600 hover:text-indigo-800 underline">
                author guidelines
              </a>{' '}
              for faster processing
            </span>
          </li>
          <li className="flex items-start">
            <span className="text-indigo-600 mr-2">•</span>
            <span>Include all co-authors with their ORCID iDs for better discoverability</span>
          </li>
          <li className="flex items-start">
            <span className="text-indigo-600 mr-2">•</span>
            <span>Upload high-quality figures in the recommended formats (PDF, PNG, TIFF)</span>
          </li>
          <li className="flex items-start">
            <span className="text-indigo-600 mr-2">•</span>
            <span>
              Average review time is 21 days - you'll receive email notifications for all updates
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default AuthorDashboard;
