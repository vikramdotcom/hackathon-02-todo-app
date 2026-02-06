/**
 * InputBox component - Text input for sending chat messages
 */

import React, { useState, useRef, KeyboardEvent } from 'react';

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function InputBox({
  onSendMessage,
  disabled = false,
  placeholder = 'Type your message...',
}: InputBoxProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-4">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        {/* Text input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed"
            style={{ minHeight: '48px', maxHeight: '150px' }}
          />

          {/* Character count (optional) */}
          {message.length > 0 && (
            <div className="absolute bottom-2 right-2 text-xs text-gray-400 dark:text-gray-500">
              {message.length}/10000
            </div>
          )}
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="flex-shrink-0 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          aria-label="Send message"
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
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>

      {/* Helper text */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
        Press <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-700 dark:text-gray-300">Enter</kbd> to send,
        <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded ml-1 text-gray-700 dark:text-gray-300">Shift+Enter</kbd> for new line
      </div>
    </div>
  );
}
