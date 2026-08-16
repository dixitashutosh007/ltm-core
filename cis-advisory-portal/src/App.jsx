import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { DataProvider } from './context/DataContext';
import { RoleProvider } from './context/RoleContext';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import LandingPage from './pages/LandingPage';
import OfferingPage from './pages/OfferingPage';
import ToastContainer from './components/common/Toast';

export default function App() {
  return (
    <BrowserRouter>
      <DataProvider>
        <RoleProvider>
          <div className="app-shell">
            <Header />
            <Sidebar />
            <main className="app-main">
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/offering/:id" element={<OfferingPage />} />
              </Routes>
            </main>
          </div>
          <ToastContainer />
        </RoleProvider>
      </DataProvider>
    </BrowserRouter>
  );
}
