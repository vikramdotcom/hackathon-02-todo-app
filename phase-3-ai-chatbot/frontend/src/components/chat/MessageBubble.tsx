/**
 * MessageBubble component - Displays a single chat message
 */

import React from 'react';
import { ChatMessage, TodoCard as TodoCardType } from '@/types/chat';
import TodoCard from './TodoCard';

interface MessageBubbleProps {
  message: ChatMessage;
  todos?: TodoCardType[];
}

export default function MessageBubble({ message, todos }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}
    >
      <div
        className={`max-w-[80%] ${
          isUser ? 'order-2' : 'order-1'
        }`}
      >
        {/* Message bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-none'
          }`}
        >
          {/* Message content */}
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>

          {/* Timestamp */}
          <div
            className={`text-xs mt-1 ${
              isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            {formatTimestamp(message.timestamp)}
          </div>
        </div>

        {/* Todo cards (if any) */}
        {todos && todos.length > 0 && (
          <div className="mt-2 space-y-2">
            {todos.map((todo) => (
              <TodoCard key={todo.id} todo={todo} />
            ))}
          </div>
        )}

        {/* Message metadata indicators */}
        {message.metadata?.message_type === 'confirmation_request' && (
          <div className="mt-2 text-xs text-orange-600 dark:text-orange-400 flex items-center gap-1">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <span>Confirmation required</span>
          </div>
        )}

        {message.metadata?.message_type === 'error' && (
          <div className="mt-2 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
            <svg
              className="w-4 h-4"
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
            <span>Error occurred</span>
          </div>
        )}
      </div>

      {/* Avatar */}
      <div
        className={`flex-shrink-0 ${
          isUser ? 'order-1 mr-2' : 'order-2 ml-2'
        }`}
      >
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200'
          }`}
        >
          {isUser ? 'U' : 'AI'}
        </div>
      </div>
    </div>
  );
}
