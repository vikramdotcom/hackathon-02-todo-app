'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { logout, isAuthenticated } from '@/lib/auth'
import ThemeToggle from './ThemeToggle'

export default function Header() {
  const router = useRouter()
  const [authenticated, setAuthenticated] = useState(false)
  const [mounted, setMounted] = useState(false)

  // Check authentication only on client side after mount
  useEffect(() => {
    setMounted(true)
    setAuthenticated(isAuthenticated())
  }, [])

  const handleLogout = () => {
    logout()
    setAuthenticated(false)
    router.push('/')
  }

  // Render a consistent state until mounted to avoid hydration mismatch
  if (!mounted) {
    return (
      <header className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-bold text-primary-600 dark:text-primary-400">
                Todo App
              </Link>
            </div>
            <nav className="flex items-center space-x-4">
              <ThemeToggle />
              <Link
                href="/login"
                className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="bg-primary-600 dark:bg-primary-700 text-white hover:bg-primary-700 dark:hover:bg-primary-600 px-4 py-2 rounded-md text-sm font-medium"
              >
                Sign Up
              </Link>
            </nav>
          </div>
        </div>
      </header>
    )
  }

  return (
    <header className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-primary-600 dark:text-primary-400">
              Todo App
            </Link>
          </div>

          <nav className="flex items-center space-x-4">
            <ThemeToggle />
            {authenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  href="/profile"
                  className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 px-4 py-2 rounded-md text-sm font-medium"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="bg-primary-600 dark:bg-primary-700 text-white hover:bg-primary-700 dark:hover:bg-primary-600 px-4 py-2 rounded-md text-sm font-medium"
                >
                  Sign Up
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}
