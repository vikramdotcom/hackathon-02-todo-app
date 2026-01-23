'use client'

import { useState } from 'react'
import apiClient from '@/lib/api'
import type { Todo } from '@/lib/types'

interface TodoItemProps {
  todo: Todo
  onUpdate: () => void
}

export default function TodoItem({ todo, onUpdate }: TodoItemProps) {
  const [loading, setLoading] = useState(false)

  const toggleComplete = async () => {
    setLoading(true)
    try {
      const endpoint = todo.completed ? `/todos/${todo.id}/incomplete` : `/todos/${todo.id}/complete`
      await apiClient.post(endpoint)
      onUpdate()
    } catch (err) {
      console.error('Failed to toggle todo:', err)
    } finally {
      setLoading(false)
    }
  }

  const deleteTodo = async () => {
    if (!confirm('Are you sure you want to delete this todo?')) return

    setLoading(true)
    try {
      await apiClient.delete(`/todos/${todo.id}`)
      onUpdate()
    } catch (err) {
      console.error('Failed to delete todo:', err)
    } finally {
      setLoading(false)
    }
  }

  const priorityColors = {
    low: 'bg-blue-100 text-blue-700',
    medium: 'bg-yellow-100 text-yellow-700',
    high: 'bg-red-100 text-red-700',
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={toggleComplete}
          disabled={loading}
          className="mt-1 h-5 w-5 text-primary-600 rounded focus:ring-primary-500"
        />

        <div className="flex-1 min-w-0">
          <h3 className={`text-lg font-medium ${todo.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
            {todo.title}
          </h3>

          {todo.description && (
            <p className="text-sm text-gray-600 mt-1">{todo.description}</p>
          )}

          <div className="flex flex-wrap items-center gap-2 mt-2">
            <span className={`px-2 py-1 rounded-md text-xs font-medium ${priorityColors[todo.priority]}`}>
              {todo.priority}
            </span>

            {todo.tags.map((tag) => (
              <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-xs">
                {tag}
              </span>
            ))}

            {todo.due_date && (
              <span className="text-xs text-gray-500">
                Due: {new Date(todo.due_date).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>

        <button
          onClick={deleteTodo}
          disabled={loading}
          className="text-red-600 hover:text-red-800 p-2 rounded-md hover:bg-red-50 disabled:opacity-50"
          title="Delete todo"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  )
}
