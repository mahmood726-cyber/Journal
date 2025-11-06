import React, { useState, useEffect } from 'react';
import {
  UserGroupIcon,
  PlusIcon,
  XMarkIcon,
  EnvelopeIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';

interface Participant {
  user_id: number;
  user_name: string;
  user_email: string;
  role: string;
  stage: string | null;
  added_at: string | null;
}

interface ParticipantsPanelProps {
  manuscriptId: number;
  isEditor?: boolean;
  onParticipantAdded?: () => void;
}

const ParticipantsPanel: React.FC<ParticipantsPanelProps> = ({
  manuscriptId,
  isEditor = false,
  onParticipantAdded,
}) => {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newParticipant, setNewParticipant] = useState({
    user_id: '',
    role: 'reviewer',
    stage: '',
  });

  useEffect(() => {
    fetchParticipants();
  }, [manuscriptId]);

  const fetchParticipants = async () => {
    try {
      setLoading(true);
      const response = await apiService.manuscripts.getParticipants(manuscriptId);
      setParticipants(response.data.participants || []);
    } catch (error) {
      console.error('Failed to fetch participants:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddParticipant = async () => {
    if (!newParticipant.user_id || !newParticipant.role) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      await apiService.manuscripts.addParticipant(manuscriptId, {
        user_id: parseInt(newParticipant.user_id),
        role: newParticipant.role,
        stage: newParticipant.stage || undefined,
      });

      setShowAddModal(false);
      setNewParticipant({ user_id: '', role: 'reviewer', stage: '' });
      await fetchParticipants();

      if (onParticipantAdded) {
        onParticipantAdded();
      }
    } catch (error: any) {
      console.error('Failed to add participant:', error);
      alert(error.response?.data?.detail || 'Failed to add participant');
    }
  };

  const handleRemoveParticipant = async (userId: number, role: string) => {
    if (!confirm(`Remove this participant (${role})?`)) return;

    try {
      await apiService.manuscripts.removeParticipant(manuscriptId, userId, role);
      await fetchParticipants();
    } catch (error) {
      console.error('Failed to remove participant:', error);
      alert('Failed to remove participant');
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: { [key: string]: string } = {
      author: 'bg-blue-100 text-blue-800',
      editor: 'bg-purple-100 text-purple-800',
      reviewer: 'bg-green-100 text-green-800',
      copyeditor: 'bg-yellow-100 text-yellow-800',
      production_staff: 'bg-orange-100 text-orange-800',
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  const getStageBadgeColor = (stage: string | null) => {
    if (!stage) return 'bg-gray-100 text-gray-600';

    const colors: { [key: string]: string } = {
      submission: 'bg-blue-100 text-blue-700',
      review: 'bg-purple-100 text-purple-700',
      copyediting: 'bg-yellow-100 text-yellow-700',
      production: 'bg-green-100 text-green-700',
    };
    return colors[stage] || 'bg-gray-100 text-gray-700';
  };

  const formatRole = (role: string) => {
    return role.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const formatStage = (stage: string | null) => {
    if (!stage) return 'All Stages';
    return stage.charAt(0).toUpperCase() + stage.slice(1);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getInitials = (name: string) => {
    const names = name.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Group participants by role
  const groupedParticipants = participants.reduce((acc, participant) => {
    if (!acc[participant.role]) {
      acc[participant.role] = [];
    }
    acc[participant.role].push(participant);
    return acc;
  }, {} as { [key: string]: Participant[] });

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <UserGroupIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">Participants</h3>
              <p className="text-sm text-gray-600">
                {participants.length} {participants.length === 1 ? 'person' : 'people'} involved
              </p>
            </div>
          </div>

          {isEditor && (
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <PlusIcon className="h-5 w-5" />
              <span>Add Participant</span>
            </button>
          )}
        </div>
      </div>

      {/* Participants List */}
      <div className="p-6 space-y-6">
        {participants.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <UserGroupIcon className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p>No participants added yet</p>
          </div>
        ) : (
          Object.entries(groupedParticipants).map(([role, roleParticipants]) => (
            <div key={role} className="space-y-3">
              {/* Role Section Header */}
              <div className="flex items-center space-x-2 pb-2 border-b border-gray-200">
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRoleBadgeColor(role)}`}>
                  {formatRole(role)}
                </span>
                <span className="text-sm text-gray-500">
                  {roleParticipants.length} {roleParticipants.length === 1 ? 'person' : 'people'}
                </span>
              </div>

              {/* Participants in this role */}
              {roleParticipants.map((participant) => (
                <div
                  key={`${participant.user_id}-${participant.role}`}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
                >
                  <div className="flex items-center space-x-4">
                    {/* Avatar */}
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                        {getInitials(participant.user_name)}
                      </div>
                    </div>

                    {/* Info */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900">
                        {participant.user_name}
                      </h4>
                      <div className="flex items-center space-x-2 mt-1">
                        <EnvelopeIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{participant.user_email}</span>
                      </div>
                      <div className="flex items-center space-x-3 mt-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStageBadgeColor(participant.stage)}`}>
                          {formatStage(participant.stage)}
                        </span>
                        <span className="text-xs text-gray-500">
                          Added {formatDate(participant.added_at)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Remove Button */}
                  {isEditor && (
                    <button
                      onClick={() => handleRemoveParticipant(participant.user_id, participant.role)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      title="Remove participant"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          ))
        )}
      </div>

      {/* Add Participant Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Add Participant</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              {/* User ID Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={newParticipant.user_id}
                  onChange={(e) => setNewParticipant({ ...newParticipant, user_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter user ID"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Enter the ID of the user you want to add as a participant
                </p>
              </div>

              {/* Role Select */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Role <span className="text-red-500">*</span>
                </label>
                <select
                  value={newParticipant.role}
                  onChange={(e) => setNewParticipant({ ...newParticipant, role: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="author">Author</option>
                  <option value="editor">Editor</option>
                  <option value="reviewer">Reviewer</option>
                  <option value="copyeditor">Copyeditor</option>
                  <option value="production_staff">Production Staff</option>
                </select>
              </div>

              {/* Stage Select */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stage (Optional)
                </label>
                <select
                  value={newParticipant.stage}
                  onChange={(e) => setNewParticipant({ ...newParticipant, stage: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Stages</option>
                  <option value="submission">Submission</option>
                  <option value="review">Review</option>
                  <option value="copyediting">Copyediting</option>
                  <option value="production">Production</option>
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Leave empty to add participant for all stages
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end space-x-3 px-6 py-4 bg-gray-50 rounded-b-lg">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddParticipant}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add Participant
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParticipantsPanel;
