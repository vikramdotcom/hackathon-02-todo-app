/**
 * TypeScript types for chat functionality
 */

export interface ChatMessage {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  message_type?: 'text' | 'todo_display' | 'confirmation_request' | 'error';
  referenced_todos?: number[];
  tokens_used?: number;
}

export interface ConversationSession {
  session_id: string;
  user_id: number;
  created_at: string;
  last_activity_at: string;
  message_count: number;
  messages: ChatMessage[];
}

export interface ChatMessageRequest {
  session_id?: string;
  message: string;
}

export interface TodoCard {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  tags?: string[];
  due_date?: string;
}

export interface StreamEvent {
  type: 'token' | 'todo' | 'done' | 'error';
  content?: string;
  todo?: TodoCard;
  message_id?: string;
  error?: string;
}

export interface SessionSummary {
  session_id: string;
  created_at: string;
  last_activity_at: string;
  message_count: number;
  last_message_preview?: string;
}
