import { useState } from 'react';
import { useRole } from '../../context/RoleContext';
import { useData } from '../../context/DataContext';
import ImportModal from '../Editor/ImportModal';

export default function Header() {
  const { role, setRole } = useRole();
  const { exportData } = useData();
  const [showImport, setShowImport] = useState(false);

  const handleExport = () => {
    const data = exportData();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cis-advisory-portal-data.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <header className="app-header">
        <div className="header-brand">
          <span className="logo-text">LTM</span>
          <span className="divider" />
          <span className="sub-text">CIS Tech Advisory Portal</span>
        </div>
        <div className="header-actions">
          {role === 'editor' && (
            <button className="download-btn" onClick={() => setShowImport(true)} title="Import data from JSON file">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 14.5v-9m0 0l3.5 3.5M8 5.5L4.5 9M2 2.5h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
              Import
            </button>
          )}
          <button className="download-btn" onClick={handleExport} title="Export all portal data as JSON">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 1.5v9m0 0l3.5-3.5M8 10.5L4.5 7M2 13.5h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Export
          </button>
          <div className="role-toggle">
            <button className={role === 'viewer' ? 'active' : ''} onClick={() => setRole('viewer')}>Viewer</button>
            <button className={role === 'editor' ? 'active' : ''} onClick={() => setRole('editor')}>Editor</button>
          </div>
        </div>
      </header>
      {showImport && <ImportModal onClose={() => setShowImport(false)} />}
    </>
  );
}
