export default function Legend() {
  return (
    <div className="legend">
      <div className="legend__title">Warming Contribution</div>
      <div className="legend__gradient" />
      <div className="legend__labels">
        <span>0°C</span>
        <span>0.15°C</span>
        <span>0.3°C</span>
      </div>
      <div className="legend__scale-note">Log scale</div>
      <div className="legend__no-data">
        <span className="legend__no-data-swatch" />
        <span>No data</span>
      </div>
      <style>{`
        .legend {
          position: fixed;
          bottom: 32px;
          left: 16px;
          background: rgba(30, 30, 40, 0.82);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 6px;
          padding: 10px 14px 8px;
          color: #fff;
          font-size: 11px;
          min-width: 180px;
          z-index: 10;
          user-select: none;
        }
        .legend__title {
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          color: rgba(255,255,255,0.75);
          margin-bottom: 7px;
        }
        .legend__gradient {
          height: 10px;
          border-radius: 3px;
          background: linear-gradient(
            to right,
            rgba(255,255,255,0.75),
            rgba(255,165,0,0.75),
            rgba(255,0,0,0.75)
          );
          margin-bottom: 4px;
        }
        .legend__labels {
          display: flex;
          justify-content: space-between;
          color: rgba(255,255,255,0.6);
          font-size: 10px;
          margin-bottom: 2px;
        }
        .legend__scale-note {
          text-align: center;
          color: rgba(255,255,255,0.35);
          font-size: 9px;
          margin-bottom: 8px;
        }
        .legend__no-data {
          display: flex;
          align-items: center;
          gap: 6px;
          color: rgba(255,255,255,0.5);
          font-size: 10px;
        }
        .legend__no-data-swatch {
          width: 14px;
          height: 10px;
          border-radius: 2px;
          background: rgba(120,120,120,0.7);
          flex-shrink: 0;
        }
      `}</style>
    </div>
  )
}
