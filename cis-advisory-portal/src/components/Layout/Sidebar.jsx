import { NavLink, useLocation } from 'react-router-dom';
import { useData } from '../../context/DataContext';

export default function Sidebar() {
  const { verticals, methodology } = useData();
  const location = useLocation();
  const isHome = location.pathname === '/';

  const scrollTo = (id) => {
    if (location.pathname === '/') {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <aside className="app-sidebar">
      <div className="sidebar-brand">
        <h2>CIS Tech Advisory</h2>
        <p>Cognitive Infrastructure Services</p>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-title">Navigation</div>
        <ul className="sidebar-nav">
          <li>
            <NavLink to="/" className={isHome ? 'active' : ''}>
              <span className="nav-icon">&#9632;</span>
              Dashboard
            </NavLink>
          </li>
        </ul>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-title">Pillars</div>
        <ul className="sidebar-nav">
          {verticals.map(v => (
            <li key={v.id}>
              <NavLink to={`/#${v.id}`} onClick={() => scrollTo(v.id)}>
                <span className="nav-icon" style={{ color: v.color, fontWeight: 800, fontSize: 11 }}>
                  {v.number}
                </span>
                {v.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-title">More</div>
        <ul className="sidebar-nav">
          <li>
            <a href="/#accelerators" onClick={() => scrollTo('accelerators')}>
              <span className="nav-icon">&#9670;</span>
              Accelerators
            </a>
          </li>
          <li>
            <a href="/#thought" onClick={() => scrollTo('thought')}>
              <span className="nav-icon">&#9679;</span>
              Insights
            </a>
          </li>
          <li>
            <a href="/#partners" onClick={() => scrollTo('partners')}>
              <span className="nav-icon">&#9733;</span>
              Partners
            </a>
          </li>
        </ul>
      </div>

      <div className="methodology-panel">
        <h3>Jump Start Methodology</h3>
        <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 16, marginTop: -8 }}>
          {methodology.tagline}
        </p>
        {methodology.phases.map(phase => (
          <div className="phase-item" key={phase.number}>
            <div className="phase-num">{phase.number}</div>
            <div className="phase-info">
              <h4>{phase.name}</h4>
              <p>{phase.duration}</p>
            </div>
          </div>
        ))}
        <div className="principle-tags">
          {methodology.principles.map(p => (
            <span className="principle-tag" key={p}>{p}</span>
          ))}
        </div>
      </div>
    </aside>
  );
}
