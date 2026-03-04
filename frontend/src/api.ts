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

export interface TimeSeriesPoint {
  year: number
  value: number
}

export interface TimeSeries {
  country_id: number
  country_name: string
  iso_code: string
  metric: string
  unit: string
  data: TimeSeriesPoint[]
}

export async function fetchTimeSeries(
  id: number,
  metric: string,
  startYear: number,
  endYear: number,
): Promise<TimeSeries> {
  const params = new URLSearchParams({
    metric,
    start_year: String(startYear),
    end_year: String(endYear),
  })
  const res = await fetch(`/api/countries/${id}/climate?${params}`)
  if (!res.ok) throw new Error(`Failed to fetch climate data for country ${id}: ${res.status}`)
  return res.json()
}

export interface QASource { title: string; excerpt: string }
export interface QAResponse { answer: string; sources: QASource[] }

export async function postQuestion(countryId: number, question: string): Promise<QAResponse> {
  const res = await fetch('/api/qa', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ country_id: countryId, question }),
  })
  if (!res.ok) throw new Error(`Q&A request failed: ${res.status}`)
  return res.json()
}

export async function fetchCompare(
  ids: number[],
  metric: string,
  startYear: number,
  endYear: number,
): Promise<TimeSeries[]> {
  const params = new URLSearchParams({ metric, start_year: String(startYear), end_year: String(endYear) })
  for (const id of ids) params.append('country_ids', String(id))
  const res = await fetch(`/api/compare?${params}`)
  if (!res.ok) throw new Error(`Failed to fetch compare data: ${res.status}`)
  return res.json()
}
