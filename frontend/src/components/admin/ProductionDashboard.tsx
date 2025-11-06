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
  WrenchScrewdriverIcon,
  DocumentCheckIcon,
  CubeIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';

interface ProductionAssignment {
  id: number;
  manuscript_id: number;
  manuscript_title: string;
  assigned_to_id: number;
  assigned_to_name: string;
  task_type: string;
  galley_format: string | null;
  galley_label: string | null;
  status: string;
  due_date: string | null;
  assigned_at: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
  source_file_id: number | null;
  output_file_id: number | null;
}

interface Statistics {
  total_assignments: number;
  pending_assignments: number;
  in_progress_assignments: number;
  completed_assignments: number;
  layout_assignments: number;
  proofreading_assignments: number;
  galley_assignments: number;
  overdue_assignments: number;
  average_completion_days: number | null;
}

interface Galley {
  id: number;
  manuscript_id: number;
  format: string;
  label: string;
  file_path: string;
  file_size: number;
  generated_at: string;
  version: number;
}

const ProductionDashboard: React.FC = () => {
  const [assignments, setAssignments] = useState<ProductionAssignment[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [taskTypeFilter, setTaskTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Selected assignment for detail view
  const [selectedAssignment, setSelectedAssignment] = useState<ProductionAssignment | null>(null);
  const [showDetail, setShowDetail] = useState(false);
  const [showGalleyGenerator, setShowGalleyGenerator] = useState(false);
  const [selectedManuscriptId, setSelectedManuscriptId] = useState<number | null>(null);

  // File upload
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  useEffect(() => {
    fetchAssignments();
    fetchStatistics();
  }, [taskTypeFilter, statusFilter, page, searchQuery]);

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      const params: any = { page, page_size: 20 };
      if (taskTypeFilter !== 'all') params.task_type = taskTypeFilter;
      if (statusFilter !== 'all') params.status_filter = statusFilter;
      if (searchQuery) params.search = searchQuery;

      const response = await apiService.production.list(params);
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
      const response = await apiService.production.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const handleFileUpload = async (assignmentId: number) => {
    if (!uploadFile) return;

    try {
      setUploadingFile(true);
      await apiService.production.uploadFile(assignmentId, uploadFile);
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

  const handleCompleteAssignment = async (assignmentId: number) => {
    try {
      await apiService.production.complete(assignmentId);
      fetchAssignments();
      fetchStatistics();
      alert('Assignment completed');
    } catch (error) {
      console.error('Failed to complete assignment:', error);
      alert('Failed to complete assignment');
    }
  };

  const handleGenerateGalley = async (manuscriptId: number, format: string) => {
    try {
      await apiService.production.generateGalley(manuscriptId, {
        format,
        include_metadata: true,
        include_references: true,
      });
      alert(`${format.toUpperCase()} galley generated successfully`);
      setShowGalleyGenerator(false);
    } catch (error) {
      console.error('Failed to generate galley:', error);
      alert('Failed to generate galley. Ensure pandoc is installed.');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getTaskTypeIcon = (taskType: string) => {
    switch (taskType) {
      case 'layout':
        return <WrenchScrewdriverIcon className="h-5 w-5" />;
      case 'proofreading':
        return <DocumentCheckIcon className="h-5 w-5" />;
      case 'galley_conversion':
        return <CubeIcon className="h-5 w-5" />;
      default:
        return <DocumentTextIcon className="h-5 w-5" />;
    }
  };

  const getTaskTypeColor = (taskType: string) => {
    const colors: Record<string, string> = {
      layout: 'bg-purple-100 text-purple-800',
      proofreading: 'bg-yellow-100 text-yellow-800',
      galley_conversion: 'bg-indigo-100 text-indigo-800',
    };
    return colors[taskType] || 'bg-gray-100 text-gray-800';
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
          <h1 className="text-3xl font-bold text-gray-900">Production Dashboard</h1>
          <p className="mt-2 text-gray-600">Manage layout, proofreading, and galley generation</p>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
                  <p className="text-sm font-medium text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold text-blue-600">{statistics.in_progress_assignments}</p>
                </div>
                <WrenchScrewdriverIcon className="h-8 w-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.completed_assignments}</p>
                </div>
                <CheckCircleIcon className="h-8 w-8 text-green-400" />
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

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-100">Layout</p>
                  <p className="text-2xl font-bold">{statistics.layout_assignments}</p>
                </div>
                <WrenchScrewdriverIcon className="h-8 w-8 text-purple-200" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-yellow-100">Proofreading</p>
                  <p className="text-2xl font-bold">{statistics.proofreading_assignments}</p>
                </div>
                <DocumentCheckIcon className="h-8 w-8 text-yellow-200" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-indigo-100">Galleys</p>
                  <p className="text-2xl font-bold">{statistics.galley_assignments}</p>
                </div>
                <CubeIcon className="h-8 w-8 text-indigo-200" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-100">Avg. Days</p>
                  <p className="text-2xl font-bold">
                    {statistics.average_completion_days?.toFixed(1) || 'N/A'}
                  </p>
                </div>
                <CalendarIcon className="h-8 w-8 text-green-200" />
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search manuscripts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Task Type Filter */}
            <div className="relative">
              <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={taskTypeFilter}
                onChange={(e) => setTaskTypeFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Task Types</option>
                <option value="layout">Layout</option>
                <option value="proofreading">Proofreading</option>
                <option value="galley_conversion">Galley Conversion</option>
              </select>
            </div>

            {/* Status Filter */}
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <button
              onClick={() => {
                setSearchQuery('');
                setTaskTypeFilter('all');
                setStatusFilter('all');
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="text-white">
              <h3 className="text-lg font-semibold flex items-center">
                <SparklesIcon className="h-6 w-6 mr-2" />
                Automated Galley Generation
              </h3>
              <p className="text-indigo-100 mt-1">
                Generate publication-ready files (PDF, HTML, EPUB, XML) with one click
              </p>
            </div>
            <button
              onClick={() => setShowGalleyGenerator(true)}
              className="px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-indigo-50 transition-colors"
            >
              Generate Galleys
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
                      Assigned To
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Task Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
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
                          <span className="text-sm text-gray-900">{assignment.assigned_to_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTaskTypeColor(assignment.task_type)}`}>
                          <span className="mr-1">{getTaskTypeIcon(assignment.task_type)}</span>
                          {assignment.task_type.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(assignment.status)}`}>
                          {assignment.status.replace(/_/g, ' ').toUpperCase()}
                        </span>
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

        {/* Galley Generator Modal */}
        {showGalleyGenerator && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Generate Galley Files</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Manuscript ID
                  </label>
                  <input
                    type="number"
                    value={selectedManuscriptId || ''}
                    onChange={(e) => setSelectedManuscriptId(parseInt(e.target.value))}
                    placeholder="Enter manuscript ID"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => selectedManuscriptId && handleGenerateGalley(selectedManuscriptId, 'pdf')}
                    disabled={!selectedManuscriptId}
                    className="px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 font-medium"
                  >
                    📕 PDF
                  </button>
                  <button
                    onClick={() => selectedManuscriptId && handleGenerateGalley(selectedManuscriptId, 'html')}
                    disabled={!selectedManuscriptId}
                    className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
                  >
                    🌐 HTML
                  </button>
                  <button
                    onClick={() => selectedManuscriptId && handleGenerateGalley(selectedManuscriptId, 'epub')}
                    disabled={!selectedManuscriptId}
                    className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 font-medium"
                  >
                    📱 EPUB
                  </button>
                  <button
                    onClick={() => selectedManuscriptId && handleGenerateGalley(selectedManuscriptId, 'xml')}
                    disabled={!selectedManuscriptId}
                    className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
                  >
                    📊 XML
                  </button>
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowGalleyGenerator(false);
                    setSelectedManuscriptId(null);
                  }}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductionDashboard;
