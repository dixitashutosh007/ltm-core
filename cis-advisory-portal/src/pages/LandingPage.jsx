import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { useRole } from '../context/RoleContext';
import AddOfferingModal from '../components/Editor/AddOfferingModal';

/* ------------------------------------------------------------------ */
/* Offering visuals — one hand-drawn SVG illustration per offering id  */
/* ------------------------------------------------------------------ */

const OFFERING_VISUALS = {
  'it-for-the-future': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Horizon arc with three milestones">
      <rect width="400" height="300" fill="#f4f4f3" />
      <path d="M40 240 Q200 40, 360 240" fill="none" stroke="#141414" strokeWidth="1.5" opacity="0.4" />
      <circle cx="120" cy="165" r="10" fill="#141414" />
      <circle cx="200" cy="90" r="12" fill="#ff5e4f" />
      <circle cx="280" cy="165" r="10" fill="#ffb4ac" />
      <line x1="40" y1="260" x2="360" y2="260" stroke="#141414" strokeWidth="1" opacity="0.3" />
    </svg>
  ),
  'target-operating-model': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Operating model organisation chart">
      <rect width="400" height="300" fill="#f4f4f3" />
      <rect x="160" y="55" width="80" height="40" fill="#141414" />
      <line x1="200" y1="95" x2="200" y2="120" stroke="#141414" strokeWidth="1.5" opacity="0.5" />
      <line x1="90" y1="120" x2="310" y2="120" stroke="#141414" strokeWidth="1.5" opacity="0.5" />
      <line x1="90" y1="120" x2="90" y2="145" stroke="#141414" strokeWidth="1.5" opacity="0.5" />
      <line x1="200" y1="120" x2="200" y2="145" stroke="#141414" strokeWidth="1.5" opacity="0.5" />
      <line x1="310" y1="120" x2="310" y2="145" stroke="#141414" strokeWidth="1.5" opacity="0.5" />
      <rect x="55" y="145" width="70" height="36" fill="#ffb4ac" />
      <rect x="165" y="145" width="70" height="36" fill="#ff5e4f" />
      <rect x="275" y="145" width="70" height="36" fill="#ffb4ac" />
      <rect x="55" y="205" width="70" height="36" fill="#141414" opacity="0.55" />
      <rect x="165" y="205" width="70" height="36" fill="#141414" opacity="0.55" />
      <rect x="275" y="205" width="70" height="36" fill="#141414" opacity="0.55" />
    </svg>
  ),
  'technical-debt-portfolio': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Technical debt portfolio bars">
      <rect width="400" height="300" fill="#f4f4f3" />
      <line x1="40" y1="260" x2="360" y2="260" stroke="#141414" strokeWidth="1" opacity="0.3" />
      <rect x="70" y="140" width="40" height="120" fill="#141414" opacity="0.65" />
      <rect x="70" y="110" width="40" height="30" fill="#ff5e4f" />
      <rect x="140" y="170" width="40" height="90" fill="#141414" opacity="0.55" />
      <rect x="140" y="150" width="40" height="20" fill="#ffb4ac" />
      <rect x="210" y="90" width="40" height="170" fill="#141414" opacity="0.75" />
      <rect x="210" y="60" width="40" height="30" fill="#ff5e4f" />
      <rect x="280" y="190" width="40" height="70" fill="#141414" opacity="0.5" />
      <rect x="280" y="175" width="40" height="15" fill="#ffb4ac" />
    </svg>
  ),
  'right-cloud-strategy-workload-placement': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Workload placement grid">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g stroke="#141414" strokeWidth="1" fill="none" opacity="0.35">
        <line x1="0" y1="75" x2="400" y2="75" /><line x1="0" y1="150" x2="400" y2="150" /><line x1="0" y1="225" x2="400" y2="225" />
        <line x1="100" y1="0" x2="100" y2="300" /><line x1="200" y1="0" x2="200" y2="300" /><line x1="300" y1="0" x2="300" y2="300" />
      </g>
      <circle cx="150" cy="112" r="18" fill="#141414" />
      <circle cx="250" cy="112" r="12" fill="#ff5e4f" />
      <circle cx="350" cy="187" r="16" fill="#141414" />
      <circle cx="50" cy="187" r="14" fill="#ffb4ac" />
      <rect x="120" y="82" width="60" height="60" fill="none" stroke="#ff5e4f" strokeWidth="1.5" strokeDasharray="3 3" />
    </svg>
  ),
  'finops-excellence': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="FinOps maturity trajectory">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g stroke="#141414" strokeWidth="1" opacity="0.3"><line x1="40" y1="260" x2="360" y2="260" /><line x1="40" y1="260" x2="40" y2="40" /></g>
      <path d="M40 240 Q120 220, 160 180 T280 100 T360 60" fill="none" stroke="#ff5e4f" strokeWidth="3" strokeLinecap="round" />
      <g fill="#141414"><circle cx="80" cy="230" r="5" /><circle cx="160" cy="180" r="5" /><circle cx="240" cy="130" r="5" /><circle cx="320" cy="80" r="5" /></g>
      <circle cx="360" cy="60" r="7" fill="#ffb4ac" />
    </svg>
  ),
  'ai-ready-cloud-foundations': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Layered cloud foundation">
      <rect width="400" height="300" fill="#f4f4f3" />
      <rect x="60" y="200" width="280" height="50" fill="#141414" opacity="0.85" />
      <rect x="80" y="145" width="240" height="45" fill="#141414" opacity="0.65" />
      <rect x="100" y="95" width="200" height="40" fill="#141414" opacity="0.45" />
      <circle cx="200" cy="60" r="22" fill="#ffb4ac" />
      <circle cx="200" cy="60" r="12" fill="#ff5e4f" />
    </svg>
  ),
  'cloud-strategy-adoption-roadmap': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Phased roadmap">
      <rect width="400" height="300" fill="#f4f4f3" />
      <line x1="50" y1="150" x2="350" y2="150" stroke="#141414" strokeWidth="1.5" opacity="0.4" />
      <circle cx="100" cy="150" r="10" fill="#141414" />
      <circle cx="200" cy="150" r="10" fill="#ff5e4f" />
      <circle cx="300" cy="150" r="10" fill="#ffb4ac" />
    </svg>
  ),
  'ai-powered-well-architected-review': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Six-pillar hexagon">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g transform="translate(200,150)">
        <polygon points="0,-90 78,-45 78,45 0,90 -78,45 -78,-45" fill="none" stroke="#141414" strokeWidth="1.2" opacity="0.4" />
        <polygon points="0,-70 60,-35 40,25 0,55 -55,30 -65,-40" fill="rgba(255,94,79,0.2)" stroke="#ff5e4f" strokeWidth="1.75" />
      </g>
    </svg>
  ),
  'quick-sovereignty-posture-assessment': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Seven-lens compass">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g transform="translate(200,150)">
        <circle r="95" fill="none" stroke="#141414" strokeWidth="1" opacity="0.35" />
        <circle r="65" fill="none" stroke="#141414" strokeWidth="1" opacity="0.25" />
        <g stroke="#141414" strokeWidth="1" opacity="0.4">
          <line x1="0" y1="-95" x2="0" y2="95" /><line x1="-95" y1="0" x2="95" y2="0" />
          <line x1="-67" y1="-67" x2="67" y2="67" /><line x1="67" y1="-67" x2="-67" y2="67" />
        </g>
        <circle r="12" fill="#ff5e4f" />
      </g>
    </svg>
  ),
  'cross-border-data-strategy': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cross-border data flow between regions">
      <rect width="400" height="300" fill="#f4f4f3" />
      <circle cx="105" cy="150" r="55" fill="none" stroke="#141414" strokeWidth="1.5" opacity="0.55" />
      <circle cx="295" cy="150" r="55" fill="none" stroke="#141414" strokeWidth="1.5" opacity="0.55" />
      <circle cx="105" cy="150" r="14" fill="#141414" />
      <circle cx="295" cy="150" r="14" fill="#ff5e4f" />
      <path d="M160 130 Q200 90, 240 130" fill="none" stroke="#ff5e4f" strokeWidth="2" strokeDasharray="5 4" />
      <path d="M240 170 Q200 210, 160 170" fill="none" stroke="#141414" strokeWidth="2" opacity="0.55" strokeDasharray="5 4" />
      <polygon points="235,126 245,132 233,138" fill="#ff5e4f" />
      <polygon points="165,174 155,168 167,162" fill="#141414" opacity="0.55" />
    </svg>
  ),
  'sovereignty-readiness-assessment': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Risk register grid">
      <rect width="400" height="300" fill="#f4f4f3" />
      <rect x="52" y="62" width="146" height="91" fill="#ffb4ac" opacity="0.45" />
      <rect x="202" y="62" width="146" height="91" fill="#ff5e4f" opacity="0.7" />
      <rect x="52" y="157" width="146" height="91" fill="#141414" opacity="0.15" />
      <rect x="202" y="157" width="146" height="91" fill="#ffb4ac" opacity="0.35" />
    </svg>
  ),
  'app-portfolio-mapping': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Application portfolio waves">
      <rect width="400" height="300" fill="#f4f4f3" />
      <rect x="30" y="60" width="340" height="50" fill="#141414" opacity="0.1" />
      <rect x="30" y="125" width="340" height="50" fill="#141414" opacity="0.1" />
      <rect x="30" y="190" width="340" height="50" fill="#141414" opacity="0.1" />
    </svg>
  ),
  'regulatory-alignment-exit-strategy': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Regulatory alignment framework">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g transform="translate(200,150)">
        <path d="M0,-70 L50,-50 L50,20 Q50,55 0,70 Q-50,55 -50,20 L-50,-50 Z" fill="#141414" />
      </g>
    </svg>
  ),
  'sovereign-ai-readiness': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sovereign AI stack across jurisdictions">
      <rect width="400" height="300" fill="#f4f4f3" />
      <rect x="60" y="205" width="280" height="45" fill="#141414" opacity="0.85" />
      <rect x="80" y="150" width="240" height="45" fill="#141414" opacity="0.6" />
      <rect x="100" y="95" width="200" height="45" fill="#ffb4ac" opacity="0.85" />
      <circle cx="200" cy="60" r="16" fill="#ff5e4f" />
      <line x1="80" y1="80" x2="80" y2="260" stroke="#141414" strokeWidth="1" opacity="0.35" strokeDasharray="3 3" />
      <line x1="320" y1="80" x2="320" y2="260" stroke="#141414" strokeWidth="1" opacity="0.35" strokeDasharray="3 3" />
    </svg>
  ),
  'ai-opportunity-value-advisory': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Use-case value quadrant">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g stroke="#141414" strokeWidth="1" opacity="0.35"><line x1="60" y1="150" x2="340" y2="150" /><line x1="200" y1="50" x2="200" y2="250" /></g>
      <circle cx="260" cy="200" r="22" fill="#ff5e4f" opacity="0.85" />
      <circle cx="290" cy="180" r="15" fill="#ffb4ac" opacity="0.85" />
      <circle cx="245" cy="215" r="11" fill="#141414" />
    </svg>
  ),
  'ai-readiness-data-foundation-assessment': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Data foundation readiness">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g transform="translate(200,180)">
        <ellipse cx="0" cy="-40" rx="70" ry="15" fill="#141414" />
        <rect x="-70" y="-40" width="140" height="70" fill="#141414" />
        <ellipse cx="0" cy="30" rx="70" ry="15" fill="#0d0d0d" />
      </g>
    </svg>
  ),
  'responsible-ai-governance-advisory': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Risk tiers">
      <rect width="400" height="300" fill="#f4f4f3" />
      <polygon points="200,55 240,110 160,110" fill="#ff5e4f" />
      <polygon points="160,110 240,110 275,175 125,175" fill="#ffb4ac" />
      <polygon points="125,175 275,175 320,250 80,250" fill="#141414" />
    </svg>
  ),
  'ai-cost-finops-for-ai': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AI cost per token trend">
      <rect width="400" height="300" fill="#f4f4f3" />
      <path d="M50 220 Q120 200, 160 165 T280 90 T360 40" fill="none" stroke="#ff5e4f" strokeWidth="2.5" strokeDasharray="6 4" />
      <path d="M50 220 Q120 210, 160 195 T280 165 T360 145" fill="none" stroke="#141414" strokeWidth="2.5" />
    </svg>
  ),
  'tokenops-genai-governance': (
    <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Token flow throttled by governance">
      <rect width="400" height="300" fill="#f4f4f3" />
      <g stroke="#141414" strokeWidth="1" opacity="0.3">
        <line x1="40" y1="260" x2="360" y2="260" /><line x1="40" y1="260" x2="40" y2="40" />
      </g>
      <path d="M40 240 Q90 100, 200 70 T360 60" fill="none" stroke="#141414" strokeWidth="2" strokeDasharray="5 4" opacity="0.55" />
      <path d="M40 240 Q90 200, 200 175 T360 155" fill="none" stroke="#ff5e4f" strokeWidth="2.5" />
      <circle cx="200" cy="175" r="8" fill="#ff5e4f" />
      <line x1="200" y1="55" x2="200" y2="260" stroke="#141414" strokeWidth="1" opacity="0.4" strokeDasharray="3 3" />
      <text x="205" y="70" fill="#141414" opacity="0.55" fontFamily="Inter,sans-serif" fontSize="10">quota</text>
    </svg>
  ),
};

