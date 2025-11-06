/**
 * Analytics Dashboard
 *
 * Comprehensive analytics and insights:
 * - Real-time metrics
 * - Article performance
 * - User behavior
 * - Geographic distribution
 * - Traffic sources
 * - Conversion funnels
 * - Custom reports
 */
import React, { useState, useEffect } from 'react';
import {
  TrendingUp, Users, Eye, Download, Globe, Share2,
  Clock, Target, BarChart3, PieChart, Activity,
  Calendar, Filter, RefreshCw, Download as DownloadIcon,
  ChevronUp, ChevronDown, MapPin, Search, ArrowUpRight
} from 'lucide-react';

interface AnalyticsData {
  overview: OverviewMetrics;
  articles: ArticleMetrics[];
  users: UserMetrics;
  traffic: TrafficData;
  geography: GeographyData;
  trends: TrendData[];
}

interface OverviewMetrics {
  totalViews: number;
  uniqueVisitors: number;
  downloads: number;
  avgTimeOnSite: number;
  bounceRate: number;
  conversionRate: number;
  viewsChange: number;
  visitorsChange: number;
  downloadsChange: number;
}

interface ArticleMetrics {
  id: string;
  title: string;
  views: number;
  downloads: number;
  shares: number;
  avgReadTime: number;
  completionRate: number;
  citationCount: number;
  publishedDate: string;
  viewsTrend: number;
}

interface UserMetrics {
  totalUsers: number;
  activeUsers: number;
  newUsers: number;
  returningUsers: number;
  averageSessionDuration: number;
  pagesPerSession: number;
  deviceBreakdown: DeviceBreakdown;
  userRetention: RetentionData;
}

interface DeviceBreakdown {
  desktop: number;
  mobile: number;
  tablet: number;
}

interface RetentionData {
  day1: number;
  day7: number;
  day30: number;
}

interface TrafficData {
  sources: TrafficSource[];
  referrers: Referrer[];
  keywords: SearchKeyword[];
}

interface TrafficSource {
  name: string;
  visitors: number;
  percentage: number;
  color: string;
}

interface Referrer {
  domain: string;
  visits: number;
  percentage: number;
}

interface SearchKeyword {
  keyword: string;
  searches: number;
  clickThroughRate: number;
}

interface GeographyData {
  countries: CountryData[];
  cities: CityData[];
}

interface CountryData {
  country: string;
  visitors: number;
  percentage: number;
  avgTimeOnSite: number;
}

interface CityData {
  city: string;
  country: string;
  visitors: number;
}

interface TrendData {
  date: string;
  views: number;
  visitors: number;
  downloads: number;
}

