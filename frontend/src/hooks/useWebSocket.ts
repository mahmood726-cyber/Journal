/**
 * WebSocket hook for real-time updates.
 *
 * Features:
 * - Automatic connection/reconnection
 * - Authentication with JWT token
 * - Message queuing when disconnected
 * - Event listeners for different notification types
 * - Ping/pong keep-alive
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface WebSocketMessage {
  type: 'manuscript_status' | 'new_review' | 'editor_decision' | 'deadline_reminder' | 'system_announcement';
  data: any;
  timestamp: string;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

interface WebSocketHookReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: any) => void;
  connect: () => void;
  disconnect: () => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): WebSocketHookReturn => {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options;

  const { user, token } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<any[]>([]);

  const connect = useCallback(() => {
    if (!user || !token) {
      console.log('[WS] No user or token, skipping connection');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[WS] Already connected');
      return;
    }

    try {
      // Determine WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = import.meta.env.VITE_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000';
      const wsUrl = `${protocol}//${host}/api/v1/ws/${user.id}?token=${token}`;

      console.log('[WS] Connecting to WebSocket...');
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[WS] Connected');
        setIsConnected(true);
        onConnect?.();

        // Send any queued messages
        while (messageQueueRef.current.length > 0) {
          const message = messageQueueRef.current.shift();
          ws.send(JSON.stringify(message));
        }

        // Start ping/pong keep-alive (every 30 seconds)
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        if (event.data === 'pong') {
          return; // Ignore pong responses
        }

        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('[WS] Message received:', message);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error('[WS] Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[WS] Error:', error);
      };

      ws.onclose = (event) => {
        console.log('[WS] Disconnected:', event.code, event.reason);
        setIsConnected(false);
        onDisconnect?.();

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Auto-reconnect if enabled
        if (autoReconnect && !event.wasClean) {
          console.log(`[WS] Reconnecting in ${reconnectInterval}ms...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('[WS] Connection failed:', error);
    }
  }, [user, token, autoReconnect, reconnectInterval, onConnect, onDisconnect, onMessage]);

  const disconnect = useCallback(() => {
    console.log('[WS] Disconnecting...');

    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Clear ping interval
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.log('[WS] Not connected, queuing message');
      messageQueueRef.current.push(message);
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
  };
};

/**
 * Simplified hook for specific notification types.
 */
export const useNotifications = (
  onManuscriptStatus?: (data: any) => void,
  onNewReview?: (data: any) => void,
  onEditorDecision?: (data: any) => void,
  onDeadlineReminder?: (data: any) => void,
  onSystemAnnouncement?: (data: any) => void
) => {
  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'manuscript_status':
        onManuscriptStatus?.(message.data);
        break;
      case 'new_review':
        onNewReview?.(message.data);
        break;
      case 'editor_decision':
        onEditorDecision?.(message.data);
        break;
      case 'deadline_reminder':
        onDeadlineReminder?.(message.data);
        break;
      case 'system_announcement':
        onSystemAnnouncement?.(message.data);
        break;
    }
  }, [onManuscriptStatus, onNewReview, onEditorDecision, onDeadlineReminder, onSystemAnnouncement]);

  return useWebSocket({
    onMessage: handleMessage,
  });
};
