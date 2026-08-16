import { useState } from 'react';
import { useData } from '../../context/DataContext';

export default function AddOfferingModal({ onClose }) {
  const { verticals, offerings, addOffering } = useData();
  const [form, setForm] = useState({
    name: '', tagline: '', verticalId: verticals[0]?.id || '',
    stage: 'Diagnose', duration: '6 weeks', phase: 'Phase 2',
    buyers: '', objective: ''
  });

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    const vertical = verticals.find(v => v.id === form.verticalId);
    const nextNum = offerings.filter(o => o.verticalId === form.verticalId).length + 1;
    const id = form.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

    addOffering({
      id,
      verticalId: form.verticalId,
      number: String(offerings.length + 1).padStart(2, '0'),
      name: form.name.trim(),
      tagline: form.tagline.trim(),
      pillar: `${vertical?.number || '01'} · ${vertical?.name || ''}`,
      stage: form.stage,
      duration: form.duration,
      phase: form.phase,
      buyers: form.buyers.trim(),
      l1: form.objective.trim() ? {
        objective: form.objective.trim(),
        valueToCustomer: [],
        problemsSolved: [],
        keyDeliverables: [],
        inScope: [],
        outOfScope: []
      } : null,
      l2: null,
      battleCard: null
    });
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add New Offering</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-group">
            <label>Offering Name *</label>
            <input value={form.name} onChange={e => set('name', e.target.value)} placeholder="e.g. Cloud Migration Assessment" required />
          </div>
          <div className="form-group">
            <label>Tagline</label>
            <input value={form.tagline} onChange={e => set('tagline', e.target.value)} placeholder="Short description for the card" />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Vertical</label>
              <select value={form.verticalId} onChange={e => set('verticalId', e.target.value)}>
                {verticals.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Stage</label>
              <select value={form.stage} onChange={e => set('stage', e.target.value)}>
                <option>Diagnose</option>
                <option>Design</option>
                <option>Mobilise</option>
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Duration</label>
              <input value={form.duration} onChange={e => set('duration', e.target.value)} placeholder="e.g. 6 weeks" />
            </div>
            <div className="form-group">
              <label>Phase</label>
              <select value={form.phase} onChange={e => set('phase', e.target.value)}>
                <option>Phase 1</option>
                <option>Phase 2</option>
                <option>Phase 3</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Target Buyers</label>
            <input value={form.buyers} onChange={e => set('buyers', e.target.value)} placeholder="e.g. CIO · CTO · Head of Cloud" />
          </div>
          <div className="form-group">
            <label>Objective</label>
            <textarea value={form.objective} onChange={e => set('objective', e.target.value)} placeholder="Brief objective statement for L1 section..." rows={3} />
          </div>
          <div className="modal-actions">
            <button type="button" className="download-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary">Add Offering</button>
          </div>
        </form>
      </div>
    </div>
  );
}
