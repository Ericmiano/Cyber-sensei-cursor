import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await axios.get('/api/recommendations/?limit=10')
        setRecommendations(response.data.recommendations)
      } catch (error) {
        console.error('Failed to fetch recommendations:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchRecommendations()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <p>Loading recommendations...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Recommendations</h1>
      <div className="space-y-4">
        {recommendations.length === 0 ? (
          <div className="bg-gray-800 p-6 rounded-lg">
            <p className="text-gray-400">No recommendations available at this time.</p>
          </div>
        ) : (
          recommendations.map((rec, idx) => (
            <div key={idx} className="bg-gray-800 p-6 rounded-lg">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xl font-semibold">{rec.concept_name || rec.title}</h3>
                <span className="bg-indigo-600 px-3 py-1 rounded text-sm">
                  {rec.type}
                </span>
              </div>
              <p className="text-gray-300 mb-2">{rec.reasoning}</p>
              <p className="text-sm text-gray-400">Priority: {(rec.priority * 100).toFixed(0)}%</p>
              <button className="mt-4 bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded">
                {rec.action}
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
