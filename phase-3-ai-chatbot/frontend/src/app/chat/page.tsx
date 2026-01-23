/**
 * Chat page - AI-powered todo management through conversation
 */

'use client';

import React from 'react';
import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatPage() {
  const handleError = (error: string) => {
    console.error('Chat error:', error);
    // You can add toast notifications or other error handling here
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Page header */}
      <header className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Todo Assistant</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage your tasks through natural conversation
            </p>
          </div>

          {/* Navigation back to main app */}
          <a
            href="/"
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
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
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to Todos
          </a>
        </div>
      </header>

      {/* Chat interface */}
      <main className="flex-1 overflow-hidden">
        <ChatInterface
          apiBaseUrl={process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}
          onError={handleError}
        />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-4">
            <span>Powered by OpenAI GPT</span>
            <span>•</span>
            <span>Phase III - AI Chatbot</span>
          </div>
          <div className="flex items-center gap-2">
            <svg
              className="w-4 h-4 text-green-500"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span>Connected</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
