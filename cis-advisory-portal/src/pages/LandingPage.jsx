import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { useRole } from '../context/RoleContext';
import SearchBar from '../components/common/SearchBar';
import AddOfferingModal from '../components/Editor/AddOfferingModal';

function OfferingCard({ offering, pillarColor }) {
  return (
    <Link to={`/offering/${offering.id}`} className="offering-card">
      <div className="offering-card-header">
        <h3>{offering.name}</h3>
        <span className="offering-card-num" style={{ color: pillarColor, background: pillarColor + '14' }}>
          {offering.number.padStart(2, '0')}
        </span>
      </div>
      <p className="tagline">{offering.tagline}</p>
      {offering.poweredBy && offering.poweredBy.length > 0 ? (
        <div className="card-accels">
          <span className="card-accels-lbl">Powered by</span>
          {offering.poweredBy.map(a => <span className="accel-chip" key={a}>{a}</span>)}
        </div>
      ) : (
        <div className="card-accels">
          <span className="card-accels-lbl">Powered by</span>
          <span className="accel-chip methodology">methodology-led</span>
        </div>
      )}
    </Link>
  );
}

function AcceleratorCard({ accel }) {
  return (
    <div className="accel-card-item">
      <span className={`accel-label ${accel.type}`}>
        {accel.type === 'free' ? 'Free' : 'Available with engagement'}
      </span>
      <div className="accel-num">{accel.number.padStart(2, '0')} / {accel.name}</div>
      <h4>{accel.title}</h4>
      <p className="accel-desc">{accel.description}</p>
      {accel.url ? (
        <a href={accel.url} className="accel-cta" target="_blank" rel="noopener noreferrer">
          Try {accel.name} <span>→</span>
        </a>
      ) : (
        <span className="accel-cta placeholder">
          {accel.type === 'free' ? 'Coming soon' : 'Available with engagement'}
        </span>
      )}
    </div>
  );
}

function InsightCard({ insight }) {
  return (
    <a className="insight-card" href={insight.url} target="_blank" rel="noopener noreferrer">
      <div className="insight-meta">
        <span className="insight-type">{insight.type}</span>
        <span>{insight.source}</span>
      </div>
      <h4>{insight.title}</h4>
      <p className="insight-excerpt">{insight.excerpt}</p>
      <span className="insight-read">Read on {insight.source.split(' ·')[0].toLowerCase()}.com →</span>
    </a>
  );
}

export default function LandingPage() {
  const { verticals, offerings, accelerators, insights, partners, getOfferingsByVertical } = useData();
  const { isEditor } = useRole();
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  const stats = useMemo(() => ({
    pillars: verticals.length,
    total: offerings.length,
    accelCount: accelerators ? accelerators.length : 0,
  }), [offerings, verticals, accelerators]);

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
      <div className="landing-hero dark-hero">
        <div className="hero-in">
          <div className="eyebrow"><span className="hero-dot" /> Infra Tech Advisory · Part of Cognitive Infrastructure Services</div>
          <h1>Shape the intelligent core.<br />Turn IT cost, resilience and AI into <em>advantage.</em></h1>
          <p className="hero-sub">
            Advisory that leads to action — helping CIOs, CTOs and CDOs decide what to do about their estate,
            sovereignty, cloud and AI, then delivering the plan that gets there.
          </p>
          <div className="hero-ctas">
            <a href="#accelerators" className="btn-hero-ghost">Explore Accelerators <span>→</span></a>
          </div>
          <div className="hero-parent">
            <span>Part of <b>Cognitive Infrastructure Services</b> · LTIMindtree</span>
            <span>Four pillars · {stats.total} offerings · {stats.accelCount} branded accelerators</span>
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
                <span className="vertical-number" style={{ color: vertical.color }}>{vertical.number}</span>
                <div className="vertical-info">
                  <h2>{vertical.name}</h2>
                  <p>{vertical.description}</p>
                </div>
              </div>
              <div className="offerings-grid">
                {vOfferings.map(o => <OfferingCard key={o.id} offering={o} pillarColor={vertical.color} />)}
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

      {accelerators && accelerators.length > 0 && (
        <section className="section-full" id="accelerators">
          <div className="section-inner">
            <div className="section-eyebrow-alt">Proprietary IP</div>
            <h2 className="section-title-alt">Twelve branded accelerators, four free to try</h2>
            <p className="section-lede-alt">Every accelerator is proprietary LTIMindtree IP — either free lead-in diagnostics that produce evidence in hours, or engagement-gated tools that come with an advisory partnership.</p>
            <div className="accel-grid">
              {accelerators.map(a => <AcceleratorCard key={a.id} accel={a} />)}
            </div>
          </div>
        </section>
      )}

      {insights && insights.length > 0 && (
        <section className="section-full section-white" id="insights">
          <div className="section-inner">
            <div className="section-eyebrow-alt">Points of View</div>
            <h2 className="section-title-alt">Latest thinking from LTIMindtree Infra Tech Advisory</h2>
            <p className="section-lede-alt">Published perspectives from our advisors, featured across LTIMindtree, CIO.com and industry stages.</p>
            <div className="insights-grid">
              {insights.map(i => <InsightCard key={i.id} insight={i} />)}
            </div>
          </div>
        </section>
      )}

      {partners && partners.length > 0 && (
        <section className="section-full" id="partners">
          <div className="section-inner">
            <div className="section-eyebrow-alt">Our Partner Ecosystem</div>
            <h2 className="section-title-alt">Advisory grounded in the platforms our clients rely on</h2>
            <div className="partners-grid">
              {partners.map(p => (
                <div className="partner-card" key={p.id}>
                  <div className="partner-name">{p.name}</div>
                  <div className="partner-cat">{p.category}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {showAddModal && <AddOfferingModal onClose={() => setShowAddModal(false)} />}
    </div>
  );
}
