import { useState, useRef, useEffect } from 'react';
import { useRole } from '../../context/RoleContext';

export default function EditableText({ value, onChange, tag: Tag = 'p', className = '', multiline = false }) {
  const { isEditor } = useRole();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const inputRef = useRef(null);

  useEffect(() => { setDraft(value); }, [value]);
  useEffect(() => {
    if (editing && inputRef.current) inputRef.current.focus();
  }, [editing]);

  if (!isEditor) return <Tag className={className}>{value}</Tag>;

  if (editing) {
    const handleSave = () => {
      onChange(draft);
      setEditing(false);
    };
    if (multiline) {
      return (
        <textarea
          ref={inputRef}
          className="editing-field"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onBlur={handleSave}
          onKeyDown={e => { if (e.key === 'Escape') { setDraft(value); setEditing(false); } }}
        />
      );
    }
    return (
      <input
        ref={inputRef}
        className="editing-field"
        value={draft}
        onChange={e => setDraft(e.target.value)}
        onBlur={handleSave}
        onKeyDown={e => {
          if (e.key === 'Enter') handleSave();
          if (e.key === 'Escape') { setDraft(value); setEditing(false); }
        }}
      />
    );
  }

  return (
    <div className="editable" onClick={() => setEditing(true)} style={{ cursor: 'text' }}>
      <Tag className={className}>{value}</Tag>
      <span className="edit-indicator" title="Click to edit">&#9998;</span>
    </div>
  );
}
