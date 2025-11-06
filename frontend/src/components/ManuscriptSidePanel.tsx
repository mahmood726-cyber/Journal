import React, { useState, useEffect } from 'react';
import {
  DocumentTextIcon,
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  TagIcon,
  UserCircleIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import SidePanel from './SidePanel';
import ParticipantsPanel from './ParticipantsPanel';
import DiscussionList from './DiscussionList';
import { apiService } from '../services/api';

interface Manuscript {
  id: number;
  manuscript_id: string;
  title: string;
  abstract: string;
  keywords: string[];
  status: string;
  stage: string;
  submitted_at: string;
  submitter_name: string;
  authors: Array<{
    id: number;
    full_name: string;
    email: string;
    affiliation: string;
  }>;
}

interface ManuscriptSidePanelProps {
  manuscriptId: number;
  isOpen: boolean;
  onClose: () => void;
  isEditor?: boolean;
}

type TabType = 'details' | 'participants' | 'discussions';

const ManuscriptSidePanel: React.FC<ManuscriptSidePanelProps> = ({
  manuscriptId,
  isOpen,
  onClose,
  isEditor = false,
}) => {
  const [manuscript, setManuscript] = useState<Manuscript | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('details');

  useEffect(() => {
    if (isOpen && manuscriptId) {
      fetchManuscript();
    }
  }, [isOpen, manuscriptId]);

  const fetchManuscript = async () => {
    try {
      setLoading(true);
      const response = await apiService.manuscripts.get(manuscriptId);
      setManuscript(response.data);
    } catch (error) {
      console.error('Failed to fetch manuscript:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeColor = (status: string) => {
    const colors: { [key: string]: string } = {
      draft: 'bg-gray-100 text-gray-800',
      submitted: 'bg-blue-100 text-blue-800',
      under_review: 'bg-purple-100 text-purple-800',
      revisions_required: 'bg-yellow-100 text-yellow-800',
      accepted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      published: 'bg-indigo-100 text-indigo-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStageBadgeColor = (stage: string) => {
    const colors: { [key: string]: string } = {
      submission: 'bg-blue-100 text-blue-700',
      review: 'bg-purple-100 text-purple-700',
      copyediting: 'bg-yellow-100 text-yellow-700',
      production: 'bg-green-100 text-green-700',
    };
    return colors[stage] || 'bg-gray-100 text-gray-700';
  };

  const formatStatus = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const formatStage = (stage: string) => {
    return stage.charAt(0).toUpperCase() + stage.slice(1);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const tabs: Array<{ id: TabType; label: string; icon: React.ReactNode }> = [
    {
      id: 'details',
      label: 'Details',
      icon: <DocumentTextIcon className="h-5 w-5" />,
    },
    {
      id: 'participants',
      label: 'Participants',
      icon: <UserGroupIcon className="h-5 w-5" />,
    },
    {
      id: 'discussions',
      label: 'Discussions',
      icon: <ChatBubbleLeftRightIcon className="h-5 w-5" />,
    },
  ];

  const renderTabContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (!manuscript) {
      return (
        <div className="p-6 text-center text-gray-500">
          <p>Manuscript not found</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'details':
        return (
          <div className="p-6 space-y-6">
            {/* Status and Stage */}
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadgeColor(manuscript.status)}`}>
                {formatStatus(manuscript.status)}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStageBadgeColor(manuscript.stage)}`}>
                {formatStage(manuscript.stage)}
              </span>
            </div>

            {/* Manuscript ID */}
            <div className="flex items-center space-x-2 text-gray-600">
              <TagIcon className="h-5 w-5" />
              <span className="font-mono text-sm">{manuscript.manuscript_id}</span>
            </div>

            {/* Title */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Title</h3>
              <p className="text-base text-gray-900">{manuscript.title}</p>
            </div>

            {/* Abstract */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Abstract</h3>
              <p className="text-sm text-gray-700 leading-relaxed">{manuscript.abstract}</p>
            </div>

            {/* Keywords */}
            {manuscript.keywords && manuscript.keywords.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Keywords</h3>
                <div className="flex flex-wrap gap-2">
                  {manuscript.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Authors */}
            {manuscript.authors && manuscript.authors.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-3">Authors</h3>
                <div className="space-y-3">
                  {manuscript.authors.map((author) => (
                    <div key={author.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                          {author.full_name
                            .split(' ')
                            .map((n) => n[0])
                            .join('')
                            .substring(0, 2)
                            .toUpperCase()}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900">{author.full_name}</p>
                        <p className="text-sm text-gray-600">{author.email}</p>
                        {author.affiliation && (
                          <p className="text-xs text-gray-500 mt-1">{author.affiliation}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Submission Info */}
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <CalendarIcon className="h-5 w-5" />
                <span>Submitted on {formatDate(manuscript.submitted_at)}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600 mt-2">
                <UserCircleIcon className="h-5 w-5" />
                <span>Submitted by {manuscript.submitter_name}</span>
              </div>
            </div>
          </div>
        );

      case 'participants':
        return (
          <div className="p-6">
            <ParticipantsPanel manuscriptId={manuscriptId} isEditor={isEditor} />
          </div>
        );

      case 'discussions':
        return (
          <div className="p-6">
            <DiscussionList manuscriptId={manuscriptId} isEditor={isEditor} />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <SidePanel
      isOpen={isOpen}
      onClose={onClose}
      title={manuscript?.title || 'Manuscript Details'}
      subtitle={manuscript ? `ID: ${manuscript.manuscript_id}` : undefined}
      width="wide"
    >
      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </SidePanel>
  );
};

export default ManuscriptSidePanel;
