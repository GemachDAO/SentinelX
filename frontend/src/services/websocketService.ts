/**
 * WebSocket service for real-time updates from SentinelX backend
 */

export interface WebSocketMessage {
  type: string;
  timestamp: string;
  data?: any;
}

export interface ExecutionUpdate {
  execution_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  result?: any;
  error?: string;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private listeners: { [key: string]: ((data: any) => void)[] } = {};
  private isConnected = false;

  constructor() {
    this.connect();
  }

  private connect() {
    try {
      const wsUrl = (window as any).REACT_APP_WS_URL || 'ws://localhost:8000/ws/execution';
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connected', null);
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message received:', message);
          
          // Handle different message types
          switch (message.type) {
            case 'execution_update':
              this.emit('execution_update', message.data);
              break;
            case 'task_started':
              this.emit('task_started', message.data);
              break;
            case 'task_completed':
              this.emit('task_completed', message.data);
              break;
            case 'task_failed':
              this.emit('task_failed', message.data);
              break;
            case 'progress_update':
              this.emit('progress_update', message.data);
              break;
            case 'heartbeat':
              this.emit('heartbeat', message);
              break;
            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.emit('disconnected', null);
        this.handleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.handleReconnect();
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('max_reconnect_reached', null);
    }
  }

  public subscribe(event: string, callback: (data: any) => void) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);

    // Return unsubscribe function
    return () => {
      this.unsubscribe(event, callback);
    };
  }

  public unsubscribe(event: string, callback: (data: any) => void) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  private emit(event: string, data: any) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  public send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message);
    }
  }

  public disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public getConnectionStatus(): boolean {
    return this.isConnected;
  }

  // Heartbeat to keep connection alive
  public startHeartbeat(interval: number = 30000) {
    setInterval(() => {
      if (this.isConnected) {
        this.send({ type: 'ping', timestamp: new Date().toISOString() });
      }
    }, interval);
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();

// Auto-start heartbeat
websocketService.startHeartbeat();

export default websocketService;
