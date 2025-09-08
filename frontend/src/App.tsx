import React, { useMemo, useState } from 'react'

type BattleRequest = {
  pokemon1: string
  pokemon2: string
  level?: number
  max_turns?: number
}

type BattleResponse = {
  tool: string
  params: BattleRequest
  result: {
    winner: string
    turns: number
    log: string[]
    final_state: { p1: { name: string; hp: number }; p2: { name: string; hp: number } }
  }
}

export default function App() {
  const [pokemon1, setPokemon1] = useState('pikachu')
  const [pokemon2, setPokemon2] = useState('charmander')
  const [level, setLevel] = useState(50)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<BattleResponse | null>(null)

  const canSubmit = useMemo(() => {
    return !!pokemon1.trim() && !!pokemon2.trim() && pokemon1.trim().toLowerCase() !== pokemon2.trim().toLowerCase()
  }, [pokemon1, pokemon2])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!canSubmit) return
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const resp = await fetch('/mcp/tools/battle_simulator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pokemon1: pokemon1.trim(), pokemon2: pokemon2.trim(), level, max_turns: 200 })
      })
      if (!resp.ok) {
        const text = await resp.text()
        throw new Error(text || `Request failed: ${resp.status}`)
      }
      const json = (await resp.json()) as BattleResponse
      setData(json)
    } catch (err: any) {
      setError(err?.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif', padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <h1 style={{ marginBottom: 8 }}>Pokemon Battle Simulator</h1>
      <p style={{ marginTop: 0, color: '#555' }}>Enter two Pokémon names. Data is fetched from PokeAPI via your backend.</p>

      <form onSubmit={onSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 12, alignItems: 'end', marginTop: 16 }}>
        <div>
          <label htmlFor="pokemon1" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Pokémon 1</label>
          <input id="pokemon1" value={pokemon1} onChange={e => setPokemon1(e.target.value)} placeholder="e.g., pikachu" required style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid #ccc' }} />
        </div>
        <div>
          <label htmlFor="pokemon2" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Pokémon 2</label>
          <input id="pokemon2" value={pokemon2} onChange={e => setPokemon2(e.target.value)} placeholder="e.g., charizard" required style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid #ccc' }} />
        </div>
        <div>
          <label htmlFor="level" style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>Level</label>
          <input id="level" type="number" min={1} max={100} value={level} onChange={e => setLevel(parseInt(e.target.value || '50', 10))} style={{ width: 120, padding: '10px 12px', borderRadius: 8, border: '1px solid #ccc' }} />
        </div>
        <button type="submit" disabled={!canSubmit || loading} style={{ padding: '12px 16px', borderRadius: 8, border: '1px solid #0a7', background: loading ? '#9fd' : '#0a7', color: '#fff', fontWeight: 600, cursor: loading ? 'default' : 'pointer', height: 44 }}>
          {loading ? 'Simulating…' : 'Simulate Battle'}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: 16, padding: 12, border: '1px solid #f99', background: '#fee', color: '#900', borderRadius: 8 }}>
          {error}
        </div>
      )}

      {data && (
        <div style={{ marginTop: 24 }}>
          <h2 style={{ marginBottom: 8 }}>Result</h2>
          <div style={{ padding: 12, border: '1px solid #ddd', borderRadius: 8 }}>
            <p style={{ marginTop: 0 }}><strong>Winner:</strong> {data.result.winner}</p>
            <p><strong>Turns:</strong> {data.result.turns}</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <strong>{data.result.final_state.p1.name}</strong>
                <div>HP: {data.result.final_state.p1.hp}</div>
              </div>
              <div>
                <strong>{data.result.final_state.p2.name}</strong>
                <div>HP: {data.result.final_state.p2.hp}</div>
              </div>
            </div>
            <details style={{ marginTop: 12 }}>
              <summary style={{ cursor: 'pointer' }}>Battle log</summary>
              <ul style={{ marginTop: 12 }}>
                {data.result.log.map((line, idx) => (
                  <li key={idx} style={{ marginBottom: 4 }}>{line}</li>
                ))}
              </ul>
            </details>
          </div>
        </div>
      )}

      <footer style={{ marginTop: 40, color: '#777', fontSize: 12 }}>
        Backend endpoints used: <code>/mcp/tools/battle_simulator</code>
      </footer>
    </div>
  )
}

