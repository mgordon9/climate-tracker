import { useState } from 'react'
import Globe from './components/Globe'
import CountryPanel from './components/CountryPanel'
import './App.css'

export default function App() {
  const [selectedCountryId, setSelectedCountryId] = useState<number | null>(null)

  return (
    <div className="app">
      <Globe onCountrySelect={setSelectedCountryId} />
      <CountryPanel
        countryId={selectedCountryId}
        onClose={() => setSelectedCountryId(null)}
      />
    </div>
  )
}
