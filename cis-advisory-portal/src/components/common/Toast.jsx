import { useData } from '../../context/DataContext';

export default function ToastContainer() {
  const { toasts } = useData();

  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>{t.message}</div>
      ))}
    </div>
  );
}
