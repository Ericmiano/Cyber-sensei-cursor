import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function Dashboard() {
  const logout = useAuthStore((state) => state.logout)

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <nav className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">Cyber Sensei</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/dashboard" className="hover:text-indigo-400">Dashboard</Link>
              <Link to="/curriculum" className="hover:text-indigo-400">Curriculum</Link>
              <Link to="/quiz" className="hover:text-indigo-400">Quiz</Link>
              <Link to="/recommendations" className="hover:text-indigo-400">Recommendations</Link>
              <button
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-700 rounded-lg p-8">
            <h2 className="text-2xl font-bold mb-4">Welcome to Cyber Sensei</h2>
            <p className="text-gray-400 mb-6">
              Your intelligent adaptive learning platform. Get personalized study materials,
              interactive quizzes, and practical labs.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <Link
                to="/curriculum"
                className="bg-gray-800 p-6 rounded-lg hover:bg-gray-700 transition"
              >
                <h3 className="text-xl font-semibold mb-2">Curriculum</h3>
                <p className="text-gray-400">
                  Generate personalized learning paths based on your goals and mastery level.
                </p>
              </Link>

              <Link
                to="/quiz"
                className="bg-gray-800 p-6 rounded-lg hover:bg-gray-700 transition"
              >
                <h3 className="text-xl font-semibold mb-2">Quiz</h3>
                <p className="text-gray-400">
                  Test your knowledge with adaptive quizzes that adjust to your ability level.
                </p>
              </Link>

              <Link
                to="/recommendations"
                className="bg-gray-800 p-6 rounded-lg hover:bg-gray-700 transition"
              >
                <h3 className="text-xl font-semibold mb-2">Recommendations</h3>
                <p className="text-gray-400">
                  Get AI-powered recommendations for your next learning steps.
                </p>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
