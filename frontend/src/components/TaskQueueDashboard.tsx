import React, { useState, useEffect } from 'react';
import {
  ClockIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CheckCircleIcon,
  PencilSquareIcon,
  BeakerIcon,
  RocketLaunchIcon,
  ChevronRightIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';

interface TaskCount {
  type: string;
  label: string;
  count: number;
  icon: React.ReactNode;
  color: string;
  urgent: boolean;
}

interface Manuscript {
  id: number;
  manuscript_id: string;
  title: string;
  submitter_name: string;
  status: string;
  stage: string;
  submitted_at: string;
  due_date: string | null;
  days_in_stage: number;
}

const TaskQueueDashboard: React.FC = () => {
  const [taskCounts, setTaskCounts] = useState<TaskCount[]>([]);
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [manuscripts, setManuscripts] = useState<Manuscript[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchTaskCounts();
  }, []);

  useEffect(() => {
    if (selectedTask) {
      fetchManuscriptsForTask(selectedTask);
    }
  }, [selectedTask, searchQuery]);

  const fetchTaskCounts = async () => {
    try {
      setLoading(true);

      // Fetch counts from various endpoints
      const [submissionResponse, reviewResponse, copyeditingResponse, productionResponse] = await Promise.all([
        apiService.manuscripts.list({ status: 'submitted', page_size: 1 }),
        apiService.manuscripts.list({ status: 'under_review', page_size: 1 }),
        apiService.copyediting.list({ status_filter: 'pending', page_size: 1 }),
        apiService.production.list({ status_filter: 'pending', page_size: 1 }),
      ]);

      const tasks: TaskCount[] = [
        {
          type: 'desk_review',
          label: 'Desk Review Needed',
          count: submissionResponse.data.total || 0,
          icon: <DocumentTextIcon className="h-6 w-6" />,
          color: 'from-blue-500 to-blue-600',
          urgent: true,
        },
        {
          type: 'assign_reviewers',
          label: 'Reviewers to Assign',
          count: reviewResponse.data.total || 0,
          icon: <UserGroupIcon className="h-6 w-6" />,
          color: 'from-purple-500 to-purple-600',
          urgent: true,
        },
        {
          type: 'decision_needed',
          label: 'Decision Required',
          count: 0, // Would need specific endpoint
          icon: <CheckCircleIcon className="h-6 w-6" />,
          color: 'from-red-500 to-red-600',
          urgent: true,
        },
        {
          type: 'copyediting_review',
          label: 'Copyediting to Review',
          count: copyeditingResponse.data.total || 0,
          icon: <PencilSquareIcon className="h-6 w-6" />,
          color: 'from-yellow-500 to-yellow-600',
          urgent: false,
        },
        {
          type: 'production_pending',
          label: 'Production Tasks',
          count: productionResponse.data.total || 0,
          icon: <BeakerIcon className="h-6 w-6" />,
          color: 'from-green-500 to-green-600',
          urgent: false,
        },
        {
          type: 'ready_to_publish',
          label: 'Ready to Publish',
          count: 0, // Would need specific endpoint
          icon: <RocketLaunchIcon className="h-6 w-6" />,
          color: 'from-indigo-500 to-indigo-600',
          urgent: false,
        },
      ];

      setTaskCounts(tasks);
    } catch (error) {
      console.error('Failed to fetch task counts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchManuscriptsForTask = async (taskType: string) => {
    try {
      setLoading(true);
      let response;

      switch (taskType) {
        case 'desk_review':
          response = await apiService.manuscripts.list({
            status: 'submitted',
            search: searchQuery,
            page_size: 50,
          });
          break;
        case 'assign_reviewers':
          response = await apiService.manuscripts.list({
            status: 'under_review',
            search: searchQuery,
            page_size: 50,
          });
          break;
        case 'copyediting_review':
          const copyResponse = await apiService.copyediting.list({
            status_filter: 'pending',
            search: searchQuery,
            page_size: 50,
          });
          // Transform copyediting assignments to manuscript format
          setManuscripts(copyResponse.data.assignments.map((a: any) => ({
            id: a.manuscript_id,
            manuscript_id: a.manuscript_id,
            title: a.manuscript_title,
            submitter_name: a.copyeditor_name,
            status: a.status,
            stage: 'copyediting',
            submitted_at: a.assigned_at,
            due_date: a.due_date,
            days_in_stage: a.assigned_at ? Math.floor((new Date().getTime() - new Date(a.assigned_at).getTime()) / (1000 * 60 * 60 * 24)) : 0,
          })));
          setLoading(false);
          return;
        default:
          response = await apiService.manuscripts.list({
            search: searchQuery,
            page_size: 50,
          });
      }

      setManuscripts(response.data || []);
    } catch (error) {
      console.error('Failed to fetch manuscripts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTotalUrgentTasks = () => {
    return taskCounts.filter(t => t.urgent).reduce((sum, t) => sum + t.count, 0);
  };

  const formatDaysInStage = (days: number) => {
    if (days === 0) return 'Today';
    if (days === 1) return '1 day';
    return `${days} days`;
  };

  const getUrgencyColor = (daysInStage: number) => {
    if (daysInStage > 14) return 'text-red-600';
    if (daysInStage > 7) return 'text-orange-600';
    return 'text-gray-600';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Task Queue Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Complete editorial tasks efficiently with smart prioritization
          </p>
        </div>

        {/* Needs Action Summary */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-xl p-8 mb-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3">
                <ClockIcon className="h-10 w-10" />
                <div>
                  <p className="text-blue-100 text-sm font-medium">NEEDS IMMEDIATE ATTENTION</p>
                  <p className="text-4xl font-bold mt-1">{getTotalUrgentTasks()}</p>
                  <p className="text-blue-100 text-sm mt-1">urgent tasks require your action</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-5xl font-bold opacity-20">{getTotalUrgentTasks()}</p>
            </div>
          </div>
        </div>

        {/* Task Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {loading ? (
            <div className="col-span-3 text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : (
            taskCounts.map((task) => (
              <button
                key={task.type}
                onClick={() => setSelectedTask(task.type === selectedTask ? null : task.type)}
                className={`group relative overflow-hidden rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105 ${
                  selectedTask === task.type ? 'ring-4 ring-blue-500' : ''
                }`}
              >
                <div className={`bg-gradient-to-br ${task.color} p-6 text-white`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                      {task.icon}
                    </div>
                    {task.urgent && task.count > 0 && (
                      <span className="px-3 py-1 bg-red-500 bg-opacity-90 rounded-full text-xs font-bold uppercase animate-pulse">
                        Urgent
                      </span>
                    )}
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium opacity-90">{task.label}</p>
                    <div className="flex items-baseline space-x-2">
                      <p className="text-4xl font-bold">{task.count}</p>
                      <p className="text-sm opacity-75">
                        {task.count === 1 ? 'item' : 'items'}
                      </p>
                    </div>
                  </div>

                  {task.count > 0 && (
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-sm font-medium opacity-90">
                        Click to view queue →
                      </span>
                      <ChevronRightIcon className="h-5 w-5 transform group-hover:translate-x-1 transition-transform" />
                    </div>
                  )}
                </div>

                {/* Progress indicator at bottom */}
                {task.count > 0 && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-white bg-opacity-30">
                    <div
                      className="h-full bg-white"
                      style={{ width: `${Math.min(task.count * 10, 100)}%` }}
                    ></div>
                  </div>
                )}
              </button>
            ))
          )}
        </div>

        {/* Selected Task Queue */}
        {selectedTask && (
          <div className="bg-white rounded-lg shadow-xl overflow-hidden">
            {/* Queue Header */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    {taskCounts.find(t => t.type === selectedTask)?.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">
                      {taskCounts.find(t => t.type === selectedTask)?.label}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {manuscripts.length} {manuscripts.length === 1 ? 'item' : 'items'} in queue
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedTask(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              {/* Search */}
              <div className="mt-4 relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search in this queue..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Queue Items */}
            <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
              {manuscripts.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No items in this queue
                </div>
              ) : (
                manuscripts.map((manuscript, index) => (
                  <div
                    key={manuscript.id}
                    className="p-6 hover:bg-gray-50 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-800 text-sm font-bold">
                            {index + 1}
                          </span>
                          <h4 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                            {manuscript.title}
                          </h4>
                        </div>

                        <div className="ml-11 space-y-1">
                          <p className="text-sm text-gray-600">
                            ID: {manuscript.manuscript_id} • {manuscript.submitter_name}
                          </p>
                          <div className="flex items-center space-x-4 text-sm">
                            <span className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded">
                              {manuscript.status.replace(/_/g, ' ').toUpperCase()}
                            </span>
                            <span className={getUrgencyColor(manuscript.days_in_stage)}>
                              In queue: {formatDaysInStage(manuscript.days_in_stage)}
                            </span>
                            {manuscript.due_date && (
                              <span className="text-gray-500">
                                Due: {new Date(manuscript.due_date).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 opacity-0 group-hover:opacity-100 transition-opacity font-medium">
                        Take Action →
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Queue Footer */}
            {manuscripts.length > 0 && (
              <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    Showing {manuscripts.length} {manuscripts.length === 1 ? 'item' : 'items'}
                  </p>
                  <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                    View All Manuscripts →
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Help Text */}
        {!selectedTask && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-blue-900 mb-1">
                  How to use Task Queues
                </h3>
                <p className="text-sm text-blue-800">
                  Click on any task card above to see the full queue. Work through items one by one.
                  The system will automatically advance to the next item when you complete an action.
                  Focus on urgent tasks (marked in red) first for optimal workflow.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskQueueDashboard;
