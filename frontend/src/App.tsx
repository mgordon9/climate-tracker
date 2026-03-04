import { useState } from 'react'
import Globe from './components/Globe'
import CountryPanel from './components/CountryPanel'
import CompareBar from './components/CompareBar'
import Legend from './components/Legend'
import './App.css'

export default function App() {
  const [selectedCountryId, setSelectedCountryId] = useState<number | null>(null)
  const [compareIds, setCompareIds] = useState<number[]>([])

  function toggleCompare(id: number) {
    setCompareIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )
  }

  return (
    <div className="app">
      <Globe onCountrySelect={setSelectedCountryId} />
      <CountryPanel
        countryId={selectedCountryId}
        onClose={() => setSelectedCountryId(null)}
        compareIds={compareIds}
        onCompareToggle={toggleCompare}
      />
      <CompareBar
        compareIds={compareIds}
        onRemove={(id) => setCompareIds((prev) => prev.filter((x) => x !== id))}
        onClearAll={() => setCompareIds([])}
      />
      <Legend />
    </div>
  )
}
