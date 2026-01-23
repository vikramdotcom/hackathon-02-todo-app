/**
 * TypeScript type definitions for the application
 */

/**
 * User model
 */
export interface User {
  id: number
  email: string
  username: string
  created_at: string
  updated_at: string
}

/**
 * User login credentials
 */
export interface UserLogin {
  email: string
  password: string
}

/**
 * User registration data
 */
export interface UserCreate {
  email: string
  username: string
  password: string
}

/**
 * Authentication token response
 */
export interface Token {
  access_token: string
  token_type: string
}

/**
 * Todo model
 */
export interface Todo {
  id: number
  user_id: number
  title: string
  description: string
  completed: boolean
  priority: 'low' | 'medium' | 'high'
  tags: string[]
  due_date: string | null
  recurrence: string | null
  created_at: string
  updated_at: string
}

/**
 * Todo creation data
 */
export interface TodoCreate {
  title: string
  description?: string
  priority?: 'low' | 'medium' | 'high'
  tags?: string[]
  due_date?: string | null
  recurrence?: string | null
}

/**
 * Todo update data
 */
export interface TodoUpdate {
  title?: string
  description?: string
  completed?: boolean
  priority?: 'low' | 'medium' | 'high'
  tags?: string[]
  due_date?: string | null
  recurrence?: string | null
}