const FALLBACK_VISUAL = (
  <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Advisory offering">
    <rect width="400" height="300" fill="#f4f4f3" />
    <circle cx="200" cy="150" r="60" fill="none" stroke="#ff5e4f" strokeWidth="1.75" opacity="0.75" />
    <circle cx="200" cy="150" r="14" fill="#ff5e4f" />
  </svg>
);

/* ------------------------------------------------------------------ */
/* Tab configuration — display order and copy matched to the v3 brief  */
/* ------------------------------------------------------------------ */

const TAB_LABELS = {
  'enterprise-it-strategy': 'IT Strategy',
  'public-cloud': 'Public Cloud',
  'digital-sovereignty': 'Digital Sovereignty',
  'ai-infusion': 'AI Infusion',
};

const TAB_ORDER = {
  'enterprise-it-strategy': ['it-for-the-future', 'target-operating-model', 'technical-debt-portfolio'],
  'public-cloud': ['right-cloud-strategy-workload-placement', 'finops-excellence', 'ai-ready-cloud-foundations', 'cloud-strategy-adoption-roadmap', 'ai-powered-well-architected-review'],
  'digital-sovereignty': ['quick-sovereignty-posture-assessment', 'cross-border-data-strategy', 'sovereignty-readiness-assessment', 'app-portfolio-mapping', 'regulatory-alignment-exit-strategy', 'sovereign-ai-readiness'],
  'ai-infusion': ['ai-opportunity-value-advisory', 'ai-readiness-data-foundation-assessment', 'responsible-ai-governance-advisory', 'ai-cost-finops-for-ai', 'tokenops-genai-governance'],
};