const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState<'views' | 'visitors' | 'downloads'>('views');

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/analytics/dashboard?range=${dateRange}`);
      const analyticsData = await response.json();
      setData(analyticsData);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="w-12 h-12 text-indigo-600 animate-pulse mx-auto mb-4" />
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">Real-time insights and performance metrics</p>
        </div>
        <div className="flex items-center space-x-3">
          {/* Date Range Selector */}
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>

          <button
            onClick={loadAnalytics}
            className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-5 h-5 text-gray-600" />
          </button>

          <button className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium">
            <DownloadIcon className="w-4 h-4" />
            <span>Export Report</span>
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          icon={<Eye className="w-6 h-6" />}
          label="Total Views"
          value={data.overview.totalViews.toLocaleString()}
          change={data.overview.viewsChange}
          color="from-blue-500 to-blue-600"
        />
        <MetricCard
          icon={<Users className="w-6 h-6" />}
          label="Unique Visitors"
          value={data.overview.uniqueVisitors.toLocaleString()}
          change={data.overview.visitorsChange}
          color="from-purple-500 to-purple-600"
        />
        <MetricCard
          icon={<Download className="w-6 h-6" />}
          label="Downloads"
          value={data.overview.downloads.toLocaleString()}
          change={data.overview.downloadsChange}
          color="from-green-500 to-green-600"
        />
        <MetricCard
          icon={<Clock className="w-6 h-6" />}
          label="Avg. Time on Site"
          value={formatDuration(data.overview.avgTimeOnSite)}
          change={0}
          color="from-indigo-500 to-indigo-600"
        />
      </div>

      {/* Trends Chart */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Trends</h2>
          <div className="flex items-center space-x-2">
            {(['views', 'visitors', 'downloads'] as const).map((metric) => (
              <button
                key={metric}
                onClick={() => setSelectedMetric(metric)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedMetric === metric
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {metric.charAt(0).toUpperCase() + metric.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <TrendsChart data={data.trends} metric={selectedMetric} />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Traffic Sources */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Target className="w-5 h-5 mr-2 text-indigo-600" />
            Traffic Sources
          </h2>
          <div className="space-y-4">
            {data.traffic.sources.map((source) => (
              <div key={source.name} className="flex items-center space-x-4">
                <div className="w-24 font-medium text-gray-700">{source.name}</div>
                <div className="flex-1 h-8 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r ${source.color} rounded-full flex items-center justify-end pr-2 text-white text-sm font-medium transition-all duration-500`}
                    style={{ width: `${source.percentage}%` }}
                  >
                    {source.percentage > 10 && `${source.percentage}%`}
                  </div>
                </div>
                <div className="w-20 text-right text-gray-600">
                  {source.visitors.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Device Breakdown */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-indigo-600" />
            Device Breakdown
          </h2>
          <div className="flex items-center justify-center mb-6">
            <DevicePieChart breakdown={data.users.deviceBreakdown} />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {data.users.deviceBreakdown.desktop}%
              </div>
              <div className="text-sm text-gray-600">Desktop</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {data.users.deviceBreakdown.mobile}%
              </div>
              <div className="text-sm text-gray-600">Mobile</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {data.users.deviceBreakdown.tablet}%
              </div>
              <div className="text-sm text-gray-600">Tablet</div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Articles */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" />
          Top Performing Articles
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Article</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Views</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Downloads</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Shares</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Avg. Read Time</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Completion</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Trend</th>
              </tr>
            </thead>
            <tbody>
              {data.articles.map((article, idx) => (
                <tr key={article.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-4">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                        {idx + 1}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900 line-clamp-1">
                          {article.title}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Published {new Date(article.publishedDate).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="text-center py-4 px-4 font-medium text-gray-900">
                    {article.views.toLocaleString()}
                  </td>
                  <td className="text-center py-4 px-4 text-gray-600">
                    {article.downloads.toLocaleString()}
                  </td>
                  <td className="text-center py-4 px-4 text-gray-600">
                    {article.shares.toLocaleString()}
                  </td>
                  <td className="text-center py-4 px-4 text-gray-600">
                    {formatDuration(article.avgReadTime)}
                  </td>
                  <td className="text-center py-4 px-4">
                    <div className="flex items-center justify-center">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full"
                          style={{ width: `${article.completionRate}%` }}
                        />
                      </div>
                      <span className="ml-2 text-sm text-gray-600">
                        {article.completionRate}%
                      </span>
                    </div>
                  </td>
                  <td className="text-center py-4 px-4">
                    <div className={`flex items-center justify-center ${
                      article.viewsTrend > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {article.viewsTrend > 0 ? (
                        <ChevronUp className="w-4 h-4 mr-1" />
                      ) : (
                        <ChevronDown className="w-4 h-4 mr-1" />
                      )}
                      <span className="text-sm font-medium">
                        {Math.abs(article.viewsTrend)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Geographic Distribution */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <Globe className="w-5 h-5 mr-2 text-indigo-600" />
          Geographic Distribution
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Countries */}
          <div>
            <h3 className="font-semibold text-gray-700 mb-4">Top Countries</h3>
            <div className="space-y-3">
              {data.geography.countries.slice(0, 5).map((country, idx) => (
                <div key={country.country} className="flex items-center space-x-3">
                  <div className="w-6 text-sm text-gray-500">{idx + 1}</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900">{country.country}</span>
                      <span className="text-sm text-gray-600">
                        {country.visitors.toLocaleString()}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                        style={{ width: `${country.percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Cities */}
          <div>
            <h3 className="font-semibold text-gray-700 mb-4">Top Cities</h3>
            <div className="space-y-3">
              {data.geography.cities.slice(0, 5).map((city, idx) => (
                <div key={city.city} className="flex items-center justify-between py-2 border-b border-gray-100">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 text-sm text-gray-500">{idx + 1}</div>
                    <div>
                      <div className="font-medium text-gray-900">{city.city}</div>
                      <div className="text-xs text-gray-500">{city.country}</div>
                    </div>
                  </div>
                  <div className="text-sm font-medium text-gray-900">
                    {city.visitors.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Metric Card Component
 */
const MetricCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string;
  change: number;
  color: string;
}> = ({ icon, label, value, change }) => {
  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center text-white`}>
          {icon}
        </div>
        {change !== 0 && (
          <div className={`flex items-center text-sm font-medium ${
            change > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {change > 0 ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ChevronDown className="w-4 h-4 mr-1" />}
            {Math.abs(change)}%
          </div>
        )}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );
};

/**
 * Trends Chart Component (Simplified)
 */
const TrendsChart: React.FC<{
  data: TrendData[];
  metric: 'views' | 'visitors' | 'downloads';
}> = ({ data, metric }) => {
  const maxValue = Math.max(...data.map((d) => d[metric]));

  return (
    <div className="h-64 flex items-end space-x-2">
      {data.map((point, idx) => {
        const height = (point[metric] / maxValue) * 100;
        return (
          <div key={idx} className="flex-1 flex flex-col items-center group">
            <div
              className="w-full bg-gradient-to-t from-indigo-600 to-purple-600 rounded-t-lg transition-all duration-300 group-hover:from-indigo-700 group-hover:to-purple-700 relative"
              style={{ height: `${height}%` }}
            >
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                {point[metric].toLocaleString()}
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/**
 * Device Pie Chart Component (Simplified)
 */
const DevicePieChart: React.FC<{ breakdown: DeviceBreakdown }> = ({ breakdown }) => {
  const total = breakdown.desktop + breakdown.mobile + breakdown.tablet;
  const desktopAngle = (breakdown.desktop / total) * 360;
  const mobileAngle = (breakdown.mobile / total) * 360;

  return (
    <svg width="200" height="200" viewBox="0 0 200 200">
      {/* Desktop slice */}
      <path
        d={`M 100 100 L 100 0 A 100 100 0 ${desktopAngle > 180 ? 1 : 0} 1 ${
          100 + 100 * Math.sin((desktopAngle * Math.PI) / 180)
        } ${100 - 100 * Math.cos((desktopAngle * Math.PI) / 180)} Z`}
        fill="url(#desktopGradient)"
      />
      {/* Mobile slice */}
      <path
        d={`M 100 100 L ${
          100 + 100 * Math.sin((desktopAngle * Math.PI) / 180)
        } ${
          100 - 100 * Math.cos((desktopAngle * Math.PI) / 180)
        } A 100 100 0 ${mobileAngle > 180 ? 1 : 0} 1 ${
          100 + 100 * Math.sin(((desktopAngle + mobileAngle) * Math.PI) / 180)
        } ${
          100 - 100 * Math.cos(((desktopAngle + mobileAngle) * Math.PI) / 180)
        } Z`}
        fill="url(#mobileGradient)"
      />
      {/* Tablet slice */}
      <path
        d={`M 100 100 L ${
          100 + 100 * Math.sin(((desktopAngle + mobileAngle) * Math.PI) / 180)
        } ${
          100 - 100 * Math.cos(((desktopAngle + mobileAngle) * Math.PI) / 180)
        } A 100 100 0 0 1 100 0 Z`}
        fill="url(#tabletGradient)"
      />
      <defs>
        <linearGradient id="desktopGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#8b5cf6" />
        </linearGradient>
        <linearGradient id="mobileGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#8b5cf6" />
          <stop offset="100%" stopColor="#a855f7" />
        </linearGradient>
        <linearGradient id="tabletGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#a855f7" />
          <stop offset="100%" stopColor="#c084fc" />
        </linearGradient>
      </defs>
    </svg>
  );
};

/**
 * Utility functions
 */
function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export default AnalyticsDashboard;
