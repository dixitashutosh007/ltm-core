import EditableText from '../common/EditableText';
import EditableList from '../common/EditableList';
import { useData } from '../../context/DataContext';

export default function BattleCard({ offering }) {
  const { updateOfferingField } = useData();
  const bc = offering.battleCard;
  if (!bc) return (
    <div className="detail-content">
      <div className="empty-state">
        <p>Battle Card not yet available for this offering.</p>
        <p style={{ fontSize: 13, color: 'var(--muted)' }}>Switch to Editor mode to add Battle Card content.</p>
      </div>
    </div>
  );

  const update = (field, value) => updateOfferingField(offering.id, `battleCard.${field}`, value);

  return (
    <div className="detail-content">
      <div className="battle-card-hero">
        <div className="bc-stat">
          <div className="value">{bc.targetBuyer.split(' · ')[0]}</div>
          <div className="label">Primary Buyer</div>
        </div>
        <div className="bc-stat">
          <div className="value">{bc.dealSize.split('|')[0].trim()}</div>
          <div className="label">Typical Deal Size</div>
        </div>
        <div className="bc-stat">
          <div className="value">{bc.salesCycle}</div>
          <div className="label">Sales Cycle</div>
        </div>
      </div>

      <div className="section-block">
        <h2>The Pitch</h2>
        <div className="pitch-box">
          <EditableText value={bc.pitch} onChange={v => update('pitch', v)} multiline />
        </div>
        {bc.proofPoints && bc.proofPoints.length > 0 && (
          <div className="proof-points">
            {bc.proofPoints.map((pp, i) => (
              <div className="proof-point" key={i}>
                <div className="stat">{pp.stat}</div>
                <div className="label">{pp.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="two-col">
        <div className="section-block">
          <h2>Discovery Questions</h2>
          <EditableList items={bc.discoveryQuestions} onChange={v => update('discoveryQuestions', v)} />
        </div>
        <div>
          <div className="section-block">
            <h3 style={{ color: '#059669' }}>Qualify In</h3>
            <EditableList items={bc.qualifyIn} onChange={v => update('qualifyIn', v)} />
          </div>
          <div className="section-block">
            <h3 style={{ color: 'var(--coral)' }}>Qualify Out</h3>
            <EditableList items={bc.qualifyOut} onChange={v => update('qualifyOut', v)} />
          </div>
        </div>
      </div>

      {bc.pricingGuardrail && (
        <div className="section-block" style={{ background: 'var(--coral-tint)', border: '1.5px solid var(--coral-light)' }}>
          <h2 style={{ fontSize: 12, letterSpacing: 1, textTransform: 'uppercase', color: 'var(--coral-deep)' }}>
            Pricing Guardrail
          </h2>
          <EditableText value={bc.pricingGuardrail} onChange={v => update('pricingGuardrail', v)} />
        </div>
      )}

      {bc.faq && bc.faq.length > 0 && (
        <div className="section-block">
          <h2>FAQ</h2>
          {bc.faq.map((item, i) => (
            <div className="faq-item" key={i}>
              <div className="faq-q">{item.q}</div>
              <div className="faq-a">{item.a}</div>
            </div>
          ))}
        </div>
      )}

      {bc.objectionHandling && bc.objectionHandling.length > 0 && (
        <div className="section-block">
          <h2>Objection Handling</h2>
          {bc.objectionHandling.map((item, i) => (
            <div className="objection-item" key={i}>
              <div className="objection-label">Objection</div>
              <div className="objection-text">{item.objection}</div>
              <div className="objection-response">{item.response}</div>
            </div>
          ))}
        </div>
      )}

      {bc.whyWeWin && bc.whyWeWin.length > 0 && (
        <div className="section-block">
          <h2>Why We Win</h2>
          <EditableList items={bc.whyWeWin} onChange={v => update('whyWeWin', v)} />
        </div>
      )}

      {bc.competitiveCounters && bc.competitiveCounters.length > 0 && (
        <div className="section-block">
          <h2>Competitive Counters</h2>
          <div style={{ overflowX: 'auto' }}>
            <table className="competitive-table">
              <thead>
                <tr><th>Competitor</th><th>Their Strength</th><th>Our Counter</th><th>Trap Question</th></tr>
              </thead>
              <tbody>
                {bc.competitiveCounters.map((cc, i) => (
                  <tr key={i}>
                    <td>{cc.competitor}</td>
                    <td>{cc.strength}</td>
                    <td>{cc.counter}</td>
                    <td style={{ fontStyle: 'italic', color: 'var(--coral-deep)' }}>{cc.trapQuestion}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {bc.differentiators && bc.differentiators.length > 0 && (
        <div className="section-block">
          <h2>LTM Differentiators</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
            {bc.differentiators.map((d, i) => (
              <div key={i} style={{
                padding: 16, background: 'var(--bg)', borderRadius: 'var(--radius-sm)',
                borderLeft: '3px solid var(--coral)'
              }}>
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4, color: 'var(--ink)' }}>
                  {String(i + 1).padStart(2, '0')}. {d.title}
                </div>
                <div style={{ fontSize: 13, color: 'var(--graphite)', lineHeight: 1.45 }}>{d.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
