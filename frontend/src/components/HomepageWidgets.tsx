/**
 * Homepage Widgets
 *
 * Modular widgets for journal homepage:
 * - Journal stats
 * - Announcements
 * - Trending articles
 * - Popular topics
 * - Recent articles
 * - Upcoming events
 * - Quick actions
 */
import React, { useState } from 'react';
import {
  TrendingUp, Users, FileText, Eye, Download, Clock,
  Calendar, Award, MessageSquare, ExternalLink, ChevronRight,
  Bell, Sparkles, ArrowUp, Target, Zap, BookOpen
} from 'lucide-react';
import { Link } from 'react-router-dom';

/**
 * Journal Statistics Widget
 */
export const JournalStatsWidget: React.FC = () => {
  const stats = [
    {
      icon: <FileText className="w-6 h-6" />,
      value: '1,234',
      label: 'Published Articles',
      trend: '+12%',
      trendUp: true,
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: <Eye className="w-6 h-6" />,
      value: '2.4M',
      label: 'Total Views',
      trend: '+28%',
      trendUp: true,
      color: 'from-indigo-500 to-indigo-600',
    },
    {
      icon: <Download className="w-6 h-6" />,
      value: '856K',
      label: 'Downloads',
      trend: '+18%',
      trendUp: true,
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: <Users className="w-6 h-6" />,
      value: '450',
      label: 'Expert Reviewers',
      trend: '+5%',
      trendUp: true,
      color: 'from-pink-500 to-pink-600',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Journal Impact</h2>
        <Link
          to="/metrics"
          className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
        >
          View Details
          <ExternalLink className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            className="relative overflow-hidden rounded-lg bg-gradient-to-br p-[1px] group hover:scale-105 transition-transform duration-200"
            style={{
              backgroundImage: `linear-gradient(to bottom right, var(--tw-gradient-stops))`,
            }}
          >
            <div className="bg-white rounded-lg p-4 h-full">
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center text-white mb-3`}>
                {stat.icon}
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-1">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600 mb-2">{stat.label}</div>
              <div className={`flex items-center text-xs font-medium ${stat.trendUp ? 'text-green-600' : 'text-red-600'}`}>
                <ArrowUp className={`w-3 h-3 mr-1 ${stat.trendUp ? '' : 'rotate-180'}`} />
                {stat.trend} this month
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Announcements Widget
 */
export const AnnouncementsWidget: React.FC = () => {
  const announcements = [
    {
      id: 1,
      type: 'important',
      title: 'Special Issue: AI in Healthcare',
      description: 'Submit your research on artificial intelligence applications in medical science.',
      date: '2024-03-15',
      deadline: '2024-06-30',
      link: '/special-issues/ai-healthcare',
    },
    {
      id: 2,
      type: 'update',
      title: 'New Submission Guidelines',
      description: 'Updated author guidelines now include data availability statements.',
      date: '2024-03-10',
      link: '/guidelines',
    },
    {
      id: 3,
      type: 'event',
      title: 'Editorial Board Meeting',
      description: 'Annual meeting to discuss journal direction and policies.',
      date: '2024-04-05',
      link: '/events/editorial-meeting-2024',
    },
  ];

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'important':
        return 'bg-red-100 text-red-600 border-red-200';
      case 'update':
        return 'bg-blue-100 text-blue-600 border-blue-200';
      case 'event':
        return 'bg-purple-100 text-purple-600 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-500 rounded-lg flex items-center justify-center">
            <Bell className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Announcements</h2>
        </div>
        <Link
          to="/announcements"
          className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
        >
          View All
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {announcements.map((announcement) => (
          <Link
            key={announcement.id}
            to={announcement.link}
            className="block p-4 border border-gray-200 rounded-lg hover:border-indigo-300 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-start justify-between mb-2">
              <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${getTypeColor(announcement.type)}`}>
                {announcement.type.charAt(0).toUpperCase() + announcement.type.slice(1)}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(announcement.date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">{announcement.title}</h3>
            <p className="text-sm text-gray-600">{announcement.description}</p>
            {announcement.deadline && (
              <div className="mt-2 flex items-center text-xs text-gray-500">
                <Clock className="w-3 h-3 mr-1" />
                Deadline: {new Date(announcement.deadline).toLocaleDateString()}
              </div>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
};

/**
 * Trending Articles Widget
 */
export const TrendingArticlesWidget: React.FC = () => {
  const trendingArticles = [
    {
      id: 1,
      title: 'CRISPR-Cas9 Gene Editing: A Revolution in Treating Genetic Disorders',
      authors: 'Smith J, Johnson R, Williams M',
      views: 12500,
      downloads: 3200,
      trend: 'hot',
      publishedDate: '2024-03-01',
      category: 'Genetics',
    },
    {
      id: 2,
      title: 'Machine Learning Approaches to Drug Discovery and Development',
      authors: 'Brown A, Davis K, Miller L',
      views: 9800,
      downloads: 2100,
      trend: 'rising',
      publishedDate: '2024-02-28',
      category: 'Bioinformatics',
    },
    {
      id: 3,
      title: 'Microbiome Analysis Reveals Novel Insights into Human Health',
      authors: 'Wilson P, Martinez C, Garcia E',
      views: 8700,
      downloads: 1900,
      trend: 'steady',
      publishedDate: '2024-02-25',
      category: 'Microbiology',
    },
  ];

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'hot':
        return <Zap className="w-4 h-4 text-red-500" />;
      case 'rising':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      default:
        return <Target className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Trending Now</h2>
        </div>
        <Link
          to="/trending"
          className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
        >
          See More
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {trendingArticles.map((article, idx) => (
          <div
            key={article.id}
            className="p-4 border border-gray-200 rounded-lg hover:border-indigo-300 hover:shadow-md transition-all duration-200 cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  {idx + 1}
                </div>
                {getTrendIcon(article.trend)}
              </div>
              <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                {article.category}
              </span>
            </div>

            <h3 className="font-semibold text-gray-900 mb-2 hover:text-indigo-600 transition-colors">
              {article.title}
            </h3>

            <p className="text-sm text-gray-600 mb-3">{article.authors}</p>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <Eye className="w-4 h-4 mr-1" />
                  {article.views.toLocaleString()}
                </div>
                <div className="flex items-center">
                  <Download className="w-4 h-4 mr-1" />
                  {article.downloads.toLocaleString()}
                </div>
              </div>
              <span>
                {new Date(article.publishedDate).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Popular Topics Widget
 */
export const PopularTopicsWidget: React.FC = () => {
  const topics = [
    { name: 'CRISPR', count: 234, color: 'from-blue-500 to-blue-600' },
    { name: 'Machine Learning', count: 189, color: 'from-purple-500 to-purple-600' },
    { name: 'Immunotherapy', count: 156, color: 'from-pink-500 to-pink-600' },
    { name: 'Microbiome', count: 142, color: 'from-green-500 to-green-600' },
    { name: 'Cancer Research', count: 128, color: 'from-red-500 to-red-600' },
    { name: 'Genomics', count: 115, color: 'from-indigo-500 to-indigo-600' },
    { name: 'Stem Cells', count: 98, color: 'from-orange-500 to-orange-600' },
    { name: 'Neuroscience', count: 87, color: 'from-teal-500 to-teal-600' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Popular Topics</h2>
        <Link
          to="/topics"
          className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
        >
          Browse All
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="flex flex-wrap gap-3">
        {topics.map((topic) => (
          <Link
            key={topic.name}
            to={`/topics/${topic.name.toLowerCase().replace(/\s+/g, '-')}`}
            className="group"
          >
            <div className={`px-4 py-2 bg-gradient-to-br ${topic.color} rounded-full text-white font-medium text-sm hover:scale-105 transition-transform duration-200 shadow-md cursor-pointer`}>
              <span>{topic.name}</span>
              <span className="ml-2 opacity-75">({topic.count})</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

/**
 * Quick Actions Widget
 */
export const QuickActionsWidget: React.FC = () => {
  const actions = [
    {
      icon: <FileText className="w-6 h-6" />,
      label: 'Submit Manuscript',
      description: 'One-click submission',
      href: '/submit',
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: <Users className="w-6 h-6" />,
      label: 'Become a Reviewer',
      description: 'Join our panel',
      href: '/reviewers/join',
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: <BookOpen className="w-6 h-6" />,
      label: 'Browse Articles',
      description: 'Explore research',
      href: '/articles',
      color: 'from-indigo-500 to-indigo-600',
    },
    {
      icon: <Bell className="w-6 h-6" />,
      label: 'Get Alerts',
      description: 'Stay updated',
      href: '/alerts',
      color: 'from-pink-500 to-pink-600',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {actions.map((action) => (
          <Link
            key={action.label}
            to={action.href}
            className="group p-4 border-2 border-gray-200 rounded-lg hover:border-transparent hover:shadow-lg transition-all duration-200"
          >
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center text-white mb-3 group-hover:scale-110 transition-transform duration-200`}>
              {action.icon}
            </div>
            <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-indigo-600 transition-colors">
              {action.label}
            </h3>
            <p className="text-sm text-gray-600">{action.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
};

/**
 * Recent Articles Widget
 */
export const RecentArticlesWidget: React.FC = () => {
  const articles = [
    {
      id: 1,
      title: 'Novel Therapeutic Approaches for Alzheimer\'s Disease',
      authors: 'Thompson R, Lee S, Chen Y',
      category: 'Neuroscience',
      publishedDate: '2024-03-12',
      openAccess: true,
    },
    {
      id: 2,
      title: 'Advances in Renewable Energy Storage Systems',
      authors: 'Kumar A, Patel V, Singh R',
      category: 'Engineering',
      publishedDate: '2024-03-11',
      openAccess: true,
    },
    {
      id: 3,
      title: 'Biodiversity Conservation in Tropical Rainforests',
      authors: 'Rodriguez M, Silva J, Costa F',
      category: 'Ecology',
      publishedDate: '2024-03-10',
      openAccess: true,
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Recently Published</h2>
        <Link
          to="/articles/recent"
          className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
        >
          View All
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {articles.map((article) => (
          <div
            key={article.id}
            className="p-4 border border-gray-200 rounded-lg hover:border-indigo-300 hover:shadow-md transition-all duration-200 cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded-full">
                {article.category}
              </span>
              {article.openAccess && (
                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full flex items-center">
                  🔓 Open Access
                </span>
              )}
            </div>

            <h3 className="font-semibold text-gray-900 mb-2 hover:text-indigo-600 transition-colors">
              {article.title}
            </h3>

            <p className="text-sm text-gray-600 mb-2">{article.authors}</p>

            <div className="flex items-center text-xs text-gray-500">
              <Calendar className="w-3 h-3 mr-1" />
              Published: {new Date(article.publishedDate).toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric',
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Upcoming Events Widget
 */
export const UpcomingEventsWidget: React.FC = () => {
  const events = [
    {
      id: 1,
      title: 'Annual Scientific Symposium 2024',
      date: '2024-06-15',
      location: 'Virtual',
      type: 'Conference',
    },
    {
      id: 2,
      title: 'Author Workshop: Writing Effective Abstracts',
      date: '2024-04-20',
      location: 'Online',
      type: 'Workshop',
    },
    {
      id: 3,
      title: 'Peer Review Best Practices Webinar',
      date: '2024-04-05',
      location: 'Webinar',
      type: 'Training',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-teal-500 rounded-lg flex items-center justify-center">
            <Calendar className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Upcoming Events</h2>
        </div>
        <Link
          to="/events"
          className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
        >
          All Events
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {events.map((event) => (
          <div
            key={event.id}
            className="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg hover:border-indigo-300 hover:shadow-md transition-all duration-200 cursor-pointer"
          >
            <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex flex-col items-center justify-center text-white">
              <div className="text-xs font-medium">
                {new Date(event.date).toLocaleDateString('en-US', { month: 'short' }).toUpperCase()}
              </div>
              <div className="text-2xl font-bold">
                {new Date(event.date).getDate()}
              </div>
            </div>

            <div className="flex-1">
              <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                {event.type}
              </span>
              <h3 className="font-semibold text-gray-900 mt-2 mb-1">{event.title}</h3>
              <p className="text-sm text-gray-600">{event.location}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Complete Homepage Layout with All Widgets
 */
export const HomepageWidgetsLayout: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Journal Stats - Full Width */}
      <JournalStatsWidget />

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-8">
          <TrendingArticlesWidget />
          <RecentArticlesWidget />
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-8">
          <QuickActionsWidget />
          <AnnouncementsWidget />
          <PopularTopicsWidget />
          <UpcomingEventsWidget />
        </div>
      </div>
    </div>
  );
};
