'use client'

import { useState } from 'react'
import apiClient from '@/lib/api'
import type { TodoCreate } from '@/lib/types'

interface TodoFormProps {
  onSuccess: () => void
}

export default function TodoForm({ onSuccess }: TodoFormProps) {
  const [formData, setFormData] = useState<TodoCreate>({
    title: '',
    description: '',
    priority: 'medium',
    tags: [],
    due_date: undefined,
  })
  const [tagInput, setTagInput] = useState('')
  const [error, setError] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await apiClient.post('/todos', formData)
      setFormData({
        title: '',
        description: '',
        priority: 'medium',
        tags: [],
        due_date: undefined,
      })
      setTagInput('')
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create todo')
    } finally {
      setLoading(false)
    }
  }

  const addTag = () => {
    if (tagInput.trim() && !formData.tags?.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...(formData.tags || []), tagInput.trim()],
      })
      setTagInput('')
    }
  }

  const removeTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags?.filter((t) => t !== tag) || [],
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Create New Todo</h2>

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Title *
        </label>
        <input
          id="title"
          type="text"
          required
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="What needs to be done?"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Description
        </label>
        <textarea
          id="description"
          rows={3}
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Add more details..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Due Date
          </label>
          <input
            id="due_date"
            type="datetime-local"
            value={formData.due_date ? new Date(formData.due_date).toISOString().slice(0, 16) : ''}
            onChange={(e) => setFormData({ ...formData, due_date: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Tags
        </label>
        <div className="flex gap-2">
          <input
            id="tags"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Add a tag..."
          />
          <button
            type="button"
            onClick={addTag}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            Add
          </button>
        </div>
        {formData.tags && formData.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {formData.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 rounded-md text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="text-primary-700 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Creating...' : 'Create Todo'}
      </button>
    </form>
  )
}
