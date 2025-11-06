import React, { useState, useEffect } from 'react';
import {
  BookOpenIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CalendarIcon,
  DocumentPlusIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  CheckCircleIcon,
  PhotoIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';

interface Issue {
  id: number;
  volume: number;
  number: number;
  year: number;
  title: string | null;
  description: string | null;
  cover_image_url: string | null;
  is_published: boolean;
  published_at: string | null;
  scheduled_publication: string | null;
  doi: string | null;
  article_count: number;
  created_at: string;
}

interface Article {
  id: number;
  manuscript_id: string;
  title: string;
  authors: string[];
  page_start: number | null;
  page_end: number | null;
  doi: string | null;
  article_order: number;
  article_type: string;
  published_at: string;
}

interface Statistics {
  total_issues: number;
  published_issues: number;
  scheduled_issues: number;
  current_year_issues: number;
  articles_in_current_issue: number;
  unpublished_accepted_articles: number;
}

const IssueManager: React.FC = () => {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [showTOC, setShowTOC] = useState(false);
  const [tocArticles, setTocArticles] = useState<Article[]>([]);

  // Form states
  const [newIssue, setNewIssue] = useState({
    volume: 1,
    number: 1,
    year: new Date().getFullYear(),
    title: '',
    description: '',
    scheduled_publication: '',
  });

  useEffect(() => {
    fetchIssues();
    fetchStatistics();
  }, []);

  const fetchIssues = async () => {
    try {
      setLoading(true);
      const response = await apiService.issues.list({ page_size: 100 });
      setIssues(response.data.issues);
    } catch (error) {
      console.error('Failed to fetch issues:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await apiService.issues.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const fetchTableOfContents = async (issueId: number) => {
    try {
      const response = await apiService.issues.getTableOfContents(issueId);
      setTocArticles(response.data.articles);
      setShowTOC(true);
    } catch (error) {
      console.error('Failed to fetch table of contents:', error);
    }
  };

  const handleCreateIssue = async () => {
    try {
      await apiService.issues.create(newIssue);
      setShowCreateModal(false);
      setNewIssue({
        volume: 1,
        number: 1,
        year: new Date().getFullYear(),
        title: '',
        description: '',
        scheduled_publication: '',
      });
      fetchIssues();
      fetchStatistics();
    } catch (error) {
      console.error('Failed to create issue:', error);
      alert('Failed to create issue');
    }
  };

  const handlePublishIssue = async (issueId: number) => {
    if (!confirm('Are you sure you want to publish this issue? This action will assign DOIs to all articles.')) {
      return;
    }

    try {
      await apiService.issues.publish(issueId, {
        assign_dois: true,
        send_notifications: true,
      });
      alert('Issue published successfully!');
      fetchIssues();
      fetchStatistics();
    } catch (error) {
      console.error('Failed to publish issue:', error);
      alert('Failed to publish issue');
    }
  };

  const handleDeleteIssue = async (issueId: number) => {
    if (!confirm('Are you sure you want to delete this issue?')) {
      return;
    }

    try {
      await apiService.issues.delete(issueId);
      fetchIssues();
      fetchStatistics();
    } catch (error) {
      console.error('Failed to delete issue:', error);
      alert('Failed to delete issue');
    }
  };

  const handleReorderArticle = async (articleId: number, direction: 'up' | 'down') => {
    if (!selectedIssue) return;

    const currentIndex = tocArticles.findIndex(a => a.id === articleId);
    if (currentIndex === -1) return;

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= tocArticles.length) return;

    // Create new order
    const newArticles = [...tocArticles];
    const [movedArticle] = newArticles.splice(currentIndex, 1);
    newArticles.splice(newIndex, 0, movedArticle);

    // Update orders
    const reorderData = newArticles.map((article, index) => ({
      manuscript_id: article.id,
      order: index + 1,
    }));

    try {
      await apiService.issues.reorderArticles(selectedIssue.id, { article_orders: reorderData });
      setTocArticles(newArticles);
    } catch (error) {
      console.error('Failed to reorder articles:', error);
      alert('Failed to reorder articles');
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Issue Manager</h1>
            <p className="mt-2 text-gray-600">Organize and publish journal issues</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create New Issue
          </button>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Total Issues</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">{statistics.total_issues}</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Published</div>
              <div className="text-2xl font-bold text-green-600 mt-1">{statistics.published_issues}</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Scheduled</div>
              <div className="text-2xl font-bold text-blue-600 mt-1">{statistics.scheduled_issues}</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">This Year</div>
              <div className="text-2xl font-bold text-purple-600 mt-1">{statistics.current_year_issues}</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Current Articles</div>
              <div className="text-2xl font-bold text-indigo-600 mt-1">{statistics.articles_in_current_issue}</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Ready to Assign</div>
              <div className="text-2xl font-bold text-orange-600 mt-1">{statistics.unpublished_accepted_articles}</div>
            </div>
          </div>
        )}

        {/* Issues Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-3 text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : issues.length === 0 ? (
            <div className="col-span-3 text-center py-12">
              <BookOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-gray-600">No issues yet. Create your first issue!</p>
            </div>
          ) : (
            issues.map((issue) => (
              <div
                key={issue.id}
                className={`bg-white rounded-lg shadow-lg overflow-hidden border-t-4 ${
                  issue.is_published ? 'border-green-500' : 'border-blue-500'
                }`}
              >
                {/* Cover Image */}
                {issue.cover_image_url ? (
                  <img
                    src={issue.cover_image_url}
                    alt={`Volume ${issue.volume}, Issue ${issue.number}`}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
                    <BookOpenIcon className="h-20 w-20 text-blue-400" />
                  </div>
                )}

                {/* Content */}
                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        Vol {issue.volume}, No {issue.number}
                      </h3>
                      <p className="text-sm text-gray-600">{issue.year}</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        issue.is_published
                          ? 'bg-green-100 text-green-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {issue.is_published ? 'Published' : 'Draft'}
                    </span>
                  </div>

                  {issue.title && (
                    <h4 className="text-lg font-semibold text-gray-800 mb-2">{issue.title}</h4>
                  )}

                  {issue.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">{issue.description}</p>
                  )}

                  <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                    <div className="flex items-center">
                      <DocumentPlusIcon className="h-4 w-4 mr-1" />
                      <span>{issue.article_count} articles</span>
                    </div>
                    {issue.scheduled_publication && !issue.is_published && (
                      <div className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        <span>{formatDate(issue.scheduled_publication)}</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        setSelectedIssue(issue);
                        fetchTableOfContents(issue.id);
                      }}
                      className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
                    >
                      View TOC
                    </button>

                    {!issue.is_published && (
                      <>
                        <button
                          onClick={() => handlePublishIssue(issue.id)}
                          className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium flex items-center justify-center"
                        >
                          <RocketLaunchIcon className="h-4 w-4 mr-1" />
                          Publish
                        </button>

                        <button
                          onClick={() => handleDeleteIssue(issue.id)}
                          className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Create Issue Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Create New Issue</h3>

              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Volume *
                    </label>
                    <input
                      type="number"
                      value={newIssue.volume}
                      onChange={(e) => setNewIssue({ ...newIssue, volume: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      min="1"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Number *
                    </label>
                    <input
                      type="number"
                      value={newIssue.number}
                      onChange={(e) => setNewIssue({ ...newIssue, number: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      min="1"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Year *
                    </label>
                    <input
                      type="number"
                      value={newIssue.year}
                      onChange={(e) => setNewIssue({ ...newIssue, year: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      min="1900"
                      max="2100"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={newIssue.title}
                    onChange={(e) => setNewIssue({ ...newIssue, title: e.target.value })}
                    placeholder="e.g., Special Issue on Machine Learning"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (Optional)
                  </label>
                  <textarea
                    value={newIssue.description}
                    onChange={(e) => setNewIssue({ ...newIssue, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Brief description of this issue..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scheduled Publication (Optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={newIssue.scheduled_publication}
                    onChange={(e) => setNewIssue({ ...newIssue, scheduled_publication: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateIssue}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  Create Issue
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Table of Contents Modal */}
        {showTOC && selectedIssue && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 bg-gray-50 sticky top-0">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">
                      Table of Contents
                    </h3>
                    <p className="text-gray-600 mt-1">
                      Volume {selectedIssue.volume}, Issue {selectedIssue.number} ({selectedIssue.year})
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setShowTOC(false);
                      setSelectedIssue(null);
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
              </div>

              <div className="p-6">
                {tocArticles.length === 0 ? (
                  <div className="text-center py-12">
                    <DocumentPlusIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="mt-4 text-gray-600">No articles in this issue yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {tocArticles.map((article, index) => (
                      <div
                        key={article.id}
                        className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-800 text-sm font-bold">
                                {index + 1}
                              </span>
                              <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded font-medium">
                                {article.article_type}
                              </span>
                            </div>
                            <h4 className="text-lg font-semibold text-gray-900 mb-1">
                              {article.title}
                            </h4>
                            <p className="text-sm text-gray-600 mb-2">
                              {article.authors.join(', ')}
                            </p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span>ID: {article.manuscript_id}</span>
                              {article.page_start && article.page_end && (
                                <span>pp. {article.page_start}-{article.page_end}</span>
                              )}
                              {article.doi && (
                                <span className="font-mono">{article.doi}</span>
                              )}
                            </div>
                          </div>

                          {/* Reorder Buttons */}
                          <div className="flex flex-col space-y-1 ml-4">
                            <button
                              onClick={() => handleReorderArticle(article.id, 'up')}
                              disabled={index === 0}
                              className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                              <ArrowUpIcon className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleReorderArticle(article.id, 'down')}
                              disabled={index === tocArticles.length - 1}
                              className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                              <ArrowDownIcon className="h-5 w-5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {!selectedIssue.is_published && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <button
                      className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center"
                    >
                      <DocumentPlusIcon className="h-5 w-5 mr-2" />
                      Add Article to Issue
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IssueManager;
