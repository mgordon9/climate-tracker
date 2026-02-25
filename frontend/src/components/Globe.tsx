import { useEffect, useRef, useState, useCallback } from 'react'
import ReactGlobe, { GlobeMethods } from 'react-globe.gl'
import { fetchGlobeData, GlobeCountry } from '../api'

interface GlobeProps {
  onCountrySelect: (id: number) => void
}

interface GeoFeature {
  type: string
  properties: {
    ADMIN: string
    ISO_A2: string
    ISO_A3: string
  }
  geometry: object
}

interface GeoJSON {
  type: string
  features: GeoFeature[]
}

function tempToColor(temp: number | null): string {
  if (temp === null) return 'rgba(120, 120, 120, 0.7)'

  // Map temp range [-0.5, 3.0] to [0, 1]
  const min = -0.5
  const max = 3.0
  const t = Math.max(0, Math.min(1, (temp - min) / (max - min)))

  // Blue (0,0,255) → White (255,255,255) → Red (255,0,0)
  let r: number, g: number, b: number
  if (t < 0.5) {
    const s = t / 0.5
    r = Math.round(s * 255)
    g = Math.round(s * 255)
    b = 255
  } else {
    const s = (t - 0.5) / 0.5
    r = 255
    g = Math.round((1 - s) * 255)
    b = Math.round((1 - s) * 255)
  }

  return `rgba(${r},${g},${b},0.75)`
}

export default function Globe({ onCountrySelect }: GlobeProps) {
  const globeRef = useRef<GlobeMethods | undefined>(undefined)
  const [countries, setCountries] = useState<GeoFeature[]>([])
  const [tempLookup, setTempLookup] = useState<Map<string, GlobeCountry>>(new Map())
  const [loading, setLoading] = useState(true)
  const [hoverName, setHoverName] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetch(
        'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson',
      ).then((r) => r.json()) as Promise<GeoJSON>,
      fetchGlobeData(),
    ])
      .then(([geojson, globeData]) => {
        const lookup = new Map<string, GlobeCountry>()
        for (const c of globeData) {
          if (c.iso3_code) lookup.set(c.iso3_code, c)
        }
        setTempLookup(lookup)
        setCountries(geojson.features)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to load globe data', err)
        setLoading(false)
      })
  }, [])

  const getPolygonColor = useCallback(
    (feature: object) => {
      const f = feature as GeoFeature
      const iso3 = f.properties.ISO_A3
      const entry = tempLookup.get(iso3)
      return tempToColor(entry?.latest_temp_change ?? null)
    },
    [tempLookup],
  )

  const getPolygonLabel = useCallback((feature: object) => {
    const f = feature as GeoFeature
    return f.properties.ADMIN
  }, [])

  const handlePolygonClick = useCallback(
    (feature: object) => {
      const f = feature as GeoFeature
      const iso3 = f.properties.ISO_A3
      const entry = tempLookup.get(iso3)
      if (entry) onCountrySelect(entry.id)
    },
    [tempLookup, onCountrySelect],
  )

  const handlePolygonHover = useCallback((feature: object | null) => {
    if (!feature) {
      setHoverName(null)
      return
    }
    const f = feature as GeoFeature
    setHoverName(f.properties.ADMIN)
  }, [])

  return (
    <>
      {loading && (
        <div className="globe-loading">
          <div className="spinner" />
        </div>
      )}
      {hoverName && <div className="globe-tooltip">{hoverName}</div>}
      <ReactGlobe
        ref={globeRef}
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
        polygonsData={countries}
        polygonCapColor={getPolygonColor}
        polygonSideColor={() => 'rgba(0,0,0,0.1)'}
        polygonStrokeColor={() => 'rgba(255,255,255,0.15)'}
        polygonLabel={getPolygonLabel}
        onPolygonClick={handlePolygonClick}
        onPolygonHover={handlePolygonHover}
        polygonsTransitionDuration={300}
        width={window.innerWidth}
        height={window.innerHeight}
        backgroundColor="rgba(0,0,0,1)"
      />
      <style>{`
        .globe-loading {
          position: fixed;
          inset: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0, 0, 0, 0.6);
          z-index: 10;
        }
        .spinner {
          width: 48px;
          height: 48px;
          border: 4px solid rgba(255,255,255,0.2);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .globe-tooltip {
          position: fixed;
          top: 16px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0, 0, 0, 0.75);
          color: #fff;
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 14px;
          pointer-events: none;
          z-index: 5;
          white-space: nowrap;
        }
      `}</style>
    </>
  )
}
