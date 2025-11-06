import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  UserGroupIcon,
  DocumentTextIcon,
  ClockIcon,
  GlobeAltIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import { api } from '../../services/api';

interface AnalyticsData {
  overview: {
    totalSubmissions: number;
    submissionsChange: number;
    totalPublished: number;
    publishedChange: number;
    avgReviewTime: number;
    reviewTimeChange: number;
    activeReviewers: number;
    reviewersChange: number;
  };
  submissionTrend: Array<{
    month: string;
    submissions: number;
    published: number;
  }>;
  statusBreakdown: Array<{
    status: string;
    count: number;
    percentage: number;
  }>;
  topCountries: Array<{
    country: string;
    count: number;
    percentage: number;
  }>;
  subjectAreas: Array<{
    subject: string;
    count: number;
    avgReviewTime: number;
  }>;
  reviewerPerformance: {
    avgResponseTime: number;
    avgReviewTime: number;
    completionRate: number;
  };
}

const AnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('12months');

  const { data: analytics, isLoading } = useQuery<AnalyticsData>(
    ['analytics', timeRange],
    () => api.get(`/analytics?range=${timeRange}`).then((res) => res.data),
    {
      initialData: {
        overview: {
          totalSubmissions: 0,
          submissionsChange: 0,
          totalPublished: 0,
          publishedChange: 0,
          avgReviewTime: 0,
          reviewTimeChange: 0,
          activeReviewers: 0,
          reviewersChange: 0,
        },
        submissionTrend: [],
        statusBreakdown: [],
        topCountries: [],
        subjectAreas: [],
        reviewerPerformance: {
          avgResponseTime: 0,
          avgReviewTime: 0,
          completionRate: 0,
        },
      },
    }
  );

  const statCards = [
    {
      name: 'Total Submissions',
      value: analytics?.overview.totalSubmissions || 0,
      change: analytics?.overview.submissionsChange || 0,
      icon: DocumentTextIcon,
      color: 'blue',
    },
    {
      name: 'Published Articles',
      value: analytics?.overview.totalPublished || 0,
      change: analytics?.overview.publishedChange || 0,
      icon: ChartBarIcon,
      color: 'green',
    },
    {
      name: 'Avg. Review Time',
      value: `${analytics?.overview.avgReviewTime || 0}d`,
      change: analytics?.overview.reviewTimeChange || 0,
      icon: ClockIcon,
      color: 'purple',
      reverseChange: true,
    },
    {
      name: 'Active Reviewers',
      value: analytics?.overview.activeReviewers || 0,
      change: analytics?.overview.reviewersChange || 0,
      icon: UserGroupIcon,
      color: 'indigo',
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, { bg: string; text: string; border: string }> = {
      blue: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
      green: { bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-200' },
      purple: { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200' },
      indigo: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
    };
    return colors[color] || colors.blue;
  };

  const formatChange = (change: number, reverse: boolean = false) => {
    const isPositive = reverse ? change < 0 : change > 0;
    const Icon = isPositive ? ArrowTrendingUpIcon : ArrowTrendingDownIcon;
    const colorClass = isPositive ? 'text-green-600' : 'text-red-600';

    return (
      <div className={`flex items-center text-sm ${colorClass}`}>
        <Icon className="h-4 w-4 mr-1" />
        <span>{Math.abs(change)}%</span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
            <p className="text-indigo-100">
              Comprehensive insights into journal performance and trends
            </p>
          </div>
          <ChartBarIcon className="h-16 w-16 text-indigo-200 opacity-50 hidden md:block" />
        </div>

        {/* Time Range Selector */}
        <div className="mt-6 flex items-center space-x-2">
          <span className="text-sm text-indigo-100">Time Range:</span>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-1.5 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-md text-sm text-white focus:outline-none focus:ring-2 focus:ring-white"
          >
            <option value="3months" className="text-gray-900">Last 3 Months</option>
            <option value="6months" className="text-gray-900">Last 6 Months</option>
            <option value="12months" className="text-gray-900">Last 12 Months</option>
            <option value="all" className="text-gray-900">All Time</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const colors = getColorClasses(stat.color);
          return (
            <div
              key={stat.name}
              className={`${colors.bg} border-2 ${colors.border} rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow duration-200`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 ${colors.bg} rounded-lg border ${colors.border}`}>
                  <stat.icon className={`h-6 w-6 ${colors.text}`} />
                </div>
                {stat.change !== 0 && formatChange(stat.change, stat.reverseChange)}
              </div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-sm text-gray-600 mt-1">{stat.name}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Submission Trend */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Submission Trend</h3>
          <div className="space-y-3">
            {analytics?.submissionTrend.slice(-6).map((item) => (
              <div key={item.month} className="flex items-center">
                <div className="w-20 text-sm text-gray-600">{item.month}</div>
                <div className="flex-1 flex items-center space-x-2">
                  <div className="flex-1 h-8 bg-gray-100 rounded-md overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-md flex items-center justify-end pr-2 text-white text-xs font-medium"
                      style={{
                        width: `${Math.min((item.submissions / Math.max(...analytics.submissionTrend.map(d => d.submissions))) * 100, 100)}%`,
                      }}
                    >
                      {item.submissions > 0 && item.submissions}
                    </div>
                  </div>
                  <div className="w-16 text-sm text-gray-900 font-medium">
                    {item.submissions} sub
                  </div>
                  <div className="w-16 text-sm text-green-600 font-medium">
                    {item.published} pub
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Status Breakdown */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Manuscript Status</h3>
          <div className="space-y-3">
            {analytics?.statusBreakdown.map((item) => {
              const statusColors: Record<string, string> = {
                submitted: 'bg-blue-500',
                'under-review': 'bg-yellow-500',
                'needs-revision': 'bg-orange-500',
                accepted: 'bg-green-500',
                published: 'bg-indigo-500',
                rejected: 'bg-red-500',
              };
              return (
                <div key={item.status} className="flex items-center">
                  <div className="w-32 text-sm text-gray-700 capitalize">
                    {item.status.replace('-', ' ')}
                  </div>
                  <div className="flex-1 flex items-center space-x-3">
                    <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${statusColors[item.status] || 'bg-gray-400'} rounded-full`}
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                    <div className="w-16 text-sm text-gray-900 font-medium text-right">
                      {item.count} ({item.percentage}%)
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Geographic Distribution & Subject Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Countries */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <GlobeAltIcon className="h-6 w-6 text-indigo-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Top Contributing Countries</h3>
          </div>
          <div className="space-y-3">
            {analytics?.topCountries.slice(0, 8).map((item, index) => (
              <div key={item.country} className="flex items-center">
                <div className="w-8 text-center">
                  <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-100 text-indigo-600 text-xs font-medium">
                    {index + 1}
                  </span>
                </div>
                <div className="flex-1 ml-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">{item.country}</span>
                    <span className="text-sm text-gray-600">{item.count} manuscripts</span>
                  </div>
                  <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Subject Areas */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <FunnelIcon className="h-6 w-6 text-indigo-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Top Subject Areas</h3>
          </div>
          <div className="space-y-4">
            {analytics?.subjectAreas.slice(0, 6).map((item) => (
              <div key={item.subject} className="border-l-4 border-indigo-500 pl-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900">{item.subject}</span>
                  <span className="text-xs text-gray-500">{item.count} manuscripts</span>
                </div>
                <div className="flex items-center text-xs text-gray-600">
                  <ClockIcon className="h-3 w-3 mr-1" />
                  Avg. review: {item.avgReviewTime} days
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Reviewer Performance */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center mb-6">
          <UserGroupIcon className="h-6 w-6 text-indigo-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Reviewer Performance Metrics</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <div className="text-4xl font-bold text-indigo-600 mb-2">
              {analytics?.reviewerPerformance.avgResponseTime || 0}d
            </div>
            <div className="text-sm text-gray-600">Avg. Response Time</div>
            <p className="text-xs text-gray-500 mt-2">
              Time from invitation to acceptance
            </p>
          </div>
          <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-200">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {analytics?.reviewerPerformance.avgReviewTime || 0}d
            </div>
            <div className="text-sm text-gray-600">Avg. Review Time</div>
            <p className="text-xs text-gray-500 mt-2">
              Time from acceptance to completion
            </p>
          </div>
          <div className="text-center p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {analytics?.reviewerPerformance.completionRate || 0}%
            </div>
            <div className="text-sm text-gray-600">Completion Rate</div>
            <p className="text-xs text-gray-500 mt-2">
              Reviews completed vs. accepted
            </p>
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Export this data for further analysis
          </div>
          <div className="flex items-center space-x-3">
            <button className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors duration-200">
              Export as CSV
            </button>
            <button className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors duration-200">
              Export as PDF
            </button>
            <button className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors duration-200">
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
