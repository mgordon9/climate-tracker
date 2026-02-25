import { useEffect, useRef, useState, useCallback } from 'react'
import ReactGlobe, { GlobeMethods } from 'react-globe.gl'
import { feature } from 'topojson-client'
import type { Topology, GeometryCollection } from 'topojson-specification'
import * as isoCountries from 'i18n-iso-countries'
import { fetchGlobeData, GlobeCountry } from '../api'

interface GlobeProps {
  onCountrySelect: (id: number) => void
}

interface GeoFeature {
  type: string
  id?: string | number
  properties: Record<string, string>
  geometry: object
}

function tempToColor(temp: number | null): string {
  if (temp === null) return 'rgba(120, 120, 120, 0.7)'

  // Map temp range [-0.5, 3.0] to [0, 1]
  const min = -0.5
  const max = 3.0
  const t = Math.max(0, Math.min(1, (temp - min) / (max - min)))

  // Blue → White → Red
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
      fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
        .then((r) => r.json())
        .then((topo: Topology) => {
          const geojson = feature(
            topo,
            topo.objects['countries'] as GeometryCollection,
          )
          return geojson.features as GeoFeature[]
        }),
      fetchGlobeData(),
    ])
      .then(([features, globeData]) => {
        const lookup = new Map<string, GlobeCountry>()
        for (const c of globeData) {
          if (c.iso3_code) lookup.set(c.iso3_code, c)
        }
        setTempLookup(lookup)
        setCountries(features)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to load globe data', err)
        setLoading(false)
      })
  }, [])

  const getIso3 = useCallback((feature: GeoFeature): string | undefined => {
    return isoCountries.numericToAlpha3(String(feature.id)) || undefined
  }, [])

  const getPolygonColor = useCallback(
    (feature: object) => {
      const iso3 = getIso3(feature as GeoFeature)
      if (!iso3) return 'rgba(120,120,120,0.7)'
      const entry = tempLookup.get(iso3)
      return tempToColor(entry?.latest_temp_change ?? null)
    },
    [tempLookup, getIso3],
  )

  const getPolygonLabel = useCallback(
    (feature: object) => {
      const f = feature as GeoFeature
      const iso3 = getIso3(f)
      if (!iso3) return ''
      const entry = tempLookup.get(iso3)
      return entry?.name ?? ''
    },
    [tempLookup, getIso3],
  )

  const handlePolygonClick = useCallback(
    (feature: object) => {
      const iso3 = getIso3(feature as GeoFeature)
      if (!iso3) return
      const entry = tempLookup.get(iso3)
      if (entry) onCountrySelect(entry.id)
    },
    [tempLookup, getIso3, onCountrySelect],
  )

  const handlePolygonHover = useCallback(
    (feature: object | null) => {
      if (!feature) {
        setHoverName(null)
        return
      }
      const iso3 = getIso3(feature as GeoFeature)
      const entry = iso3 ? tempLookup.get(iso3) : undefined
      setHoverName(entry?.name ?? null)
    },
    [tempLookup, getIso3],
  )

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
