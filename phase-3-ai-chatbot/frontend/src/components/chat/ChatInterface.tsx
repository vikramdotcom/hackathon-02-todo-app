/**
 * ChatInterface component - Main chat interface with streaming support
 */

'use client';

import React, { useState, useEffect } from 'react';
import { ChatMessage, TodoCard as TodoCardType, StreamEvent } from '@/types/chat';
import MessageList from './MessageList';
import InputBox from './InputBox';

interface ChatInterfaceProps {
  apiBaseUrl?: string;
  onError?: (error: string) => void;
}

export default function ChatInterface({
  apiBaseUrl = '/api/v1',
  onError,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [todosMap, setTodosMap] = useState<Map<string, TodoCardType[]>>(new Map());
  const [error, setError] = useState<string | null>(null);

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem('chat_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
      // Optionally load session history from backend
      loadSessionHistory(savedSessionId);
    }
  }, []);

  // Save session to localStorage when it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('chat_session_id', sessionId);
    }
  }, [sessionId]);

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const token = getAuthToken();
      if (!token) return;

      const response = await fetch(`${apiBaseUrl}/chat/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const session = await response.json();
        setMessages(session.messages || []);
      }
    } catch (err) {
      console.error('Failed to load session history:', err);
    }
  };

  const getAuthToken = (): string | null => {
    // Get JWT token from localStorage or cookie
    // This should match your Phase II authentication implementation
    return localStorage.getItem('auth_token') || null;
  };

  const handleSendMessage = async (messageText: string) => {
    const token = getAuthToken();
    if (!token) {
      const errorMsg = 'Please log in to use the chat';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      message_id: `temp-${Date.now()}`,
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Send message to backend with streaming
      const response = await fetch(`${apiBaseUrl}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageText,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get session_id from response header
      const newSessionId = response.headers.get('X-Session-Id');
      if (newSessionId && newSessionId !== sessionId) {
        setSessionId(newSessionId);
      }

      // Process streaming response
      await processStreamingResponse(response);

    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMsg);
      onError?.(errorMsg);
      console.error('Error sending message:', err);

      // Add error message to chat
      const errorMessage: ChatMessage = {
        message_id: `error-${Date.now()}`,
        role: 'assistant',
        content: `I'm sorry, I encountered an error: ${errorMsg}`,
        timestamp: new Date().toISOString(),
        metadata: {
          message_type: 'error',
        },
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const processStreamingResponse = async (response: Response) => {
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let assistantMessageContent = '';
    let currentMessageId = '';
    const currentTodos: TodoCardType[] = [];

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamEvent = JSON.parse(line.slice(6));

              switch (data.type) {
                case 'session_id':
                  // Update session_id if provided
                  if ('session_id' in data && data.session_id) {
                    setSessionId(data.session_id);
                  }
                  break;

                case 'token':
                  // Accumulate text tokens
                  if (data.content) {
                    assistantMessageContent += data.content;

                    // Update message in real-time
                    setMessages((prev) => {
                      const lastMessage = prev[prev.length - 1];
                      if (lastMessage && lastMessage.role === 'assistant' && !currentMessageId) {
                        // Update existing assistant message
                        return [
                          ...prev.slice(0, -1),
                          { ...lastMessage, content: assistantMessageContent },
                        ];
                      } else {
                        // Create new assistant message
                        const newMessage: ChatMessage = {
                          message_id: `streaming-${Date.now()}`,
                          role: 'assistant',
                          content: assistantMessageContent,
                          timestamp: new Date().toISOString(),
                        };
                        return [...prev, newMessage];
                      }
                    });
                  }
                  break;

                case 'todo':
                  // Add todo to current message
                  if (data.todo) {
                    currentTodos.push(data.todo);
                  }
                  break;

                case 'done':
                  // Response complete
                  if ('message_id' in data && data.message_id) {
                    currentMessageId = data.message_id;

                    // Update final message with correct ID
                    setMessages((prev) => {
                      const lastMessage = prev[prev.length - 1];
                      if (lastMessage && lastMessage.role === 'assistant') {
                        return [
                          ...prev.slice(0, -1),
                          {
                            ...lastMessage,
                            message_id: currentMessageId,
                            content: assistantMessageContent || lastMessage.content,
                          },
                        ];
                      }
                      return prev;
                    });

                    // Store todos for this message
                    if (currentTodos.length > 0) {
                      setTodosMap((prev) => {
                        const newMap = new Map(prev);
                        newMap.set(currentMessageId, [...currentTodos]);
                        return newMap;
                      });
                    }
                  }
                  break;

                case 'error':
                  // Handle error
                  if (data.error) {
                    throw new Error(data.error);
                  }
                  break;
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to start a new conversation?')) {
      setMessages([]);
      setTodosMap(new Map());
      setSessionId(null);
      localStorage.removeItem('chat_session_id');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Todo Assistant</h1>
            <p className="text-sm text-gray-500">
              {sessionId ? `Session active` : 'Start a conversation'}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {sessionId && (
            <button
              onClick={handleClearChat}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Start new conversation"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-800">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-sm">{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}

      {/* Messages */}
      <MessageList
        messages={messages}
        todosMap={todosMap}
        isLoading={isLoading}
      />

      {/* Input */}
      <InputBox
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        placeholder="Ask me to help with your todos..."
      />
    </div>
  );
}
