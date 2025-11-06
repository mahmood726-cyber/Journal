import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import {
  SparklesIcon,
  UserIcon,
  CheckCircleIcon,
  XMarkIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ClockIcon,
  StarIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { api } from '../../services/api';

interface ReviewerMatch {
  userId: number;
  name: string;
  email: string;
  affiliation: string;
  orcid?: string;
  matchScore: number;
  expertiseScore: number;
  networkScore: number;
  performanceScore: number;
  availabilityScore: number;
  diversityScore: number;
  specializations: string[];
  recentReviews: number;
  avgReviewTime: number;
  acceptanceRate: number;
  citationOverlap: number;
  reasoning: string;
}

interface Manuscript {
  id: number;
  manuscriptId: string;
  title: string;
  abstract: string;
  keywords: string[];
  subject: string;
}

const ReviewerMatching: React.FC = () => {
  const { manuscriptId } = useParams<{ manuscriptId: string }>();
  const [selectedReviewers, setSelectedReviewers] = useState<number[]>([]);
  const [showDetails, setShowDetails] = useState<number | null>(null);

  const { data: manuscript, isLoading: manuscriptLoading } = useQuery<Manuscript>(
    ['manuscript', manuscriptId],
    () => api.get(`/manuscripts/${manuscriptId}`).then((res) => res.data)
  );

  const { data: matches, isLoading: matchesLoading, refetch } = useQuery<ReviewerMatch[]>(
    ['reviewer-matches', manuscriptId],
    () => api.get(`/manuscripts/${manuscriptId}/reviewer-matches`).then((res) => res.data),
    { enabled: !!manuscriptId }
  );

  const inviteMutation = useMutation(
    (reviewerIds: number[]) =>
      api.post(`/manuscripts/${manuscriptId}/invite-reviewers`, { reviewerIds }),
    {
      onSuccess: () => {
        toast.success('Review invitations sent successfully!');
        setSelectedReviewers([]);
      },
      onError: () => {
        toast.error('Failed to send invitations. Please try again.');
      },
    }
  );

  const handleToggleReviewer = (userId: number) => {
    setSelectedReviewers((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    );
  };

  const handleSendInvitations = () => {
    if (selectedReviewers.length === 0) {
      toast.error('Please select at least one reviewer');
      return;
    }
    if (selectedReviewers.length > 5) {
      toast.error('Please select no more than 5 reviewers');
      return;
    }
    inviteMutation.mutate(selectedReviewers);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-blue-600 bg-blue-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Low';
  };

  if (manuscriptLoading || matchesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-sm text-gray-600">Analyzing manuscript and matching reviewers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center mb-4">
          <SparklesIcon className="h-8 w-8 mr-3" />
          <h1 className="text-3xl font-bold">AI-Powered Reviewer Matching</h1>
        </div>
        <p className="text-indigo-100">
          Our AI analyzes manuscript content, citation networks, and reviewer performance to suggest
          the most qualified reviewers.
        </p>
      </div>

      {/* Manuscript Info */}
      {manuscript && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-start">
            <DocumentTextIcon className="h-6 w-6 text-indigo-600 mr-3 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">{manuscript.title}</h2>
              <div className="flex flex-wrap gap-2 mb-3">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                  {manuscript.subject}
                </span>
                {manuscript.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
              <p className="text-sm text-gray-600 line-clamp-2">{manuscript.abstract}</p>
            </div>
          </div>
        </div>
      )}

      {/* Selection Summary */}
      {selectedReviewers.length > 0 && (
        <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <CheckCircleIcon className="h-5 w-5 text-green-400 mr-2" />
              <p className="text-sm text-green-700">
                <strong>{selectedReviewers.length}</strong> reviewer
                {selectedReviewers.length !== 1 ? 's' : ''} selected
                {selectedReviewers.length >= 3 && selectedReviewers.length <= 5 && (
                  <span className="ml-2 text-green-600">(Recommended: 3-5 reviewers)</span>
                )}
              </p>
            </div>
            <button
              onClick={handleSendInvitations}
              disabled={inviteMutation.isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <EnvelopeIcon className="h-4 w-4 mr-2" />
              {inviteMutation.isLoading ? 'Sending...' : 'Send Invitations'}
            </button>
          </div>
        </div>
      )}

      {/* AI Matching Explanation */}
      <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
        <div className="flex items-start">
          <SparklesIcon className="h-5 w-5 text-purple-600 mr-3 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-purple-900">
            <p className="font-medium mb-2">How AI Matching Works:</p>
            <ul className="space-y-1 text-xs">
              <li>
                <strong>Expertise (40%):</strong> TF-IDF analysis of publications vs. manuscript
                content
              </li>
              <li>
                <strong>Network (20%):</strong> Citation overlap and co-authorship patterns
              </li>
              <li>
                <strong>Performance (15%):</strong> Review quality, timeliness, and acceptance rates
              </li>
              <li>
                <strong>Availability (15%):</strong> Current workload and response history
              </li>
              <li>
                <strong>Diversity (10%):</strong> Geographic and institutional distribution
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Reviewer Matches */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Top Reviewer Matches ({matches?.length || 0})
        </h3>

        {matches && matches.length > 0 ? (
          matches.map((match, index) => (
            <div
              key={match.userId}
              className={`bg-white rounded-lg shadow-sm border-2 transition-all duration-200 ${
                selectedReviewers.includes(match.userId)
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-200 hover:border-indigo-300'
              }`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  {/* Reviewer Info */}
                  <div className="flex-1">
                    <div className="flex items-center mb-3">
                      <div className="flex-shrink-0">
                        <div className="h-12 w-12 rounded-full bg-indigo-100 flex items-center justify-center">
                          <span className="text-xl font-bold text-indigo-600">#{index + 1}</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="flex items-center">
                          <h4 className="text-lg font-semibold text-gray-900">{match.name}</h4>
                          {match.orcid && (
                            <a
                              href={`https://orcid.org/${match.orcid}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ml-2 text-green-600 hover:text-green-800"
                              title="ORCID iD"
                            >
                              <svg className="h-4 w-4" viewBox="0 0 256 256">
                                <path
                                  fill="currentColor"
                                  d="M256 128c0 70.7-57.3 128-128 128S0 198.7 0 128 57.3 0 128 0s128 57.3 128 128z"
                                />
                              </svg>
                            </a>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{match.affiliation}</p>
                        <p className="text-xs text-gray-500 mt-1">{match.email}</p>
                      </div>
                    </div>

                    {/* Match Score */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Overall Match Score</span>
                        <span className={`text-lg font-bold ${getScoreColor(match.matchScore).split(' ')[0]}`}>
                          {match.matchScore}% {getScoreLabel(match.matchScore)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full transition-all duration-500 ${
                            match.matchScore >= 80
                              ? 'bg-green-500'
                              : match.matchScore >= 60
                              ? 'bg-blue-500'
                              : match.matchScore >= 40
                              ? 'bg-yellow-500'
                              : 'bg-gray-400'
                          }`}
                          style={{ width: `${match.matchScore}%` }}
                        />
                      </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
                      <div className="text-center">
                        <div className="text-xs text-gray-500 mb-1">Expertise</div>
                        <div className={`text-lg font-semibold ${getScoreColor(match.expertiseScore).split(' ')[0]}`}>
                          {match.expertiseScore}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-gray-500 mb-1">Network</div>
                        <div className={`text-lg font-semibold ${getScoreColor(match.networkScore).split(' ')[0]}`}>
                          {match.networkScore}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-gray-500 mb-1">Performance</div>
                        <div className={`text-lg font-semibold ${getScoreColor(match.performanceScore).split(' ')[0]}`}>
                          {match.performanceScore}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-gray-500 mb-1">Availability</div>
                        <div className={`text-lg font-semibold ${getScoreColor(match.availabilityScore).split(' ')[0]}`}>
                          {match.availabilityScore}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-gray-500 mb-1">Diversity</div>
                        <div className={`text-lg font-semibold ${getScoreColor(match.diversityScore).split(' ')[0]}`}>
                          {match.diversityScore}
                        </div>
                      </div>
                    </div>

                    {/* Specializations */}
                    <div className="mb-3">
                      <div className="text-xs font-medium text-gray-500 mb-2">Specializations:</div>
                      <div className="flex flex-wrap gap-2">
                        {match.specializations.map((spec, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                          >
                            {spec}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-4 w-4 mr-1" />
                        {match.recentReviews} recent reviews
                      </div>
                      <div className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        {match.avgReviewTime} days avg
                      </div>
                      <div className="flex items-center">
                        <StarIcon className="h-4 w-4 mr-1" />
                        {match.acceptanceRate}% acceptance rate
                      </div>
                      <div className="flex items-center">
                        <ChartBarIcon className="h-4 w-4 mr-1" />
                        {match.citationOverlap}% citation overlap
                      </div>
                    </div>

                    {/* AI Reasoning */}
                    {showDetails === match.userId && (
                      <div className="bg-purple-50 rounded-lg p-4 border border-purple-200 mb-3">
                        <p className="text-xs font-medium text-purple-900 mb-2">AI Reasoning:</p>
                        <p className="text-xs text-purple-800">{match.reasoning}</p>
                      </div>
                    )}

                    <button
                      onClick={() => setShowDetails(showDetails === match.userId ? null : match.userId)}
                      className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      {showDetails === match.userId ? 'Hide details' : 'Show AI reasoning'}
                    </button>
                  </div>

                  {/* Select Button */}
                  <div className="ml-4 flex-shrink-0">
                    <button
                      onClick={() => handleToggleReviewer(match.userId)}
                      className={`flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-200 ${
                        selectedReviewers.includes(match.userId)
                          ? 'bg-indigo-600 border-indigo-600 text-white'
                          : 'bg-white border-gray-300 text-gray-400 hover:border-indigo-500 hover:text-indigo-600'
                      }`}
                      title={selectedReviewers.includes(match.userId) ? 'Deselect' : 'Select'}
                    >
                      {selectedReviewers.includes(match.userId) ? (
                        <CheckCircleIcon className="h-6 w-6" />
                      ) : (
                        <UserIcon className="h-6 w-6" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No matches found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Unable to find suitable reviewers. Try adjusting the manuscript subject area.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewerMatching;
