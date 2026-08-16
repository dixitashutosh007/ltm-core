import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { useRole } from '../context/RoleContext';
import SearchBar from '../components/common/SearchBar';
import AddOfferingModal from '../components/Editor/AddOfferingModal';

function OfferingCard({ offering }) {
  const stageClass = offering.stage.toLowerCase() === 'diagnose' ? 'stage-diagnose'
    : offering.stage.toLowerCase() === 'design' ? 'stage-design'
    : 'stage-mobilise';

  return (
    <Link to={`/offering/${offering.id}`} className="offering-card">
      <div className="offering-card-header">
        <h3>{offering.name}</h3>
        <span className="offering-card-num">{offering.number.padStart(2, '0')}</span>
      </div>
      <p className="tagline">{offering.tagline}</p>
      <div className="offering-card-meta">
        <span className={`meta-badge ${stageClass}`}>{offering.stage}</span>
        <span className="meta-badge">{offering.duration}</span>
        <span className="meta-badge">{offering.phase}</span>
        {offering.l2 && <span className="meta-badge badge-l2">L2 Ready</span>}
        {offering.battleCard && <span className="meta-badge badge-bc">Battle Card</span>}
      </div>
    </Link>
  );
}

export default function LandingPage() {
  const { verticals, offerings, getOfferingsByVertical } = useData();
  const { isEditor } = useRole();
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  const stats = useMemo(() => ({
    total: offerings.length,
    l2Ready: offerings.filter(o => o.l2).length,
    battleCards: offerings.filter(o => o.battleCard).length,
    verticals: verticals.length,
  }), [offerings, verticals]);

  const filteredOfferings = useMemo(() => {
    const q = search.toLowerCase();
    return offerings.filter(o => {
      if (stageFilter && o.stage.toLowerCase() !== stageFilter.toLowerCase()) return false;
      if (!q) return true;
      return (o.name + o.tagline + o.buyers + o.pillar).toLowerCase().includes(q);
    });
  }, [offerings, search, stageFilter]);

  const filteredVerticals = useMemo(() => {
    if (!search && !stageFilter) return verticals;
    const verticalIds = new Set(filteredOfferings.map(o => o.verticalId));
    return verticals.filter(v => verticalIds.has(v.id));
  }, [verticals, filteredOfferings, search, stageFilter]);

  return (
    <div>
      <div className="landing-hero">
        <div className="eyebrow">CIS Tech Advisory</div>
        <h1>Advisory-led services for cloud, sovereignty &amp; AI.</h1>
        <p>
          Nine advisory offerings engineered for the CIO and CFO room. Fixed cadence,
          fixed deliverables, advisory that leads to action — at roughly one-third of
          Tier-1 consulting fees.
        </p>
        <div className="hero-stats">
          <div className="hero-stat">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Offerings</span>
          </div>
          <div className="hero-stat">
            <span className="stat-value">{stats.verticals}</span>
            <span className="stat-label">Verticals</span>
          </div>
          <div className="hero-stat">
            <span className="stat-value">{stats.l2Ready}</span>
            <span className="stat-label">L2 Ready</span>
          </div>
          <div className="hero-stat">
            <span className="stat-value">{stats.battleCards}</span>
            <span className="stat-label">Battle Cards</span>
          </div>
        </div>
      </div>

      <div className="verticals-container">
        <div className="toolbar">
          <SearchBar value={search} onChange={setSearch} placeholder="Search offerings by name, buyer, pillar..." />
          <div className="toolbar-right">
            <select className="filter-select" value={stageFilter} onChange={e => setStageFilter(e.target.value)}>
              <option value="">All Stages</option>
              <option value="Diagnose">Diagnose</option>
              <option value="Design">Design</option>
              <option value="Mobilise">Mobilise</option>
            </select>
            {isEditor && (
              <button className="btn-primary" onClick={() => setShowAddModal(true)}>
                + Add Offering
              </button>
            )}
          </div>
        </div>

        {filteredVerticals.map(vertical => {
          const vOfferings = (search || stageFilter)
            ? filteredOfferings.filter(o => o.verticalId === vertical.id)
            : getOfferingsByVertical(vertical.id);
          if (vOfferings.length === 0 && (search || stageFilter)) return null;
          return (
            <section className="vertical-section" key={vertical.id} id={vertical.id}>
              <div className="vertical-header">
                <span className="vertical-number">{vertical.number}</span>
                <div className="vertical-info">
                  <h2>{vertical.name}</h2>
                  <p>{vertical.description}</p>
                </div>
              </div>
              <div className="offerings-grid">
                {vOfferings.map(o => <OfferingCard key={o.id} offering={o} />)}
                {vOfferings.length === 0 && (
                  <div className="empty-state">
                    <p>No offerings yet in this vertical.</p>
                  </div>
                )}
              </div>
            </section>
          );
        })}

        {filteredVerticals.length === 0 && (
          <div className="empty-state" style={{ padding: '60px 24px' }}>
            <p>No offerings match your search.</p>
            <button className="download-btn" onClick={() => { setSearch(''); setStageFilter(''); }}>Clear filters</button>
          </div>
        )}
      </div>
      {showAddModal && <AddOfferingModal onClose={() => setShowAddModal(false)} />}
    </div>
  );
}
