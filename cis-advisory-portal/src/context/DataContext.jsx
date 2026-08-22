import { createContext, useContext, useState, useCallback } from 'react';
import seedData from '../data/seed.json';

const DataContext = createContext();

export function DataProvider({ children }) {
  const [verticals, setVerticals] = useState(seedData.verticals);
  const [offerings, setOfferings] = useState(seedData.offerings);
  const [methodology] = useState(seedData.methodology);
  const [accelerators] = useState(seedData.accelerators || []);
  const [insights] = useState(seedData.insights || []);
  const [partners] = useState(seedData.partners || []);
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000);
  }, []);

  const getOfferingsByVertical = useCallback((verticalId) => {
    return offerings.filter(o => o.verticalId === verticalId);
  }, [offerings]);

  const getOffering = useCallback((id) => {
    return offerings.find(o => o.id === id);
  }, [offerings]);

  const getVertical = useCallback((id) => {
    return verticals.find(v => v.id === id);
  }, [verticals]);

  const updateOffering = useCallback((id, updates) => {
    setOfferings(prev => prev.map(o => o.id === id ? { ...o, ...updates } : o));
  }, []);

  const updateOfferingField = useCallback((offeringId, path, value) => {
    setOfferings(prev => prev.map(o => {
      if (o.id !== offeringId) return o;
      const updated = JSON.parse(JSON.stringify(o));
      const parts = path.split('.');
      let target = updated;
      for (let i = 0; i < parts.length - 1; i++) {
        if (!target[parts[i]]) target[parts[i]] = {};
        target = target[parts[i]];
      }
      target[parts[parts.length - 1]] = value;
      return updated;
    }));
  }, []);

  const addOffering = useCallback((offering) => {
    setOfferings(prev => [...prev, offering]);
    addToast(`Offering "${offering.name}" added`);
  }, [addToast]);

  const deleteOffering = useCallback((id) => {
    setOfferings(prev => prev.filter(o => o.id !== id));
    addToast('Offering removed');
  }, [addToast]);

  const addVertical = useCallback((vertical) => {
    setVerticals(prev => [...prev, vertical]);
    addToast(`Vertical "${vertical.name}" added`);
  }, [addToast]);

  const importData = useCallback((data) => {
    let count = 0;
    if (data.verticals && Array.isArray(data.verticals)) {
      setVerticals(prev => {
        const ids = new Set(prev.map(v => v.id));
        const newOnes = data.verticals.filter(v => !ids.has(v.id));
        count += newOnes.length;
        return newOnes.length ? [...prev, ...newOnes] : prev;
      });
    }
    if (data.offerings && Array.isArray(data.offerings)) {
      setOfferings(prev => {
        const merged = [...prev];
        for (const incoming of data.offerings) {
          const idx = merged.findIndex(o => o.id === incoming.id);
          if (idx >= 0) {
            merged[idx] = { ...merged[idx], ...incoming };
            count++;
          } else {
            merged.push(incoming);
            count++;
          }
        }
        return merged;
      });
    }
    addToast(`Imported ${count} items successfully`, 'success');
    return count;
  }, [addToast]);

  const exportData = useCallback(() => {
    return JSON.stringify({ verticals, offerings, accelerators, insights, partners, methodology }, null, 2);
  }, [verticals, offerings, accelerators, insights, partners, methodology]);

  return (
    <DataContext.Provider value={{
      verticals, offerings, methodology, accelerators, insights, partners, toasts,
      getOfferingsByVertical, getOffering, getVertical,
      updateOffering, updateOfferingField, addOffering, deleteOffering,
      addVertical, importData, exportData, addToast
    }}>
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error('useData must be used within DataProvider');
  return ctx;
}
