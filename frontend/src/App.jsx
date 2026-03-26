import { useMemo, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const APP_NAME = 'SonicCanvas | AI Music Studio'

const PROMPT_PRESETS = [
  'Lo-fi night drive with vinyl crackle, warm Rhodes chords, mellow bass, and soft boom-bap drums.',
  'Retro synthwave with pulsing arpeggios, neon pads, punchy drums, and a cinematic rise.',
  'Epic trailer style with dark strings, brass swells, taiko hits, and a dramatic final impact.',
  'Ambient meditation soundscape with airy pads, distant bells, and spacious reverb.',
]

function App() {
  const [prompt, setPrompt] = useState('')
  const [duration, setDuration] = useState(10)
  const [audioUrl, setAudioUrl] = useState('')
  const [status, setStatus] = useState('waiting')
  const [mode, setMode] = useState('waiting')
  const [message, setMessage] = useState('Describe your song and press Generate.')

  const canSubmit = useMemo(() => prompt.trim().length > 0 && status !== 'loading', [prompt, status])

  function applyPreset(text) {
    setPrompt(text)
    setStatus('waiting')
    setMessage('Preset loaded. You can edit it or generate directly.')
  }

  async function onGenerate(event) {
    event.preventDefault()
    const cleanedPrompt = prompt.trim()
    if (!cleanedPrompt) {
      setStatus('error')
      setMessage('Please enter a prompt before generating music.')
      return
    }

    const formData = new FormData()
    formData.append('prompt', cleanedPrompt)
    formData.append('duration', String(duration))

    setStatus('loading')
    setMode('processing')
    setMessage('Generating your audio...')

    try {
      const response = await fetch(`${API_BASE_URL}/generate-music`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(data.error || 'Server returned an error.')
      }

      setAudioUrl(data.url || '')
      setMode(data.mode || 'demo')
      setStatus('success')
      setMessage(data.message || 'Your track is ready. Press play or download it.')
    } catch (error) {
      setStatus('error')
      setMode('error')
      setMessage(error.message || 'Unable to generate music right now.')
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">{APP_NAME}</p>
        <h1>Compose Audio From Text</h1>
        <p className="subtitle">A local-first AI music studio with smooth controls and instant playback.</p>

        <div className={`mode-badge mode-${mode}`}>
          Mode: {mode}
        </div>

        <div className="preset-wrap" aria-label="Prompt presets">
          {PROMPT_PRESETS.map((preset) => (
            <button
              key={preset}
              type="button"
              className="preset-chip"
              onClick={() => applyPreset(preset)}
            >
              Try preset
            </button>
          ))}
        </div>

        <form className="composer" onSubmit={onGenerate}>
          <label htmlFor="prompt">Prompt</label>
          <textarea
            id="prompt"
            rows={4}
            placeholder="Example: uplifting house groove, piano stabs, warm bassline, festival-style build and release"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
          />

          <div className="row-group">
            <label htmlFor="duration">Duration: {duration}s</label>
            <input
              id="duration"
              type="range"
              min={1}
              max={20}
              value={duration}
              onChange={(event) => setDuration(Number(event.target.value))}
            />
          </div>

          <button type="submit" disabled={!canSubmit}>
            {status === 'loading' ? 'Generating...' : 'Generate Music'}
          </button>
        </form>

        <p className={`status status-${status}`}>{message}</p>

        {audioUrl && (
          <section className="result-panel">
            <h2>Generated Track</h2>
            <audio controls src={audioUrl} />
            <a className="download-link" href={audioUrl} download>
              Download Audio
            </a>
          </section>
        )}
      </section>
    </main>
  )
}

export default App
