import Link from 'next/link'
import Header from '@/components/layout/Header'

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />

      <main className="flex flex-col items-center justify-center px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Todo App - Phase II
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Full-stack web application with authentication and database persistence
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link
              href="/register"
              className="bg-primary-600 dark:bg-primary-700 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-primary-700 dark:hover:bg-primary-600 transition-colors"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="bg-white dark:bg-gray-800 text-primary-600 dark:text-primary-400 px-8 py-3 rounded-lg text-lg font-medium border-2 border-primary-600 dark:border-primary-500 hover:bg-primary-50 dark:hover:bg-gray-700 transition-colors"
            >
              Log In
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="text-primary-600 dark:text-primary-400 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Secure Authentication</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Create an account and securely manage your todos with JWT-based authentication
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="text-primary-600 dark:text-primary-400 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Database Persistence</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Your todos are safely stored in PostgreSQL and accessible from any device
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="text-primary-600 dark:text-primary-400 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Advanced Features</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Filter by priority, search, tag your todos, and track your productivity statistics
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600 dark:text-gray-300">
          <p>Phase II - Full-Stack Web Application</p>
          <p className="text-sm mt-2">Built with Next.js 14, FastAPI, and PostgreSQL</p>
        </div>
      </footer>
    </div>
  )
}
