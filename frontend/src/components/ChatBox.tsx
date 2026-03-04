import { useEffect, useRef, useState } from 'react'
import { postQuestion, QASource } from '../api'

interface Message {
  role: 'user' | 'assistant'
  text: string
  sources?: QASource[]
}

interface ChatBoxProps {
  countryId: number
}

export default function ChatBox({ countryId }: ChatBoxProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [openSources, setOpenSources] = useState<number | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  // Reset chat when country changes
  useEffect(() => {
    setMessages([])
    setInput('')
    setOpenSources(null)
  }, [countryId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend() {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: q }])
    setLoading(true)
    try {
      const res = await postQuestion(countryId, q)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: res.answer, sources: res.sources },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Sorry, an error occurred. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      <div className="chatbox">
        <div className="chatbox__header">Ask about this country</div>
        <div className="chatbox__messages">
          {messages.length === 0 && (
            <p className="chatbox__placeholder">
              Ask a question like "What is driving emissions here?" or "What is the temperature trend?"
            </p>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`chatbox__msg chatbox__msg--${msg.role}`}>
              <div className="chatbox__bubble">{msg.text}</div>
              {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                <div className="chatbox__sources">
                  <button
                    className="chatbox__sources-toggle"
                    onClick={() => setOpenSources(openSources === i ? null : i)}
                  >
                    {openSources === i ? '▲ Hide sources' : `▼ Sources (${msg.sources.length})`}
                  </button>
                  {openSources === i && (
                    <ul className="chatbox__sources-list">
                      {msg.sources.map((s, j) => (
                        <li key={j} className="chatbox__source-item">
                          <strong>{s.title}</strong>
                          <p>{s.excerpt}</p>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="chatbox__msg chatbox__msg--assistant">
              <div className="chatbox__bubble chatbox__bubble--loading">
                <span className="chatbox__dot" />
                <span className="chatbox__dot" />
                <span className="chatbox__dot" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div className="chatbox__input-row">
          <input
            className="chatbox__input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question…"
            disabled={loading}
          />
          <button className="chatbox__send" onClick={handleSend} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>
      <style>{`
        .chatbox {
          margin-top: 24px;
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          background: rgba(255,255,255,0.03);
        }
        .chatbox__header {
          padding: 10px 16px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: rgba(255,255,255,0.45);
          border-bottom: 1px solid rgba(255,255,255,0.07);
        }
        .chatbox__messages {
          flex: 1;
          overflow-y: auto;
          padding: 12px 16px;
          display: flex;
          flex-direction: column;
          gap: 10px;
          max-height: 280px;
          min-height: 100px;
        }
        .chatbox__placeholder {
          font-size: 13px;
          color: rgba(255,255,255,0.3);
          text-align: center;
          margin: auto 0;
          line-height: 1.5;
        }
        .chatbox__msg {
          display: flex;
          flex-direction: column;
        }
        .chatbox__msg--user {
          align-items: flex-end;
        }
        .chatbox__msg--assistant {
          align-items: flex-start;
        }
        .chatbox__bubble {
          max-width: 90%;
          padding: 8px 12px;
          border-radius: 12px;
          font-size: 13px;
          line-height: 1.5;
          white-space: pre-wrap;
        }
        .chatbox__msg--user .chatbox__bubble {
          background: rgba(96,165,250,0.2);
          color: #bfdbfe;
          border-bottom-right-radius: 4px;
        }
        .chatbox__msg--assistant .chatbox__bubble {
          background: rgba(255,255,255,0.07);
          color: #e8e8f0;
          border-bottom-left-radius: 4px;
        }
        .chatbox__bubble--loading {
          display: flex;
          gap: 5px;
          align-items: center;
          padding: 12px 16px;
        }
        .chatbox__dot {
          display: inline-block;
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: rgba(255,255,255,0.4);
          animation: chatDot 1.2s ease-in-out infinite;
        }
        .chatbox__dot:nth-child(2) { animation-delay: 0.2s; }
        .chatbox__dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes chatDot {
          0%, 80%, 100% { transform: scale(0.8); opacity: 0.4; }
          40% { transform: scale(1.1); opacity: 1; }
        }
        .chatbox__sources {
          margin-top: 4px;
          max-width: 90%;
        }
        .chatbox__sources-toggle {
          background: none;
          border: none;
          color: rgba(255,255,255,0.4);
          font-size: 11px;
          cursor: pointer;
          padding: 2px 0;
        }
        .chatbox__sources-toggle:hover {
          color: rgba(255,255,255,0.65);
        }
        .chatbox__sources-list {
          list-style: none;
          padding: 6px 0 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .chatbox__source-item {
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
          padding: 8px 10px;
          font-size: 12px;
        }
        .chatbox__source-item strong {
          display: block;
          color: rgba(255,255,255,0.7);
          margin-bottom: 3px;
        }
        .chatbox__source-item p {
          margin: 0;
          color: rgba(255,255,255,0.45);
          line-height: 1.4;
        }
        .chatbox__input-row {
          display: flex;
          border-top: 1px solid rgba(255,255,255,0.07);
          padding: 8px 12px;
          gap: 8px;
        }
        .chatbox__input {
          flex: 1;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 8px;
          color: #e8e8f0;
          font-size: 13px;
          padding: 7px 10px;
          outline: none;
          transition: border-color 0.2s;
        }
        .chatbox__input:focus {
          border-color: rgba(96,165,250,0.5);
        }
        .chatbox__input::placeholder {
          color: rgba(255,255,255,0.25);
        }
        .chatbox__input:disabled {
          opacity: 0.5;
        }
        .chatbox__send {
          background: rgba(96,165,250,0.2);
          border: 1px solid rgba(96,165,250,0.4);
          border-radius: 8px;
          color: #60a5fa;
          font-size: 13px;
          font-weight: 600;
          padding: 7px 14px;
          cursor: pointer;
          transition: background 0.2s;
          white-space: nowrap;
        }
        .chatbox__send:hover:not(:disabled) {
          background: rgba(96,165,250,0.3);
        }
        .chatbox__send:disabled {
          opacity: 0.4;
          cursor: default;
        }

        @media (max-width: 600px) {
          .chatbox__messages {
            max-height: 160px;
          }
        }
      `}</style>
    </>
  )
}
