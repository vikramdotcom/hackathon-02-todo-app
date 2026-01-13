/**
 * Authentication utilities for token management
 */

const TOKEN_KEY = 'auth_token'

/**
 * Store authentication token in localStorage
 */
export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token)
  }
}

/**
 * Retrieve authentication token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY)
  }
  return null
}

/**
 * Remove authentication token from localStorage
 */
export function removeAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY)
  }
}

/**
 * Check if user is authenticated (has a valid token)
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null
}

/**
 * Logout user by removing authentication token
 */
export function logout(): void {
  removeAuthToken()
}
