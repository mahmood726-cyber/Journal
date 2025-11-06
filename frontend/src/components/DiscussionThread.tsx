import React, { useState, useEffect } from 'react';
import {
  ChatBubbleLeftRightIcon,
  PaperClipIcon,
  PaperAirplaneIcon,
  XMarkIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';

interface DiscussionMessage {
  id: number;
  discussion_id: number;
  user_id: number;
  user_name: string;
  user_role: string;
  message: string;
  attachments: Array<{
    id: number;
    name: string;
    size: number;
    type: string;
  }>;
  created_at: string;
}

interface Participant {
  user_id: number;
  name: string;
  role: string;
}

interface Discussion {
  id: number;
  manuscript_id: number;
  manuscript_title: string;
  stage: string;
  subject: string;
  created_by_id: number;
  created_by_name: string;
  status: string;
  message_count: number;
  last_message_at: string | null;
  created_at: string;
  participants: Participant[];
  messages?: DiscussionMessage[];
}

interface DiscussionThreadProps {
  discussionId: number;
  onClose?: () => void;
  showHeader?: boolean;
}

const DiscussionThread: React.FC<DiscussionThreadProps> = ({
  discussionId,
  onClose,
  showHeader = true,
}) => {
  const [discussion, setDiscussion] = useState<Discussion | null>(null);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchDiscussion();
  }, [discussionId]);

  const fetchDiscussion = async () => {
    try {
      setLoading(true);
      const response = await apiService.discussions.get(discussionId);
      setDiscussion(response.data);
    } catch (error) {
      console.error('Failed to fetch discussion:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    try {
      setSending(true);
      await apiService.discussions.addMessage(discussionId, {
        message: newMessage,
        file_ids: [],
      });
      setNewMessage('');
      await fetchDiscussion(); // Refresh to show new message
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      editor_in_chief: 'bg-purple-100 text-purple-800',
      associate_editor: 'bg-indigo-100 text-indigo-800',
      author: 'bg-blue-100 text-blue-800',
      reviewer: 'bg-green-100 text-green-800',
      copyeditor: 'bg-yellow-100 text-yellow-800',
      layout_editor: 'bg-orange-100 text-orange-800',
      proofreader: 'bg-pink-100 text-pink-800',
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!discussion) {
    return (
      <div className="p-8 text-center text-gray-600">Discussion not found</div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      {showHeader && (
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <ChatBubbleLeftRightIcon className="h-5 w-5 text-gray-400" />
              <h3 className="text-lg font-semibold text-gray-900">{discussion.subject}</h3>
            </div>
            <div className="mt-1 flex items-center space-x-2 text-sm text-gray-600">
              <span className="capitalize">{discussion.stage.replace(/_/g, ' ')}</span>
              <span>•</span>
              <span>{discussion.participants.length} participants</span>
              <span>•</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                discussion.status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {discussion.status}
              </span>
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="ml-4 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      )}

      {/* Participants */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          <UserCircleIcon className="h-5 w-5 text-gray-400" />
          <span className="text-sm font-medium text-gray-700">Participants:</span>
          <div className="flex flex-wrap gap-2">
            {discussion.participants.map((participant) => (
              <span
                key={participant.user_id}
                className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getRoleBadgeColor(participant.role)}`}
              >
                {participant.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {discussion.messages && discussion.messages.length > 0 ? (
          discussion.messages.map((message) => (
            <div key={message.id} className="flex space-x-3">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
                  {message.user_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                </div>
              </div>

              {/* Message Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline space-x-2">
                  <span className="text-sm font-semibold text-gray-900">{message.user_name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${getRoleBadgeColor(message.user_role)}`}>
                    {message.user_role.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs text-gray-500">{formatDate(message.created_at)}</span>
                </div>

                <div className="mt-1 text-sm text-gray-700 whitespace-pre-wrap break-words">
                  {message.message}
                </div>

                {/* Attachments */}
                {message.attachments && message.attachments.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.attachments.map((attachment) => (
                      <div
                        key={attachment.id}
                        className="inline-flex items-center space-x-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm hover:bg-gray-100"
                      >
                        <PaperClipIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-700">{attachment.name}</span>
                        <span className="text-gray-500">({formatFileSize(attachment.size)})</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500 py-8">No messages yet</div>
        )}
      </div>

      {/* Message Input */}
      {discussion.status === 'active' && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex space-x-3">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
              rows={3}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={sending}
            />
            <div className="flex flex-col space-y-2">
              <button
                onClick={handleSendMessage}
                disabled={!newMessage.trim() || sending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
                <span>Send</span>
              </button>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Tip: All participants will receive an email notification
          </div>
        </div>
      )}

      {discussion.status === 'closed' && (
        <div className="border-t border-gray-200 p-4 bg-gray-100 text-center text-sm text-gray-600">
          This discussion is closed. No new messages can be added.
        </div>
      )}
    </div>
  );
};

export default DiscussionThread;
