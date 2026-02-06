import Link from 'next/link'
import RegisterForm from '@/components/auth/RegisterForm'

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Create Account</h1>
          <p className="text-gray-600 dark:text-gray-300">Sign up to start managing your todos</p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
          <RegisterForm />

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Already have an account?{' '}
              <Link href="/login" className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium">
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
