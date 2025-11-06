import React from 'react';
import {
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  UserGroupIcon,
  ChartBarIcon,
  ExclamationCircleIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

interface EditorStats {
  pendingReview: number;
  underReview: number;
  needsDecision: number;
  published: number;
  awaitingReviewers: number;
  overdueReviews: number;
  recentSubmissions: Array<{
    id: number;
    manuscriptId: string;
    title: string;
    submittedAt: string;
    status: string;
    urgency: 'low' | 'medium' | 'high';
  }>;
}

const EditorDashboard: React.FC = () => {
  const { data: stats, isLoading } = useQuery<EditorStats>(
    'editor-dashboard-stats',
    () => api.get('/editor/stats').then((res) => res.data)
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const stats_data = stats || {
    pendingReview: 0,
    underReview: 0,
    needsDecision: 0,
    published: 0,
    awaitingReviewers: 0,
    overdueReviews: 0,
    recentSubmissions: [],
  };

  const statCards = [
    {
      name: 'Pending Review',
      value: stats_data.pendingReview,
      icon: ClockIcon,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      link: '/dashboard/manuscripts?status=pending',
    },
    {
      name: 'Under Review',
      value: stats_data.underReview,
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      link: '/dashboard/manuscripts?status=under-review',
    },
    {
      name: 'Needs Decision',
      value: stats_data.needsDecision,
      icon: ExclamationCircleIcon,
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      link: '/dashboard/manuscripts?status=needs-decision',
    },
    {
      name: 'Published',
      value: stats_data.published,
      icon: CheckCircleIcon,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      link: '/dashboard/manuscripts?status=published',
    },
  ];

  const alertCards = [
    {
      name: 'Awaiting Reviewers',
      value: stats_data.awaitingReviewers,
      description: 'Manuscripts need reviewer assignment',
      icon: UserGroupIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      link: '/dashboard/manuscripts?needs=reviewers',
    },
    {
      name: 'Overdue Reviews',
      value: stats_data.overdueReviews,
      description: 'Reviews past deadline',
      icon: ExclamationCircleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      link: '/dashboard/reviews?status=overdue',
    },
  ];

  const getUrgencyBadge = (urgency: 'low' | 'medium' | 'high') => {
    const styles = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800',
    };
    return styles[urgency];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Editor Dashboard</h1>
            <p className="text-indigo-100">
              Manage submissions, assign reviewers, and make editorial decisions
            </p>
          </div>
          <div className="hidden md:block">
            <SparklesIcon className="h-16 w-16 text-indigo-200 opacity-50" />
          </div>
        </div>
      </div>

      {/* Alert Cards (if any) */}
      {(stats_data.awaitingReviewers > 0 || stats_data.overdueReviews > 0) && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {alertCards.map(
            (alert) =>
              alert.value > 0 && (
                <Link
                  key={alert.name}
                  to={alert.link}
                  className={`${alert.bgColor} rounded-lg p-6 border-2 border-transparent hover:border-indigo-500 transition-all duration-200 cursor-pointer`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center">
                        <alert.icon className={`h-6 w-6 ${alert.color} mr-2`} />
                        <p className="text-sm font-medium text-gray-900">{alert.name}</p>
                      </div>
                      <p className="mt-2 text-3xl font-bold text-gray-900">{alert.value}</p>
                      <p className="mt-1 text-xs text-gray-600">{alert.description}</p>
                    </div>
                    <ExclamationCircleIcon className={`h-12 w-12 ${alert.color} opacity-20`} />
                  </div>
                </Link>
              )
          )}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <Link
            key={stat.name}
            to={stat.link}
            className={`${stat.bgColor} rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden border-2 ${stat.borderColor} hover:border-indigo-500`}
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
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Link
            to="/dashboard/manuscripts?needs=reviewers"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all duration-200 group"
          >
            <div className="flex-shrink-0">
              <SparklesIcon className="h-8 w-8 text-purple-600 group-hover:scale-110 transition-transform duration-200" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">AI Reviewer Matching</p>
              <p className="text-xs text-gray-500">Smart reviewer suggestions</p>
            </div>
          </Link>

          <Link
            to="/dashboard/manuscripts?status=needs-decision"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all duration-200 group"
          >
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-purple-600 group-hover:scale-110 transition-transform duration-200" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">Make Decisions</p>
              <p className="text-xs text-gray-500">Review completed manuscripts</p>
            </div>
          </Link>

          <Link
            to="/dashboard/analytics"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all duration-200 group"
          >
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600 group-hover:scale-110 transition-transform duration-200" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">View Analytics</p>
              <p className="text-xs text-gray-500">Editorial insights</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Submissions */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Recent Submissions</h2>
          <Link
            to="/dashboard/manuscripts"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-800"
          >
            View all →
          </Link>
        </div>

        {stats_data.recentSubmissions.length > 0 ? (
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Manuscript ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Submitted
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats_data.recentSubmissions.map((manuscript) => (
                  <tr
                    key={manuscript.id}
                    className="hover:bg-gray-50 transition-colors duration-150"
                  >
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                      {manuscript.manuscriptId}
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-900 max-w-xs truncate">
                      {manuscript.title}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {manuscript.status}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(manuscript.submittedAt)}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getUrgencyBadge(
                          manuscript.urgency
                        )}`}
                      >
                        {manuscript.urgency}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-right text-sm">
                      <Link
                        to={`/dashboard/manuscripts/${manuscript.id}`}
                        className="text-indigo-600 hover:text-indigo-900 font-medium"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No recent submissions</h3>
            <p className="mt-1 text-sm text-gray-500">
              New manuscript submissions will appear here.
            </p>
          </div>
        )}
      </div>

      {/* Editorial Tips */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-6 border border-purple-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <SparklesIcon className="h-5 w-5 text-purple-600 mr-2" />
          AI-Powered Features
        </h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start">
            <span className="text-purple-600 mr-2">•</span>
            <span>
              <strong>Smart Reviewer Matching:</strong> Our AI analyzes manuscript content and
              suggests the most qualified reviewers based on expertise, availability, and past
              performance
            </span>
          </li>
          <li className="flex items-start">
            <span className="text-purple-600 mr-2">•</span>
            <span>
              <strong>Automated Classification:</strong> Manuscripts are automatically classified
              by subject area to streamline the assignment process
            </span>
          </li>
          <li className="flex items-start">
            <span className="text-purple-600 mr-2">•</span>
            <span>
              <strong>Plagiarism Detection:</strong> All submissions are automatically screened
              for originality using advanced similarity detection
            </span>
          </li>
          <li className="flex items-start">
            <span className="text-purple-600 mr-2">•</span>
            <span>
              <strong>Predictive Analytics:</strong> View acceptance probability and estimated
              review times for better workflow planning
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default EditorDashboard;
