import {
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { TimeSeries } from '../api'

const COLORS = ['#60a5fa', '#f87171', '#34d399', '#fbbf24', '#a78bfa', '#fb7185']
const METRICS = [
  { key: 'temperature_change', label: 'Temperature Change' },
  { key: 'co2_emissions', label: 'CO₂ Emissions' },
]

interface ClimateChartProps {
  series: TimeSeries[]
  metric: string
  onMetricChange: (m: string) => void
  startYear: number
  endYear: number
  onYearRangeChange: (start: number, end: number) => void
}

export default function ClimateChart({
  series,
  metric,
  onMetricChange,
  startYear,
  endYear,
  onYearRangeChange,
}: ClimateChartProps) {
  // Build unified data keyed by year
  const yearMap = new Map<number, Record<string, number>>()
  for (const s of series) {
    for (const pt of s.data) {
      if (!yearMap.has(pt.year)) yearMap.set(pt.year, { year: pt.year })
      yearMap.get(pt.year)![s.country_name] = pt.value
    }
  }
  const chartData = Array.from(yearMap.values()).sort((a, b) => a.year - b.year)

  const unit = series[0]?.unit ?? ''

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        {METRICS.map((m) => (
          <button
            key={m.key}
            onClick={() => onMetricChange(m.key)}
            style={{
              padding: '4px 12px',
              borderRadius: 16,
              border: 'none',
              cursor: 'pointer',
              fontSize: 12,
              fontWeight: 600,
              background: metric === m.key ? '#60a5fa' : 'rgba(255,255,255,0.12)',
              color: metric === m.key ? '#0f0f19' : '#e8e8f0',
              transition: 'background 0.2s',
            }}
          >
            {m.label}
          </button>
        ))}
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginLeft: 'auto', fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>
          <input
            type="number"
            value={startYear}
            onChange={(e) => onYearRangeChange(Number(e.target.value), endYear)}
            style={yearInputStyle}
            aria-label="Start year"
          />
          <span>–</span>
          <input
            type="number"
            value={endYear}
            onChange={(e) => onYearRangeChange(startYear, Number(e.target.value))}
            style={yearInputStyle}
            aria-label="End year"
          />
        </div>
      </div>

      {chartData.length === 0 ? (
        <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13, textAlign: 'center', padding: '24px 0' }}>
          No data for this metric / year range.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
            <XAxis
              dataKey="year"
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            />
            <YAxis
              unit={unit}
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={50}
            />
            <Tooltip
              contentStyle={{
                background: 'rgba(15,15,25,0.95)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 8,
                color: '#e8e8f0',
                fontSize: 12,
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: 12, color: 'rgba(255,255,255,0.7)' }}
            />
            {series.map((s, i) => (
              <Line
                key={s.country_id}
                type="monotone"
                dataKey={s.country_name}
                stroke={COLORS[i % COLORS.length]}
                dot={false}
                strokeWidth={2}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

const yearInputStyle: React.CSSProperties = {
  width: 60,
  padding: '3px 6px',
  background: 'rgba(255,255,255,0.08)',
  border: '1px solid rgba(255,255,255,0.15)',
  borderRadius: 6,
  color: '#e8e8f0',
  fontSize: 12,
  textAlign: 'center',
}
