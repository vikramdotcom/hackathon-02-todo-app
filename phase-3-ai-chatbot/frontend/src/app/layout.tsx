import type { Metadata } from 'next'
import '../styles/globals.css'
import FloatingChatButton from '@/components/layout/FloatingChatButton'

export const metadata: Metadata = {
  title: 'Todo App Fullstack',
  description: 'Full-stack web application for todo management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <FloatingChatButton />
      </body>
    </html>
  )
}
