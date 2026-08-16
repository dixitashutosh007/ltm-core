import { useData } from '../../context/DataContext';
import EditableText from '../common/EditableText';
import EditableList from '../common/EditableList';

export default function L1Section({ offering }) {
  const { updateOfferingField } = useData();
  const l1 = offering.l1;
  if (!l1) return <div className="empty-state"><p>L1 data not yet available for this offering.</p></div>;

  const update = (field, value) => updateOfferingField(offering.id, `l1.${field}`, value);

  return (
    <div className="detail-content">
      <div className="section-block">
        <h2>Objective</h2>
        <div className="objective-box">
          <EditableText value={l1.objective} onChange={v => update('objective', v)} multiline />
        </div>
      </div>

      <div className="two-col">
        <div className="section-block">
          <h2>Value to Customer</h2>
          <EditableList items={l1.valueToCustomer} onChange={v => update('valueToCustomer', v)} />
        </div>
        <div className="section-block">
          <h2>Customer Problems Solved</h2>
          <EditableList items={l1.problemsSolved} onChange={v => update('problemsSolved', v)} />
        </div>
      </div>

      <div className="section-block">
        <h2>Key Deliverables</h2>
        <EditableList items={l1.keyDeliverables} onChange={v => update('keyDeliverables', v)} />
      </div>

      <div className="diff-grid">
        <div className="section-block col in">
          <h3 style={{ color: '#059669' }}>In Scope</h3>
          <EditableList items={l1.inScope} onChange={v => update('inScope', v)} />
        </div>
        <div className="section-block col out">
          <h3 style={{ color: 'var(--coral)' }}>Out of Scope</h3>
          <EditableList items={l1.outOfScope} onChange={v => update('outOfScope', v)} />
        </div>
      </div>
    </div>
  );
}
