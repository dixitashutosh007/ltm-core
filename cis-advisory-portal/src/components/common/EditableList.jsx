import { useState } from 'react';
import { useRole } from '../../context/RoleContext';

export default function EditableList({ items, onChange, className = 'content-list' }) {
  const { isEditor } = useRole();
  const [editingIdx, setEditingIdx] = useState(-1);
  const [draft, setDraft] = useState('');
  const [adding, setAdding] = useState(false);
  const [newItem, setNewItem] = useState('');

  const handleSave = (idx) => {
    if (draft.trim()) {
      const updated = [...items];
      updated[idx] = draft.trim();
      onChange(updated);
    }
    setEditingIdx(-1);
  };

  const handleDelete = (idx) => {
    onChange(items.filter((_, i) => i !== idx));
  };

  const handleAdd = () => {
    if (newItem.trim()) {
      onChange([...items, newItem.trim()]);
      setNewItem('');
      setAdding(false);
    }
  };

  return (
    <div>
      <ul className={className}>
        {items.map((item, i) => (
          <li key={i}>
            {editingIdx === i ? (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  className="editing-field"
                  value={draft}
                  onChange={e => setDraft(e.target.value)}
                  onBlur={() => handleSave(i)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') handleSave(i);
                    if (e.key === 'Escape') setEditingIdx(-1);
                  }}
                  autoFocus
                  style={{ flex: 1 }}
                />
              </div>
            ) : (
              <span
                onClick={() => { if (isEditor) { setEditingIdx(i); setDraft(item); } }}
                style={isEditor ? { cursor: 'text' } : {}}
              >
                {item}
                {isEditor && (
                  <button
                    onClick={e => { e.stopPropagation(); handleDelete(i); }}
                    style={{ marginLeft: 8, color: 'var(--muted)', fontSize: 12 }}
                    title="Remove"
                  >
                    &times;
                  </button>
                )}
              </span>
            )}
          </li>
        ))}
      </ul>
      {isEditor && !adding && (
        <button
          onClick={() => setAdding(true)}
          style={{ fontSize: 13, color: 'var(--coral)', fontWeight: 600, marginTop: 8 }}
        >
          + Add item
        </button>
      )}
      {isEditor && adding && (
        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <input
            className="editing-field"
            placeholder="New item..."
            value={newItem}
            onChange={e => setNewItem(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') handleAdd();
              if (e.key === 'Escape') { setAdding(false); setNewItem(''); }
            }}
            autoFocus
            style={{ flex: 1 }}
          />
          <button className="btn-primary" onClick={handleAdd} style={{ padding: '6px 16px' }}>Add</button>
        </div>
      )}
    </div>
  );
}
