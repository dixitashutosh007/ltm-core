import { useState, useRef } from 'react';
import { useData } from '../../context/DataContext';

export default function ImportModal({ onClose }) {
  const { importData, addToast } = useData();
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileRef = useRef(null);

  const processFile = (file) => {
    if (!file) return;
    if (!file.name.endsWith('.json')) {
      addToast('Please upload a JSON file', 'error');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        const summary = [];
        if (data.verticals?.length) summary.push(`${data.verticals.length} verticals`);
        if (data.offerings?.length) summary.push(`${data.offerings.length} offerings`);
        if (!summary.length) {
          addToast('No valid data found in file', 'error');
          return;
        }
        setPreview({ data, summary: summary.join(', '), fileName: file.name });
      } catch {
        addToast('Invalid JSON file', 'error');
      }
    };
    reader.readAsText(file);
  };

  const handleImport = () => {
    if (!preview) return;
    importData(preview.data);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Import Data</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          <p style={{ fontSize: 14, color: 'var(--graphite)', marginBottom: 16 }}>
            Upload a JSON file exported from this portal. Existing offerings with matching IDs will be updated; new ones will be added.
          </p>
          <div
            className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={e => { e.preventDefault(); setDragOver(false); processFile(e.dataTransfer.files[0]); }}
            onClick={() => fileRef.current?.click()}
          >
            <input ref={fileRef} type="file" accept=".json" hidden onChange={e => processFile(e.target.files[0])} />
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <span>Drop a JSON file here or click to browse</span>
          </div>

          {preview && (
            <div className="import-preview">
              <div style={{ fontWeight: 600, marginBottom: 4 }}>{preview.fileName}</div>
              <div style={{ fontSize: 13, color: 'var(--graphite)' }}>Contains: {preview.summary}</div>
            </div>
          )}

          <div className="modal-actions">
            <button type="button" className="download-btn" onClick={onClose}>Cancel</button>
            <button className="btn-primary" onClick={handleImport} disabled={!preview}>Import</button>
          </div>
        </div>
      </div>
    </div>
  );
}
