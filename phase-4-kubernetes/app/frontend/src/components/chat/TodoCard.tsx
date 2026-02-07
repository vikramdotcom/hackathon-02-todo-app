/**
 * TodoCard component - Displays a todo item within the chat interface
 */

import React from 'react';
import { TodoCard as TodoCardType } from '@/types/chat';

interface TodoCardProps {
  todo: TodoCardType;
}

export default function TodoCard({ todo }: TodoCardProps) {
  const priorityColors = {
    low: 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    medium: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800',
    high: 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400 border-red-200 dark:border-red-800',
  };

  const priorityColor = priorityColors[todo.priority] || priorityColors.medium;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 my-2 bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow">
      {/* Header with title and status */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3
            className={`font-semibold text-lg ${
              todo.completed ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'
            }`}
          >
            {todo.title}
          </h3>
        </div>
        <div className="flex items-center gap-2 ml-2">
          {/* Priority badge */}
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium border ${priorityColor}`}
          >
            {todo.priority}
          </span>
          {/* Completion status */}
          {todo.completed && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400 border border-green-200 dark:border-green-800">
              ✓ Done
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      {todo.description && (
        <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">{todo.description}</p>
      )}

      {/* Footer with metadata */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
        {/* Due date */}
        {todo.due_date && (
          <div className="flex items-center gap-1">
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
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span>{formatDate(todo.due_date)}</span>
          </div>
        )}

        {/* Tags */}
        {todo.tags && todo.tags.length > 0 && (
          <div className="flex items-center gap-1 flex-wrap">
            {todo.tags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-0.5 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Todo ID (for reference) */}
        <span className="text-xs text-gray-400 dark:text-gray-500">ID: {todo.id}</span>
      </div>
    </div>
  );
}
