import React, { useState, useEffect } from 'react';
import {
  ChatBubbleLeftRightIcon,
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  UserGroupIcon,
  ChatBubbleOvalLeftIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';
import DiscussionThread from './DiscussionThread';

interface Discussion {
  id: number;
  manuscript_id: number;
  manuscript_title: string | null;
  stage: string;
  subject: string;
  status: string;
  created_by_id: number;
  created_by_name: string;
  message_count: number;
  last_message_at: string | null;
  created_at: string;
  participants: Array<{
    user_id: number;
    user_name: string;
    role: string;
  }>;
}

interface DiscussionListProps {
  manuscriptId?: number;
  isEditor?: boolean;
  showCreateButton?: boolean;
}

const DiscussionList: React.FC<DiscussionListProps> = ({
  manuscriptId,
  isEditor = false,
  showCreateButton = true,
}) => {
  const [discussions, setDiscussions] = useState<Discussion[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDiscussionId, setSelectedDiscussionId] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState({
    stage: '',
    status: 'active',
    search: '',
  });
  const [newDiscussion, setNewDiscussion] = useState({
    manuscript_id: manuscriptId || 0,
    stage: 'submission',
    subject: '',
    message: '',
    participant_ids: [] as number[],
  });

  useEffect(() => {
    fetchDiscussions();
  }, [manuscriptId, filters.stage, filters.status]);

  const fetchDiscussions = async () => {
    try {
      setLoading(true);
      const params: any = {};

      if (manuscriptId) {
        params.manuscript_id = manuscriptId;
      }
      if (filters.stage) {
        params.stage = filters.stage;
      }
      if (filters.status) {
        params.status = filters.status;
      }

      const response = await apiService.discussions.list(params);
      let discussionsList = response.data.discussions || [];

      // Apply search filter locally
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        discussionsList = discussionsList.filter(
          (d: Discussion) =>
            d.subject.toLowerCase().includes(searchLower) ||
            d.manuscript_title?.toLowerCase().includes(searchLower) ||
            d.created_by_name.toLowerCase().includes(searchLower)
        );
      }

      setDiscussions(discussionsList);
    } catch (error) {
      console.error('Failed to fetch discussions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDiscussion = async () => {
    if (!newDiscussion.subject || !newDiscussion.message) {
      alert('Please fill in subject and message');
      return;
    }

    if (newDiscussion.participant_ids.length === 0) {
      alert('Please add at least one participant');
      return;
    }

    try {
      await apiService.discussions.create(newDiscussion);
      setShowCreateModal(false);
      setNewDiscussion({
        manuscript_id: manuscriptId || 0,
        stage: 'submission',
        subject: '',
        message: '',
        participant_ids: [],
      });
      await fetchDiscussions();
    } catch (error: any) {
      console.error('Failed to create discussion:', error);
      alert(error.response?.data?.detail || 'Failed to create discussion');
    }
  };

  const getStageBadgeColor = (stage: string) => {
    const colors: { [key: string]: string } = {
      submission: 'bg-blue-100 text-blue-800',
      review: 'bg-purple-100 text-purple-800',
      copyediting: 'bg-yellow-100 text-yellow-800',
      production: 'bg-green-100 text-green-800',
    };
    return colors[stage] || 'bg-gray-100 text-gray-800';
  };

  const getStatusBadgeColor = (status: string) => {
    const colors: { [key: string]: string } = {
      active: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-600',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  const formatStage = (stage: string) => {
    return stage.charAt(0).toUpperCase() + stage.slice(1);
  };

  if (selectedDiscussionId) {
    return (
      <DiscussionThread
        discussionId={selectedDiscussionId}
        onClose={() => {
          setSelectedDiscussionId(null);
          fetchDiscussions();
        }}
      />
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ChatBubbleLeftRightIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">Discussions</h3>
              <p className="text-sm text-gray-600">
                {discussions.length} {discussions.length === 1 ? 'discussion' : 'discussions'}
              </p>
            </div>
          </div>

          {showCreateButton && isEditor && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <PlusIcon className="h-5 w-5" />
              <span>New Discussion</span>
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search discussions..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              onKeyUp={() => fetchDiscussions()}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Stage Filter */}
          <div className="relative">
            <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={filters.stage}
              onChange={(e) => setFilters({ ...filters, stage: e.target.value })}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="">All Stages</option>
              <option value="submission">Submission</option>
              <option value="review">Review</option>
              <option value="copyediting">Copyediting</option>
              <option value="production">Production</option>
            </select>
          </div>

          {/* Status Filter */}
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      {/* Discussions List */}
      <div className="divide-y divide-gray-200">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
          </div>
        ) : discussions.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <ChatBubbleLeftRightIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium">No discussions found</p>
            <p className="text-sm mt-1">
              {isEditor && showCreateButton
                ? 'Click "New Discussion" to start a conversation'
                : 'No active discussions at this time'}
            </p>
          </div>
        ) : (
          discussions.map((discussion) => (
            <div
              key={discussion.id}
              onClick={() => setSelectedDiscussionId(discussion.id)}
              className="p-6 hover:bg-gray-50 transition-colors cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Discussion Header */}
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                      {discussion.subject}
                    </h4>
                    <div className="flex items-center space-x-2 ml-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStageBadgeColor(discussion.stage)}`}>
                        {formatStage(discussion.stage)}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeColor(discussion.status)}`}>
                        {discussion.status}
                      </span>
                    </div>
                  </div>

                  {/* Manuscript Title (if showing discussions from multiple manuscripts) */}
                  {!manuscriptId && discussion.manuscript_title && (
                    <p className="text-sm text-gray-600 mb-2">
                      📄 {discussion.manuscript_title}
                    </p>
                  )}

                  {/* Discussion Meta */}
                  <div className="flex items-center space-x-6 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <UserGroupIcon className="h-4 w-4" />
                      <span>{discussion.participants.length} participants</span>
                    </div>

                    <div className="flex items-center space-x-1">
                      <ChatBubbleOvalLeftIcon className="h-4 w-4" />
                      <span>{discussion.message_count} messages</span>
                    </div>

                    <div className="flex items-center space-x-1">
                      <span>Started by {discussion.created_by_name}</span>
                    </div>

                    {discussion.last_message_at && (
                      <div className="flex items-center space-x-1">
                        <span>•</span>
                        <span>Last activity {formatDate(discussion.last_message_at)}</span>
                      </div>
                    )}
                  </div>

                  {/* Participants Preview */}
                  {discussion.participants.length > 0 && (
                    <div className="mt-3 flex items-center space-x-2">
                      <div className="flex -space-x-2">
                        {discussion.participants.slice(0, 5).map((participant, index) => (
                          <div
                            key={participant.user_id}
                            className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold border-2 border-white"
                            title={participant.user_name}
                          >
                            {participant.user_name
                              .split(' ')
                              .map((n) => n[0])
                              .join('')
                              .substring(0, 2)
                              .toUpperCase()}
                          </div>
                        ))}
                        {discussion.participants.length > 5 && (
                          <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs font-bold border-2 border-white">
                            +{discussion.participants.length - 5}
                          </div>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {discussion.participants.map((p) => p.user_name).join(', ')}
                      </span>
                    </div>
                  )}
                </div>

                {/* Arrow Indicator */}
                <div className="ml-4 text-gray-400 group-hover:text-blue-600 transition-colors">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Discussion Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 sticky top-0 bg-white">
              <h3 className="text-lg font-bold text-gray-900">Start New Discussion</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              {/* Manuscript ID (if not provided) */}
              {!manuscriptId && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Manuscript ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={newDiscussion.manuscript_id || ''}
                    onChange={(e) =>
                      setNewDiscussion({ ...newDiscussion, manuscript_id: parseInt(e.target.value) || 0 })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter manuscript ID"
                  />
                </div>
              )}

              {/* Stage */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stage <span className="text-red-500">*</span>
                </label>
                <select
                  value={newDiscussion.stage}
                  onChange={(e) => setNewDiscussion({ ...newDiscussion, stage: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="submission">Submission</option>
                  <option value="review">Review</option>
                  <option value="copyediting">Copyediting</option>
                  <option value="production">Production</option>
                </select>
              </div>

              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newDiscussion.subject}
                  onChange={(e) => setNewDiscussion({ ...newDiscussion, subject: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter discussion subject"
                  maxLength={500}
                />
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={newDiscussion.message}
                  onChange={(e) => setNewDiscussion({ ...newDiscussion, message: e.target.value })}
                  rows={5}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Enter your message..."
                  maxLength={10000}
                />
              </div>

              {/* Participant IDs */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Participant IDs <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newDiscussion.participant_ids.join(', ')}
                  onChange={(e) => {
                    const ids = e.target.value
                      .split(',')
                      .map((id) => parseInt(id.trim()))
                      .filter((id) => !isNaN(id));
                    setNewDiscussion({ ...newDiscussion, participant_ids: ids });
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter user IDs separated by commas (e.g., 1, 2, 3)"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Enter the IDs of users you want to include in this discussion
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end space-x-3 px-6 py-4 bg-gray-50 rounded-b-lg border-t border-gray-200 sticky bottom-0">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateDiscussion}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Start Discussion
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiscussionList;
