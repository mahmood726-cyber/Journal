import React, { useState, useEffect } from 'react';
import {
  ClockIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowUpTrayIcon,
  UserIcon,
  CalendarIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  PaperClipIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';

interface CopyeditingAssignment {
  id: number;
  manuscript_id: number;
  manuscript_title: string;
  copyeditor_id: number;
  copyeditor_name: string;
  status: string;
  due_date: string | null;
  assigned_at: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
  author_approved: boolean;
  original_file_id: number | null;
  copyedited_file_id: number | null;
}

interface Statistics {
  total_assignments: number;
  pending_assignments: number;
  in_progress_assignments: number;
  completed_assignments: number;
  awaiting_author_review: number;
  overdue_assignments: number;
  average_completion_days: number | null;
}

const CopyeditingDashboard: React.FC = () => {
  const [assignments, setAssignments] = useState<CopyeditingAssignment[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Selected assignment for detail view
  const [selectedAssignment, setSelectedAssignment] = useState<CopyeditingAssignment | null>(null);
  const [showDetail, setShowDetail] = useState(false);

  // File upload
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  useEffect(() => {
    fetchAssignments();
    fetchStatistics();
  }, [statusFilter, page, searchQuery]);

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      const params: any = { page, page_size: 20 };
      if (statusFilter !== 'all') params.status_filter = statusFilter;
      if (searchQuery) params.search = searchQuery;

      const response = await apiService.copyediting.list(params);
      setAssignments(response.data.assignments);
      setTotalPages(Math.ceil(response.data.total / 20));
    } catch (error) {
      console.error('Failed to fetch assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await apiService.copyediting.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const handleFileUpload = async (assignmentId: number) => {
    if (!uploadFile) return;

    try {
      setUploadingFile(true);
      await apiService.copyediting.uploadFile(assignmentId, uploadFile);
      fetchAssignments();
      setUploadFile(null);
      alert('File uploaded successfully');
    } catch (error) {
      console.error('Failed to upload file:', error);
      alert('Failed to upload file');
    } finally {
      setUploadingFile(false);
    }
  };

  const handleStartAssignment = async (assignmentId: number) => {
    try {
      await apiService.copyediting.start(assignmentId);
      fetchAssignments();
      fetchStatistics();
    } catch (error) {
      console.error('Failed to start assignment:', error);
      alert('Failed to start assignment');
    }
  };

  const handleRequestAuthorReview = async (assignmentId: number, notes: string) => {
    try {
      await apiService.copyediting.requestAuthorReview(assignmentId, { notes_to_author: notes });
      fetchAssignments();
      fetchStatistics();
      alert('Author review requested');
    } catch (error) {
      console.error('Failed to request author review:', error);
      alert('Failed to request author review');
    }
  };

  const handleCompleteAssignment = async (assignmentId: number) => {
    try {
      await apiService.copyediting.complete(assignmentId);
      fetchAssignments();
      fetchStatistics();
      alert('Assignment completed');
    } catch (error) {
      console.error('Failed to complete assignment:', error);
      alert('Failed to complete assignment');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      awaiting_author_review: 'bg-yellow-100 text-yellow-800',
      author_approved: 'bg-green-100 text-green-800',
      author_requested_changes: 'bg-orange-100 text-orange-800',
      completed: 'bg-emerald-100 text-emerald-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-5 w-5" />;
      case 'in_progress':
        return <DocumentTextIcon className="h-5 w-5" />;
      case 'awaiting_author_review':
        return <ChatBubbleLeftRightIcon className="h-5 w-5" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5" />;
      default:
        return <ClockIcon className="h-5 w-5" />;
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const isOverdue = (dueDate: string | null, status: string) => {
    if (!dueDate || status === 'completed') return false;
    return new Date(dueDate) < new Date();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Copyediting Dashboard</h1>
          <p className="mt-2 text-gray-600">Manage copyediting assignments and track progress</p>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.total_assignments}</p>
                </div>
                <DocumentTextIcon className="h-8 w-8 text-gray-400" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pending</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.pending_assignments}</p>
                </div>
                <ClockIcon className="h-8 w-8 text-gray-400" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold text-blue-600">{statistics.in_progress_assignments}</p>
                </div>
                <DocumentTextIcon className="h-8 w-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Awaiting Review</p>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.awaiting_author_review}</p>
                </div>
                <ChatBubbleLeftRightIcon className="h-8 w-8 text-yellow-400" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Overdue</p>
                  <p className="text-2xl font-bold text-red-600">{statistics.overdue_assignments}</p>
                </div>
                <XCircleIcon className="h-8 w-8 text-red-400" />
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search manuscripts or copyeditors..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <div className="relative">
              <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="awaiting_author_review">Awaiting Review</option>
                <option value="author_approved">Author Approved</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <button
              onClick={() => {
                setSearchQuery('');
                setStatusFilter('all');
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Assignments List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading assignments...</p>
            </div>
          ) : assignments.length === 0 ? (
            <div className="p-8 text-center">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-gray-600">No assignments found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Manuscript
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Copyeditor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Progress
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {assignments.map((assignment) => (
                    <tr key={assignment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {assignment.manuscript_title}
                            </div>
                            <div className="text-sm text-gray-500">
                              ID: {assignment.manuscript_id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <UserIcon className="h-5 w-5 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-900">{assignment.copyeditor_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(assignment.status)}`}>
                            <span className="mr-1">{getStatusIcon(assignment.status)}</span>
                            {assignment.status.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                          <span className={`text-sm ${isOverdue(assignment.due_date, assignment.status) ? 'text-red-600 font-semibold' : 'text-gray-900'}`}>
                            {formatDate(assignment.due_date)}
                            {isOverdue(assignment.due_date, assignment.status) && (
                              <span className="ml-1 text-red-600">⚠️</span>
                            )}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          {assignment.original_file_id && (
                            <span className="inline-flex items-center text-xs text-green-600">
                              <PaperClipIcon className="h-4 w-4 mr-1" /> Original
                            </span>
                          )}
                          {assignment.copyedited_file_id && (
                            <span className="inline-flex items-center text-xs text-blue-600">
                              <CheckCircleIcon className="h-4 w-4 mr-1" /> Copyedited
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => {
                            setSelectedAssignment(assignment);
                            setShowDetail(true);
                          }}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-gray-700">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </div>

        {/* Detail Modal (simplified - would need full implementation) */}
        {showDetail && selectedAssignment && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">Assignment Details</h2>
                  <button
                    onClick={() => setShowDetail(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{selectedAssignment.manuscript_title}</h3>
                    <p className="text-sm text-gray-600">Assigned to: {selectedAssignment.copyeditor_name}</p>
                  </div>

                  <div className="border-t pt-4">
                    <p className="text-sm font-medium text-gray-700">Status</p>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedAssignment.status)}`}>
                      {selectedAssignment.status.replace(/_/g, ' ').toUpperCase()}
                    </span>
                  </div>

                  {selectedAssignment.notes && (
                    <div className="border-t pt-4">
                      <p className="text-sm font-medium text-gray-700">Notes</p>
                      <p className="text-sm text-gray-600 mt-1">{selectedAssignment.notes}</p>
                    </div>
                  )}

                  <div className="border-t pt-4 flex space-x-4">
                    {selectedAssignment.status === 'pending' && (
                      <button
                        onClick={() => handleStartAssignment(selectedAssignment.id)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        Start Assignment
                      </button>
                    )}
                    {selectedAssignment.status === 'in_progress' && selectedAssignment.copyedited_file_id && (
                      <button
                        onClick={() => handleRequestAuthorReview(selectedAssignment.id, 'Please review the copyedited manuscript.')}
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                      >
                        Request Author Review
                      </button>
                    )}
                    {selectedAssignment.status === 'author_approved' && (
                      <button
                        onClick={() => handleCompleteAssignment(selectedAssignment.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        Complete Assignment
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CopyeditingDashboard;
