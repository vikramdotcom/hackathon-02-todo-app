/**
 * MessageList component - Displays conversation history with auto-scroll
 */

import React, { useEffect, useRef } from 'react';
import { ChatMessage, TodoCard as TodoCardType } from '@/types/chat';
import MessageBubble from './MessageBubble';

interface MessageListProps {
  messages: ChatMessage[];
  todosMap?: Map<string, TodoCardType[]>; // Map message_id to todos
  isLoading?: boolean;
}

export default function MessageList({ messages, todosMap, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-6 space-y-4"
      style={{ maxHeight: 'calc(100vh - 200px)' }}
    >
      {/* Empty state */}
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="w-16 h-16 mb-4 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-blue-600 dark:text-blue-400"
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
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Start a conversation
          </h3>
          <p className="text-gray-600 dark:text-gray-300 max-w-md">
            Ask me to help you manage your todos. Try saying:
          </p>
          <ul className="mt-4 text-sm text-gray-500 dark:text-gray-400 space-y-2">
            <li>"Add a task to buy groceries tomorrow"</li>
            <li>"Show me all my high priority tasks"</li>
            <li>"What do I need to do today?"</li>
          </ul>
        </div>
      )}

      {/* Messages */}
      {messages.map((message) => {
        const messageTodos = todosMap?.get(message.message_id);
        return (
          <MessageBubble
            key={message.message_id}
            message={message}
            todos={messageTodos}
          />
        );
      })}

      {/* Typing indicator */}
      {isLoading && (
        <div className="flex justify-start mb-4">
          <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-3 rounded-bl-none">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-sm text-gray-500 dark:text-gray-400">AI is thinking...</span>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}