const TAB_INTRO_COPY = {
  'enterprise-it-strategy': 'IT strategy is where the board conversation actually starts — the 3–5 year direction, the operating model that will support it, and the debt that will hold it back. Advisory that sets the horizon, designs the organisation to reach it, and quantifies the technical debt to be paid down along the way — the front door through which cloud, sovereignty and AI decisions all connect.',
  'public-cloud': 'Turn cloud from a technology footprint into a governed source of business value. From the anchor-cloud decision to workload placement, FinOps, AI-ready foundations and architectural health — advisory that decides what runs where, spends intelligently on every dollar and every token, and modernises with a plan the board can fund.',
  'digital-sovereignty': 'Sovereignty is now a board-level operating question, not a compliance footnote. With DORA, NIS2 and the EU AI Act converging through 2026, advisory that answers it clearly — where the organisation stands, what to do about it, and how to keep data, systems and operations under control if regulatory or geopolitical conditions change.',
  'ai-infusion': 'Turn scattered AI experiments into a prioritised, funded and governed adoption path. Advisory that identifies where GenAI and agentic AI will move the numbers, assesses whether the data and cloud foundation can support them, and builds the responsible-AI guardrails needed for a 2026 regulatory environment.',
};

function OfferingRow({ offering, index }) {
  const visual = OFFERING_VISUALS[offering.id] || FALLBACK_VISUAL;
  const isReverse = index % 2 === 1;
  const content = (
    <>
      <h3>{offering.name}</h3>
      <ul>
        {(offering.bullets || []).map((b, i) => <li key={i}>{b}</li>)}
      </ul>
    </>
  );
  return (
    <article className={`v3-offering${isReverse ? ' reverse' : ''}`}>
      <div className="v3-offering-visual">{visual}</div>
      <div className="v3-offering-content">
        {offering.l1 ? <Link to={`/offering/${offering.id}`}>{content}</Link> : content}
      </div>
    </article>
  );
}

