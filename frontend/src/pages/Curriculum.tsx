import { useState } from 'react'
import axios from 'axios'

export default function Curriculum() {
  const [topicId, setTopicId] = useState('')
  const [bloomLevel, setBloomLevel] = useState(3)
  const [curriculum, setCurriculum] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const response = await axios.post('/api/curriculum/generate', {
        topic_id: topicId,
        target_bloom_level: bloomLevel,
      })
      setCurriculum(response.data.curriculum)
    } catch (error) {
      console.error('Failed to generate curriculum:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Curriculum Generator</h1>
      <div className="bg-gray-800 p-6 rounded-lg mb-6">
        <div className="space-y-4">
          <div>
            <label className="block mb-2">Topic ID</label>
            <input
              type="text"
              value={topicId}
              onChange={(e) => setTopicId(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 rounded text-white"
              placeholder="Enter topic UUID"
            />
          </div>
          <div>
            <label className="block mb-2">Target Bloom Level (1-6)</label>
            <input
              type="number"
              min="1"
              max="6"
              value={bloomLevel}
              onChange={(e) => setBloomLevel(parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-gray-700 rounded text-white"
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 px-6 py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Curriculum'}
          </button>
        </div>
      </div>

      {curriculum.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Your Personalized Curriculum</h2>
          <div className="space-y-4">
            {curriculum.map((item, idx) => (
              <div key={idx} className="bg-gray-700 p-4 rounded">
                <h3 className="font-semibold">{item.concept_name}</h3>
                <p className="text-sm text-gray-400">
                  Order: {item.order} | Bloom Level: {item.bloom_level} | 
                  Difficulty: {(item.difficulty * 100).toFixed(0)}% | 
                  Mastery: {(item.current_mastery * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
