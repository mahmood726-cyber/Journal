import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  DocumentTextIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PencilIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';
import { api } from '../../services/api';

interface Manuscript {
  id: number;
  manuscriptId: string;
  title: string;
  status: string;
  submittedAt: string;
  updatedAt: string;
  authors: string;
  subject: string;
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  submitted: 'bg-blue-100 text-blue-800',
  'under-review': 'bg-yellow-100 text-yellow-800',
  'needs-revision': 'bg-orange-100 text-orange-800',
  accepted: 'bg-green-100 text-green-800',
  published: 'bg-indigo-100 text-indigo-800',
  rejected: 'bg-red-100 text-red-800',
};

const statusIcons: Record<string, React.ComponentType<any>> = {
  draft: PencilIcon,
  submitted: ClockIcon,
  'under-review': ClockIcon,
  'needs-revision': PencilIcon,
  accepted: CheckCircleIcon,
  published: CheckCircleIcon,
  rejected: XCircleIcon,
};

const ManuscriptList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('updated');

  const { data: manuscripts, isLoading } = useQuery<Manuscript[]>(
    ['manuscripts', statusFilter, sortBy],
    () =>
      api
        .get('/manuscripts', {
          params: { status: statusFilter !== 'all' ? statusFilter : undefined, sort: sortBy },
        })
        .then((res) => res.data),
    { initialData: [] }
  );

  const filteredManuscripts = manuscripts?.filter((manuscript) =>
    manuscript.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const statuses = [
    { value: 'all', label: 'All Manuscripts', count: manuscripts?.length || 0 },
    { value: 'draft', label: 'Drafts', count: manuscripts?.filter((m) => m.status === 'draft').length || 0 },
    { value: 'submitted', label: 'Submitted', count: manuscripts?.filter((m) => m.status === 'submitted').length || 0 },
    { value: 'under-review', label: 'Under Review', count: manuscripts?.filter((m) => m.status === 'under-review').length || 0 },
    { value: 'needs-revision', label: 'Needs Revision', count: manuscripts?.filter((m) => m.status === 'needs-revision').length || 0 },
    { value: 'accepted', label: 'Accepted', count: manuscripts?.filter((m) => m.status === 'accepted').length || 0 },
    { value: 'published', label: 'Published', count: manuscripts?.filter((m) => m.status === 'published').length || 0 },
    { value: 'rejected', label: 'Rejected', count: manuscripts?.filter((m) => m.status === 'rejected').length || 0 },
  ];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
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
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">My Manuscripts</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage and track all your manuscript submissions
            </p>
          </div>
          <div className="mt-4 md:mt-0">
            <Link
              to="/dashboard/manuscripts/submit"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              New Submission
            </Link>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search manuscripts by title..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Sort */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="updated">Recently Updated</option>
              <option value="submitted">Recently Submitted</option>
              <option value="title">Title (A-Z)</option>
              <option value="status">Status</option>
            </select>
          </div>
        </div>

        {/* Status Tabs */}
        <div className="mt-6 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 overflow-x-auto" aria-label="Status filters">
            {statuses.map((status) => (
              <button
                key={status.value}
                onClick={() => setStatusFilter(status.value)}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-150
                  ${
                    statusFilter === status.value
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {status.label}
                <span
                  className={`ml-2 py-0.5 px-2 rounded-full text-xs font-medium ${
                    statusFilter === status.value
                      ? 'bg-indigo-100 text-indigo-600'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  {status.count}
                </span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Manuscripts List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {filteredManuscripts && filteredManuscripts.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Manuscript
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Authors
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Status
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Submitted
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Last Updated
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredManuscripts.map((manuscript) => {
                  const StatusIcon = statusIcons[manuscript.status] || DocumentTextIcon;
                  return (
                    <tr
                      key={manuscript.id}
                      className="hover:bg-gray-50 transition-colors duration-150"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-start">
                          <div className="flex-shrink-0">
                            <DocumentTextIcon className="h-6 w-6 text-indigo-600" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900 max-w-md">
                              {manuscript.title}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              ID: {manuscript.manuscriptId}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {manuscript.subject}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{manuscript.authors}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            statusColors[manuscript.status]
                          }`}
                        >
                          <StatusIcon className="h-4 w-4 mr-1" />
                          {manuscript.status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(manuscript.submittedAt)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(manuscript.updatedAt)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Link
                          to={`/dashboard/manuscripts/${manuscript.id}`}
                          className="text-indigo-600 hover:text-indigo-900 flex items-center justify-end"
                        >
                          <EyeIcon className="h-4 w-4 mr-1" />
                          View
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12 px-4">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {searchQuery ? 'No manuscripts found' : 'No manuscripts yet'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchQuery
                ? 'Try adjusting your search or filter criteria'
                : 'Get started by submitting your first manuscript'}
            </p>
            {!searchQuery && (
              <div className="mt-6">
                <Link
                  to="/dashboard/manuscripts/submit"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  <DocumentTextIcon className="h-5 w-5 mr-2" />
                  Submit Manuscript
                </Link>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Pagination (placeholder) */}
      {filteredManuscripts && filteredManuscripts.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing <span className="font-medium">{filteredManuscripts.length}</span> manuscript
              {filteredManuscripts.length !== 1 ? 's' : ''}
            </div>
            {/* Add pagination controls here if needed */}
          </div>
        </div>
      )}
    </div>
  );
};

export default ManuscriptList;
