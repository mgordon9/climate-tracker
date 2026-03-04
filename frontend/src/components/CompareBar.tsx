import { useEffect, useState } from 'react'
import { fetchCompare, TimeSeries } from '../api'
import ClimateChart from './ClimateChart'

interface CompareBarProps {
  compareIds: number[]
  onRemove: (id: number) => void
  onClearAll: () => void
}

export default function CompareBar({ compareIds, onRemove, onClearAll }: CompareBarProps) {
  const [metric, setMetric] = useState('temperature_change')
  const [startYear, setStartYear] = useState(1990)
  const [endYear, setEndYear] = useState(2023)
  const [series, setSeries] = useState<TimeSeries[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (compareIds.length === 0) {
      setSeries([])
      return
    }
    setLoading(true)
    fetchCompare(compareIds, metric, startYear, endYear)
      .then((data) => {
        setSeries(data)
        setLoading(false)
      })
      .catch(() => {
        setSeries([])
        setLoading(false)
      })
  }, [compareIds, metric, startYear, endYear])

  if (compareIds.length === 0) return null

  return (
    <>
      <div className="compare-bar">
        <div className="compare-bar__header">
          <div className="compare-bar__chips">
            {series.map((s) => (
              <button
                key={s.country_id}
                className="compare-chip"
                onClick={() => onRemove(s.country_id)}
                title={`Remove ${s.country_name}`}
              >
                ✕ {s.country_name}
              </button>
            ))}
            {/* Show placeholders for IDs not yet loaded */}
            {compareIds
              .filter((id) => !series.find((s) => s.country_id === id))
              .map((id) => (
                <button
                  key={id}
                  className="compare-chip compare-chip--loading"
                  onClick={() => onRemove(id)}
                >
                  ✕ …
                </button>
              ))}
          </div>
          <button className="compare-bar__clear" onClick={onClearAll}>
            Clear All
          </button>
        </div>
        <div className="compare-bar__chart">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 180 }}>
              <div className="spinner-sm" />
            </div>
          ) : (
            <ClimateChart
              series={series}
              metric={metric}
              onMetricChange={setMetric}
              startYear={startYear}
              endYear={endYear}
              onYearRangeChange={(s, e) => { setStartYear(s); setEndYear(e) }}
            />
          )}
        </div>
      </div>
      <style>{`
        .compare-bar {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          height: 300px;
          background: rgba(10, 10, 20, 0.96);
          backdrop-filter: blur(16px);
          border-top: 1px solid rgba(255,255,255,0.1);
          z-index: 30;
          display: flex;
          flex-direction: column;
          padding: 12px 24px 16px;
          color: #e8e8f0;
        }
        .compare-bar__header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
          flex-wrap: wrap;
        }
        .compare-bar__chips {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
          flex: 1;
        }
        .compare-chip {
          padding: 4px 10px;
          border-radius: 16px;
          border: 1px solid rgba(96,165,250,0.4);
          background: rgba(96,165,250,0.1);
          color: #93c5fd;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
          white-space: nowrap;
        }
        .compare-chip:hover {
          background: rgba(248,113,113,0.2);
          border-color: rgba(248,113,113,0.4);
          color: #f87171;
        }
        .compare-chip--loading {
          opacity: 0.5;
        }
        .compare-bar__clear {
          padding: 4px 12px;
          border-radius: 8px;
          border: 1px solid rgba(255,255,255,0.15);
          background: transparent;
          color: rgba(255,255,255,0.5);
          font-size: 12px;
          cursor: pointer;
          white-space: nowrap;
          transition: background 0.2s;
        }
        .compare-bar__clear:hover {
          background: rgba(255,255,255,0.08);
          color: #e8e8f0;
        }
        .compare-bar__chart {
          flex: 1;
          overflow: hidden;
        }
        .spinner-sm {
          width: 32px;
          height: 32px;
          border: 3px solid rgba(255,255,255,0.2);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  )
}
