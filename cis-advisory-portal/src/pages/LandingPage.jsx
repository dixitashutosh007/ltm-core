import { Link } from 'react-router-dom';
import { useData } from '../context/DataContext';

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
        {offering.l2 && <span className="meta-badge" style={{ background: '#D1FAE5', color: '#065F46' }}>L2 Ready</span>}
        {offering.battleCard && <span className="meta-badge" style={{ background: '#FEF3C7', color: '#92400E' }}>Battle Card</span>}
      </div>
    </Link>
  );
}

export default function LandingPage() {
  const { verticals, getOfferingsByVertical } = useData();

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
      </div>

      <div className="verticals-container">
        {verticals.map(vertical => {
          const vOfferings = getOfferingsByVertical(vertical.id);
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
      </div>
    </div>
  );
}
