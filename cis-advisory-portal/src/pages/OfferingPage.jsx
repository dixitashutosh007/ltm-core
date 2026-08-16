import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useData } from '../context/DataContext';
import L1Section from '../components/Offering/L1Section';
import L2Section from '../components/Offering/L2Section';
import BattleCard from '../components/Offering/BattleCard';

const TABS = [
  { id: 'l1', label: 'L1 Overview', key: 'l1' },
  { id: 'l2', label: 'L2 Delivery Detail', key: 'l2' },
  { id: 'battle', label: 'Battle Card', key: 'battleCard' },
];

export default function OfferingPage() {
  const { id } = useParams();
  const { getOffering, getVertical } = useData();
  const [activeTab, setActiveTab] = useState('l1');

  const offering = getOffering(id);
  if (!offering) return (
    <div className="detail-content">
      <div className="empty-state">
        <p>Offering not found.</p>
        <Link to="/" className="btn-primary">Back to Dashboard</Link>
      </div>
    </div>
  );

  const vertical = getVertical(offering.verticalId);
  const stageClass = offering.stage.toLowerCase() === 'diagnose' ? 'stage-diagnose'
    : offering.stage.toLowerCase() === 'design' ? 'stage-design'
    : 'stage-mobilise';

  const handleDownload = () => {
    const data = JSON.stringify(offering, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${offering.id}-offering-data.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="offering-detail">
      <div className="offering-hero">
        <div className="breadcrumb">
          <Link to="/">Dashboard</Link>
          <span>/</span>
          {vertical && <span>{vertical.name}</span>}
          <span>/</span>
          <span style={{ color: 'var(--ink)' }}>{offering.name}</span>
        </div>
        <h1>{offering.name}</h1>
        <p className="tagline">{offering.tagline}</p>
        <div className="offering-meta-row">
          <div className="offering-meta-item">
            <span className="meta-label">Pillar</span>
            {offering.pillar}
          </div>
          <div className="offering-meta-item">
            <span className={`meta-badge ${stageClass}`}>{offering.stage}</span>
          </div>
          <div className="offering-meta-item">
            <span className="meta-label">Duration</span>
            {offering.duration}
          </div>
          <div className="offering-meta-item">
            <span className="meta-label">Buyers</span>
            {offering.buyers}
          </div>
          <button className="download-btn" onClick={handleDownload}>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 1.5v9m0 0l3.5-3.5M8 10.5L4.5 7M2 13.5h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Download
          </button>
        </div>
      </div>

      <div className="detail-tabs">
        {TABS.map(tab => {
          const hasData = offering[tab.key] !== null && offering[tab.key] !== undefined;
          return (
            <button
              key={tab.id}
              className={`detail-tab ${activeTab === tab.id ? 'active' : ''} ${!hasData ? 'disabled' : ''}`}
              onClick={() => hasData && setActiveTab(tab.id)}
              title={!hasData ? 'No data available yet' : ''}
            >
              {tab.label}
              {!hasData && <span style={{ fontSize: 10, marginLeft: 4, opacity: 0.5 }}>(empty)</span>}
            </button>
          );
        })}
      </div>

      {activeTab === 'l1' && <L1Section offering={offering} />}
      {activeTab === 'l2' && <L2Section offering={offering} />}
      {activeTab === 'battle' && <BattleCard offering={offering} />}
    </div>
  );
}
