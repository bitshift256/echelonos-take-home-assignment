import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Users, Building2, GitBranch, Search, 
  FileText, Menu, X, ChevronRight 
} from 'lucide-react';
import { useState } from 'react';

import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import Teams from './pages/Teams';
import OrgChart from './pages/OrgChart';
import SearchPage from './pages/SearchPage';
import AuditLogs from './pages/AuditLogs';

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Employees', path: '/employees', icon: Users },
  { name: 'Teams', path: '/teams', icon: Building2 },
  { name: 'Org Chart', path: '/org-chart', icon: GitBranch },
  { name: 'Search', path: '/search', icon: Search },
  { name: 'Audit Logs', path: '/audit', icon: FileText },
];

function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-midnight-950/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 h-full w-72 bg-midnight-900/80 backdrop-blur-xl
        border-r border-midnight-800/50 z-50 transform transition-transform duration-300
        lg:translate-x-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Logo */}
        <div className="h-20 flex items-center px-6 border-b border-midnight-800/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric-500 to-electric-600 
                          flex items-center justify-center shadow-lg shadow-electric-500/30">
              <Users className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-display font-bold text-xl text-white">HRIS</h1>
              <p className="text-xs text-midnight-500">Human Resources</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="ml-auto lg:hidden p-2 hover:bg-midnight-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
                {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
              </NavLink>
            );
          })}
        </nav>
        
        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-midnight-800/50">
          <div className="glass-card p-4">
            <p className="text-xs text-midnight-500 mb-1">System Status</p>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-sm text-emerald-400">All systems operational</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  return (
    <div className="min-h-screen bg-midnight-950">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-midnight-950 via-midnight-900 to-midnight-950 pointer-events-none" />
      <div className="fixed top-0 right-0 w-[800px] h-[800px] bg-electric-600/5 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-[600px] h-[600px] bg-emerald-600/5 rounded-full blur-3xl pointer-events-none" />
      
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Main content */}
      <div className="lg:ml-72 relative">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-20 bg-midnight-950/80 backdrop-blur-xl border-b border-midnight-800/50">
          <div className="h-full px-6 flex items-center">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 hover:bg-midnight-800 rounded-lg transition-colors mr-4"
            >
              <Menu className="w-6 h-6" />
            </button>
            
            <div className="flex-1" />
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-midnight-100">Admin User</p>
                <p className="text-xs text-midnight-500">HR Administrator</p>
              </div>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-coral-500 to-coral-600 
                            flex items-center justify-center text-white font-bold">
                A
              </div>
            </div>
          </div>
        </header>
        
        {/* Page content */}
        <main className="p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/teams" element={<Teams />} />
            <Route path="/org-chart" element={<OrgChart />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/audit" element={<AuditLogs />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