export default function LandingPage() {
  const { verticals, offerings, accelerators, insights, partners, getOfferingsByVertical } = useData();
  const { isEditor } = useRole();
  const [activeTab, setActiveTab] = useState(verticals[0]?.id);
  const [showAddModal, setShowAddModal] = useState(false);
  const tabRefs = useRef([]);
  const scrollerRef = useRef(null);

  const activeVertical = verticals.find(v => v.id === activeTab) || verticals[0];

  const offeringsForVertical = (verticalId) => {
    const order = TAB_ORDER[verticalId] || [];
    const ordered = order.map(id => offerings.find(o => o.id === id)).filter(Boolean);
    const orderedIds = new Set(ordered.map(o => o.id));
    const rest = getOfferingsByVertical(verticalId).filter(o => !orderedIds.has(o.id));
    return [...ordered, ...rest];
  };

  const handleTabKeyDown = (e, idx) => {
    let nextIdx = null;
    if (e.key === 'ArrowRight') nextIdx = (idx + 1) % verticals.length;
    else if (e.key === 'ArrowLeft') nextIdx = (idx - 1 + verticals.length) % verticals.length;
    else if (e.key === 'Home') nextIdx = 0;
    else if (e.key === 'End') nextIdx = verticals.length - 1;
    if (nextIdx !== null) {
      e.preventDefault();
      setActiveTab(verticals[nextIdx].id);
      tabRefs.current[nextIdx]?.focus();
    }
  };

  const scrollThought = (dir) => {
    const scroller = scrollerRef.current;
    if (!scroller) return;
    const card = scroller.querySelector('.v3-thought-card');
    const step = card ? card.getBoundingClientRect().width + 20 : 300;
    scroller.scrollBy({ left: dir * step, behavior: 'smooth' });
  };

  if (!activeVertical) return null;

  return (
    <div>
      {isEditor && (
        <div style={{ padding: '10px 24px', background: '#fff', borderBottom: '1px solid var(--line)', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn-primary" onClick={() => setShowAddModal(true)}>+ Add Offering</button>
        </div>
      )}

      {/* Hero */}
      <section className="landing-hero" aria-labelledby="hero-title">
        <div className="hero-inner">
          <div>
            <span className="eyebrow">CIS Tech Advisory</span>
            <p className="tagline-line">It's time to Out Create.</p>
            <h1 id="hero-title">Out Create clarity, control and <em>cloud value.</em></h1>
            <p className="hero-tagline">Advisory that leads to action — helping CIOs, CTOs and CDOs decide what to do about cloud, sovereignty and AI, then delivering the plan.</p>
            <div className="hero-ctas">
              <a href="CIS-Tech-Consulting-Brochure.pdf" className="brochure-btn" download>
                Download Brochure
                <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 1.5v9m0 0l3.5-3.5M8 10.5L4.5 7M2 13.5h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </a>
              <a href="#accelerators" className="ghost-btn">
                Explore Accelerators
                <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 8h12m0 0L9 3m5 5l-5 5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </a>
            </div>
          </div>
          <div className="hero-index" aria-hidden="true">
            <span className="num">{String(verticals.length).padStart(2, '0')}</span>
            <span className="label">Live Advisory<br />Pillars</span>
          </div>
        </div>
      </section>

      {/* Intro / Brief */}
      <section className="v3-intro" aria-labelledby="intro-title">
        <div className="v3-intro-inner">
          <div className="v3-intro-label" id="intro-title">The Brief</div>
          <p>Enterprise IT is now a board-level conversation — regulatory, economic and architectural at once. CIS Tech Advisory helps enterprises <em>Out Create</em> the answer: where the estate stands today, what to do about it, and how to keep control of data, systems and spend as the environment changes.</p>
        </div>
      </section>

      {/* Tabs */}
      <div className="v3-tabs" role="tablist" aria-label="CIS Tech Advisory offerings">
        <div className="v3-tabs-inner">
          {verticals.map((v, idx) => (
            <button
              key={v.id}
              ref={el => { tabRefs.current[idx] = el; }}
              role="tab"
              id={`tab-${v.id}`}
              aria-controls={`panel-${v.id}`}
              aria-selected={activeTab === v.id}
              tabIndex={activeTab === v.id ? 0 : -1}
              className={`tab-btn${activeTab === v.id ? ' active' : ''}`}
              onClick={() => setActiveTab(v.id)}
              onKeyDown={e => handleTabKeyDown(e, idx)}
            >
              <span className="tab-num">{v.number}</span> {TAB_LABELS[v.id] || v.name}
            </button>
          ))}
        </div>
      </div>

      {/* Active tab panel */}
      <section id={`panel-${activeVertical.id}`} role="tabpanel" aria-labelledby={`tab-${activeVertical.id}`} className="tab-panel">
        <div className="tab-intro">
          <div className="tab-intro-inner">
            <div className="tab-intro-label">{activeVertical.name}{activeVertical.tagline ? ` · ${activeVertical.tagline}` : ''}</div>
            <p>{TAB_INTRO_COPY[activeVertical.id] || activeVertical.description}</p>
          </div>
        </div>
        <div className="v3-offerings">
          <div className="v3-offerings-inner">
            {offeringsForVertical(activeVertical.id).map((offering, idx) => (
              <OfferingRow key={offering.id} offering={offering} index={idx} />
            ))}
          </div>
        </div>
      </section>

      {/* Accelerators */}
      <section className="v3-accelerators" id="accelerators" aria-labelledby="accel-title">
        <div className="v3-accelerators-inner">
          <div className="v3-accel-header">
            <div className="v3-accel-label">Accelerators</div>
            <div>
              <h2 id="accel-title">Tools that help you Out Create the answer</h2>
              <p className="v3-accel-lead">Every engagement is backed by a suite of in-house accelerators — purpose-built to compress diagnostic time, sharpen recommendations, and give clients working artefacts they can use long after the engagement ends. Several are available now as free, guided self-assessments.</p>
            </div>
          </div>

          <div className="v3-accel-grid">
            {accelerators.map(accel => (
              <article className="v3-accel" key={accel.number}>
                <div className="v3-accel-num">{accel.number}</div>
                <div>
                  <h3>{accel.name} {accel.badge && <span className="v3-accel-badge">{accel.badge}</span>}</h3>
                  <p>{accel.description}</p>
                  {accel.type === 'tool' && accel.url ? (
                    <a className="v3-accel-link" href={accel.url} target="_blank" rel="noopener noreferrer">
                      Launch tool
                      <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 3h7v7M13 3L6 10M11 8v5H3V5h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    </a>
                  ) : (
                    <span className="v3-accel-link muted">Available with engagement</span>
                  )}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Thought Leadership */}
      <section className="v3-thought" id="thought" aria-labelledby="thought-title">
        <div className="v3-thought-header">
          <div className="v3-thought-label">Insights</div>
          <h2 id="thought-title">Thought leadership that helps you <em>Out Create</em></h2>
          <div className="v3-thought-controls">
            <button className="v3-thought-btn" aria-label="Scroll insights left" onClick={() => scrollThought(-1)}>
              <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10 3L5 8l5 5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
            <button className="v3-thought-btn" aria-label="Scroll insights right" onClick={() => scrollThought(1)}>
              <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 3l5 5-5 5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
          </div>
        </div>

        <div className="v3-thought-scroller" ref={scrollerRef} tabIndex={0} aria-label="Thought leadership carousel">
          {insights.map((item, i) => (
            <a className="v3-thought-card" href={item.url} target="_blank" rel="noopener noreferrer" key={i}>
              <div className={`v3-thought-cover${item.coverClass ? ` ${item.coverClass}` : ''}`}>
                <span className="cover-tag">{item.coverTag}</span>
                <div className="cover-title">{item.coverTitle}</div>
              </div>
              <div className="v3-thought-body">
                <div className="v3-thought-meta">{item.type} · {item.source}</div>
                <h3>{item.title}</h3>
                <p>{item.excerpt}</p>
                <span className="read-more">Read on {new URL(item.url).hostname.replace('www.', '')} →</span>
              </div>
            </a>
          ))}
        </div>
      </section>

      {/* Key Partnerships */}
      <section className="v3-partners" aria-labelledby="partners-title">
        <div className="v3-partners-inner">
          <div className="v3-partners-header">
            <div className="v3-partners-label">Partnerships</div>
            <div>
              <h2 id="partners-title">Key partners we Out Create with</h2>
              <p>Advisory backed by deep, hands-on partnerships across hyperscalers, platform vendors and sovereign cloud specialists.</p>
            </div>
          </div>

          <div className="v3-partner-strip">
            {partners.map(p => (
              <div className="v3-partner" key={p.name}>{p.name}<span className="p-sub">{p.category}</span></div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="v3-cta" id="cta" aria-labelledby="cta-title">
        <div className="v3-cta-inner">
          <div>
            <h2 id="cta-title">Ready to <em>Out Create</em> your next move?</h2>
            <p>Connect with our CIS Tech Advisory team. One week to a first read on your estate — no commitment beyond a conversation.</p>
          </div>
          <a href="mailto:cistechadvisory@ltm.com" className="v3-cta-btn">
            Connect with our team
            <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 8h12m0 0L9 3m5 5l-5 5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="v3-footer">
        <div className="v3-footer-inner">
          <div className="foot-brand">
            <span className="logo-text">LTM</span>
            <span>© LTM · CIS Tech Advisory</span>
          </div>
          <div className="foot-tag">It's time to Out Create</div>
          <div>An L&amp;T Group Company</div>
        </div>
      </footer>

      {showAddModal && <AddOfferingModal onClose={() => setShowAddModal(false)} />}
    </div>
  );
}
