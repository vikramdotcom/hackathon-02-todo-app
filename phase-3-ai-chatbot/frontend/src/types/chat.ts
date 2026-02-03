/**
 * TypeScript interfaces for chat feature
 */

export interface Message {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  message_type?: 'text' | 'todo_display' | 'confirmation_request' | 'error';
  referenced_todos?: number[];
  function_call?: FunctionCall;
  tokens_used?: number;
}

export interface FunctionCall {
  function_name: string;
  arguments: Record<string, any>;
  result?: Record<string, any>;
  error?: string;
}

export interface ConversationSession {
  session_id: string;
  user_id: number;
  created_at: string;
  last_activity_at: string;
  message_count: number;
  messages: Message[];
  context: ConversationContext;
}

export interface ConversationContext {
  referenced_todos: Record<number, TodoReference>;
  last_query_results?: number[];
  pending_confirmation?: PendingConfirmation;
  user_preferences?: Record<string, any>;
}

export interface TodoReference {
  todo_id: number;
  title: string;
  completed: boolean;
  last_mentioned_at: string;
}

export interface PendingConfirmation {
  operation: 'delete' | 'bulk_delete' | 'bulk_update';
  target_todo_ids: number[];
  created_at: string;
  expires_at: string;
  operation_details?: Record<string, any>;
}

export interface ChatMessageRequest {
  session_id?: string;
  message: string;
}

export interface ChatMessageResponse {
  type: 'token' | 'function_call' | 'done' | 'error';
  content?: string;
  function_name?: string;
  arguments?: Record<string, any>;
  message_id?: string;
  error?: string;
}

export interface Todo {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}
