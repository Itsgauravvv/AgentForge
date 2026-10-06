import { useEffect, useState } from 'react'

function App() {
  const [health, setHealth] = useState<any>(null)

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error("API Error:", err))
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>AgentForge Dashboard</h1>
      <div style={{ padding: '1rem', background: '#f0f0f0', borderRadius: '8px' }}>
        <h3>System Status</h3>
        {health ? (
          <pre>{JSON.stringify(health, null, 2)}</pre>
        ) : (
          <p>Connecting to backend...</p>
        )}
      </div>
    </div>
  )
}

export default App