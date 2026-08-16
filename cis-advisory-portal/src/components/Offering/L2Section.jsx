import { useData } from '../../context/DataContext';
import EditableList from '../common/EditableList';

export default function L2Section({ offering }) {
  const { updateOfferingField } = useData();
  const l2 = offering.l2;
  if (!l2) return (
    <div className="detail-content">
      <div className="empty-state">
        <p>L2 delivery detail not yet available for this offering.</p>
        <p style={{ fontSize: 13, color: 'var(--muted)' }}>Switch to Editor mode to add L2 content.</p>
      </div>
    </div>
  );

  const update = (field, value) => updateOfferingField(offering.id, `l2.${field}`, value);

  return (
    <div className="detail-content">
      <div className="two-col">
        <div className="section-block">
          <h2>Target Personas</h2>
          <EditableList items={l2.personas} onChange={v => update('personas', v)} />
        </div>
        <div className="section-block">
          <h2>Firmographic Sweet Spot</h2>
          <EditableList items={l2.firmographicSweetSpot} onChange={v => update('firmographicSweetSpot', v)} />
        </div>
      </div>

      <div className="two-col">
        <div className="section-block">
          <h2>Trigger Events to Hunt On</h2>
          <EditableList items={l2.triggerEvents} onChange={v => update('triggerEvents', v)} />
        </div>
        <div className="section-block">
          <h2>Disqualifiers</h2>
          <EditableList items={l2.disqualifiers} onChange={v => update('disqualifiers', v)} />
        </div>
      </div>

      {l2.weekPlan && l2.weekPlan.length > 0 && (
        <div className="section-block">
          <h2>Week-by-Week Plan</h2>
          <div style={{ overflowX: 'auto' }}>
            <table className="week-plan-table">
              <thead>
                <tr>
                  <th>Week</th>
                  <th>Phase</th>
                  <th>Focus</th>
                  <th>Activities</th>
                </tr>
              </thead>
              <tbody>
                {l2.weekPlan.map((w, i) => (
                  <tr key={i}>
                    <td className="week-cell">{w.week}</td>
                    <td className="phase-cell">
                      <span className={`phase-badge ${w.phase.toLowerCase()}`}>{w.phase}</span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{w.focus}</td>
                    <td style={{ fontSize: 13, color: 'var(--ink2)', lineHeight: 1.5 }}>{w.activities}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {l2.engagementKPIs && l2.engagementKPIs.length > 0 && (
        <div className="section-block">
          <h2>Engagement KPIs</h2>
          <table className="kpi-table">
            <thead>
              <tr><th>KPI</th><th>Target</th></tr>
            </thead>
            <tbody>
              {l2.engagementKPIs.map((k, i) => (
                <tr key={i}><td>{k.kpi}</td><td>{k.target}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {l2.clientOutcomeKPIs && l2.clientOutcomeKPIs.length > 0 && (
        <div className="section-block">
          <h2>Client Outcome KPIs</h2>
          <div style={{ overflowX: 'auto' }}>
            <table className="kpi-table">
              <thead>
                <tr><th>KPI</th><th>Baseline</th><th>90 Days</th><th>180 Days</th></tr>
              </thead>
              <tbody>
                {l2.clientOutcomeKPIs.map((k, i) => (
                  <tr key={i}><td>{k.kpi}</td><td>{k.base}</td><td>{k.day90}</td><td>{k.day180}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {l2.behaviouralCommitments && l2.behaviouralCommitments.length > 0 && (
        <div className="section-block">
          <h2>Behavioural Commitments (SOW)</h2>
          <EditableList items={l2.behaviouralCommitments} onChange={v => update('behaviouralCommitments', v)} />
        </div>
      )}

      {l2.documentsRequired && l2.documentsRequired.length > 0 && (
        <div className="section-block">
          <h2>Documents & Data Required</h2>
          <EditableList items={l2.documentsRequired} onChange={v => update('documentsRequired', v)} />
        </div>
      )}

      {l2.resourceRequirements && l2.resourceRequirements.length > 0 && (
        <div className="section-block">
          <h2>Delivery Resource Requirements</h2>
          <div style={{ overflowX: 'auto' }}>
            <table className="resource-table">
              <thead>
                <tr><th>Role</th><th>FTE</th><th>Weeks</th><th>Level</th></tr>
              </thead>
              <tbody>
                {l2.resourceRequirements.map((r, i) => (
                  <tr key={i}><td>{r.role}</td><td>{r.fte}</td><td>{r.weeks}</td><td>{r.level}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {l2.customerCommitment && l2.customerCommitment.length > 0 && (
        <div className="section-block">
          <h2>Customer People Commitment</h2>
          <EditableList items={l2.customerCommitment} onChange={v => update('customerCommitment', v)} />
        </div>
      )}

      {l2.frameworksApplied && l2.frameworksApplied.length > 0 && (
        <div className="section-block">
          <h2>Frameworks Applied</h2>
          <EditableList items={l2.frameworksApplied} onChange={v => update('frameworksApplied', v)} />
        </div>
      )}

      {l2.deliverables && l2.deliverables.length > 0 && (
        <div className="section-block">
          <h2>Key Deliverables Handed Over</h2>
          <EditableList items={l2.deliverables} onChange={v => update('deliverables', v)} />
        </div>
      )}
    </div>
  );
}
