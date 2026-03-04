import { useEffect, useState } from 'react'
import { fetchCountryDetail, fetchTimeSeries, CountryDetail, TimeSeries } from '../api'
import ClimateChart from './ClimateChart'

interface CountryPanelProps {
  countryId: number | null
  onClose: () => void
  compareIds: number[]
  onCompareToggle: (id: number) => void
}

export default function CountryPanel({ countryId, onClose, compareIds, onCompareToggle }: CountryPanelProps) {
  const [detail, setDetail] = useState<CountryDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [metric, setMetric] = useState('temperature_change')
  const [startYear, setStartYear] = useState(1990)
  const [endYear, setEndYear] = useState(2023)
  const [chartSeries, setChartSeries] = useState<TimeSeries[]>([])
  const [chartLoading, setChartLoading] = useState(false)

  useEffect(() => {
    if (countryId === null) {
      setDetail(null)
      setChartSeries([])
      return
    }
    setLoading(true)
    setError(null)
    fetchCountryDetail(countryId)
      .then((d) => {
        setDetail(d)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [countryId])

  useEffect(() => {
    if (countryId === null) return
    setChartLoading(true)
    fetchTimeSeries(countryId, metric, startYear, endYear)
      .then((ts) => {
        setChartSeries([ts])
        setChartLoading(false)
      })
      .catch(() => {
        setChartSeries([])
        setChartLoading(false)
      })
  }, [countryId, metric, startYear, endYear])

  const open = countryId !== null
  const inCompare = countryId !== null && compareIds.includes(countryId)

  return (
    <>
      <div className={`panel ${open ? 'panel--open' : ''}`}>
        <button className="panel__close" onClick={onClose} aria-label="Close">
          ×
        </button>
        {loading && (
          <div className="panel__loading">
            <div className="spinner-sm" />
          </div>
        )}
        {error && <p className="panel__error">{error}</p>}
        {detail && !loading && (
          <div className="panel__content">
            <h2 className="panel__name">{detail.name}</h2>
            <dl className="panel__stats">
              {detail.region && (
                <>
                  <dt>Region</dt>
                  <dd>{detail.region}</dd>
                </>
              )}
              {detail.capital_city && (
                <>
                  <dt>Capital</dt>
                  <dd>{detail.capital_city}</dd>
                </>
              )}
              {detail.population !== null && detail.population !== undefined && (
                <>
                  <dt>Population</dt>
                  <dd>{detail.population.toLocaleString()}</dd>
                </>
              )}
              <dt>ISO&nbsp;2</dt>
              <dd>{detail.iso_code}</dd>
              {detail.iso3_code && (
                <>
                  <dt>ISO&nbsp;3</dt>
                  <dd>{detail.iso3_code}</dd>
                </>
              )}
            </dl>

            <button
              className={`compare-btn ${inCompare ? 'compare-btn--active' : ''}`}
              onClick={() => countryId !== null && onCompareToggle(countryId)}
            >
              {inCompare ? '✕ Remove from Compare' : '+ Add to Compare'}
            </button>

            <div className="panel__chart">
              {chartLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: 24 }}>
                  <div className="spinner-sm" />
                </div>
              ) : (
                <ClimateChart
                  series={chartSeries}
                  metric={metric}
                  onMetricChange={setMetric}
                  startYear={startYear}
                  endYear={endYear}
                  onYearRangeChange={(s, e) => { setStartYear(s); setEndYear(e) }}
                />
              )}
            </div>
          </div>
        )}
      </div>
      <style>{`
        .panel {
          position: fixed;
          top: 0;
          right: 0;
          width: 380px;
          height: 100vh;
          background: rgba(15, 15, 25, 0.92);
          backdrop-filter: blur(12px);
          color: #e8e8f0;
          transform: translateX(100%);
          transition: transform 0.3s ease;
          z-index: 20;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
        }
        .panel--open {
          transform: translateX(0);
        }
        .panel__close {
          position: absolute;
          top: 16px;
          right: 16px;
          background: rgba(255,255,255,0.1);
          border: none;
          color: #fff;
          font-size: 22px;
          line-height: 1;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }
        .panel__close:hover {
          background: rgba(255,255,255,0.2);
        }
        .panel__loading {
          display: flex;
          align-items: center;
          justify-content: center;
          flex: 1;
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
        .panel__error {
          color: #f87171;
          padding: 24px;
          font-size: 14px;
        }
        .panel__content {
          padding: 56px 28px 28px;
        }
        .panel__name {
          font-size: 26px;
          font-weight: 600;
          margin-bottom: 24px;
          line-height: 1.2;
        }
        .panel__stats {
          display: grid;
          grid-template-columns: auto 1fr;
          gap: 10px 16px;
        }
        .panel__stats dt {
          color: rgba(255,255,255,0.5);
          font-size: 13px;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          align-self: center;
          white-space: nowrap;
        }
        .panel__stats dd {
          font-size: 15px;
          font-weight: 500;
        }
        .compare-btn {
          margin-top: 20px;
          width: 100%;
          padding: 8px 16px;
          border-radius: 8px;
          border: 1px solid rgba(96,165,250,0.5);
          background: transparent;
          color: #60a5fa;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }
        .compare-btn:hover {
          background: rgba(96,165,250,0.1);
        }
        .compare-btn--active {
          background: rgba(248,113,113,0.15);
          border-color: rgba(248,113,113,0.5);
          color: #f87171;
        }
        .panel__chart {
          margin-top: 24px;
        }

        @media (max-width: 600px) {
          .panel {
            width: 100%;
            height: 50vh;
            top: auto;
            bottom: 0;
            right: 0;
            transform: translateY(100%);
            border-radius: 16px 16px 0 0;
          }
          .panel--open {
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  )
}
