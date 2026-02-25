export interface GlobeCountry {
  id: number
  name: string
  iso_code: string
  iso3_code: string | null
  latitude: number | null
  longitude: number | null
  latest_temp_change: number | null
}

export interface ClimateDataPoint {
  id: number
  date: string
  metric_type: string
  value: number
  unit: string
  source: string | null
}

export interface CountryDetail {
  id: number
  name: string
  iso_code: string
  iso3_code: string | null
  region: string | null
  capital_city: string | null
  latitude: number | null
  longitude: number | null
  population: number | null
  climate_data: ClimateDataPoint[]
}

export async function fetchGlobeData(): Promise<GlobeCountry[]> {
  const res = await fetch('/api/globe')
  if (!res.ok) throw new Error(`Failed to fetch globe data: ${res.status}`)
  return res.json()
}

export async function fetchCountryDetail(id: number): Promise<CountryDetail> {
  const res = await fetch(`/api/countries/${id}`)
  if (!res.ok) throw new Error(`Failed to fetch country ${id}: ${res.status}`)
  return res.json()
}
