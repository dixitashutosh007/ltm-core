import { createContext, useContext, useState, useCallback } from 'react';
import seedData from '../data/seed.json';

const DataContext = createContext();

export function DataProvider({ children }) {
  const [verticals, setVerticals] = useState(seedData.verticals);
  const [offerings, setOfferings] = useState(seedData.offerings);
  const [methodology] = useState(seedData.methodology);

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
  }, []);

  const addVertical = useCallback((vertical) => {
    setVerticals(prev => [...prev, vertical]);
  }, []);

  const exportData = useCallback(() => {
    return JSON.stringify({ verticals, offerings, methodology }, null, 2);
  }, [verticals, offerings, methodology]);

  return (
    <DataContext.Provider value={{
      verticals, offerings, methodology,
      getOfferingsByVertical, getOffering, getVertical,
      updateOffering, updateOfferingField, addOffering, addVertical,
      exportData
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
