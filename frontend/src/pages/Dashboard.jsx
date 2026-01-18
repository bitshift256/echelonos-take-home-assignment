import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, Building2, TrendingUp, UserPlus, 
  ArrowUpRight, Download, FileSpreadsheet, FileText
} from 'lucide-react';
import { getEmployees, getTeams, getDepartments, exportUrls } from '../api';

function StatCard({ title, value, change, icon: Icon, color, delay }) {
  const colorClasses = {
    blue: 'from-electric-500 to-electric-600 shadow-electric-500/30',
    green: 'from-emerald-500 to-emerald-600 shadow-emerald-500/30',
    amber: 'from-amber-500 to-amber-600 shadow-amber-500/30',
    coral: 'from-coral-500 to-coral-600 shadow-coral-500/30',
  };
  
  return (
    <div className={`stat-card animate-fade-in animate-fade-in-delay-${delay}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-midnight-400 text-sm font-medium mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {change && (
            <p className="text-emerald-400 text-sm mt-2 flex items-center gap-1">
              <TrendingUp className="w-4 h-4" />
              {change}
            </p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClasses[color]} 
                        flex items-center justify-center shadow-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}

function RecentEmployee({ employee, index }) {
  const statusColors = {
    active: 'badge-active',
    inactive: 'badge-inactive',
    on_leave: 'badge-on-leave',
    terminated: 'badge-terminated',
  };
  
  return (
    <div 
      className={`flex items-center gap-4 p-4 rounded-xl hover:bg-midnight-800/30 
                 transition-colors animate-fade-in`}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric-500/20 to-electric-600/20 
                    border border-electric-500/30 flex items-center justify-center">
        <span className="text-electric-400 font-bold text-sm">
          {employee.first_name[0]}{employee.last_name[0]}
        </span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-white truncate">
          {employee.first_name} {employee.last_name}
        </p>
        <p className="text-sm text-midnight-400 truncate">{employee.title}</p>
      </div>
      <span className={`badge ${statusColors[employee.status]}`}>
        {employee.status}
      </span>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    totalTeams: 0,
    departments: 0,
    recentHires: 0,
  });
  const [recentEmployees, setRecentEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [employeesRes, teamsRes, depts] = await Promise.all([
          getEmployees({ limit: 10 }),
          getTeams(),
          getDepartments(),
        ]);
        
        setStats({
          totalEmployees: employeesRes.total,
          totalTeams: teamsRes.total,
          departments: depts.length,
          recentHires: employeesRes.items.filter(e => {
            const hireDate = new Date(e.hire_date);
            const threeMonthsAgo = new Date();
            threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
            return hireDate > threeMonthsAgo;
          }).length,
        });
        
        setRecentEmployees(employeesRes.items.slice(0, 5));
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-electric-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-3xl font-display font-bold text-white mb-2">Dashboard</h1>
        <p className="text-midnight-400">Welcome back! Here's what's happening with your organization.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <StatCard
          title="Total Employees"
          value={stats.totalEmployees}
          change="+12% from last month"
          icon={Users}
          color="blue"
          delay={1}
        />
        <StatCard
          title="Teams"
          value={stats.totalTeams}
          icon={Building2}
          color="green"
          delay={2}
        />
        <StatCard
          title="Departments"
          value={stats.departments}
          icon={TrendingUp}
          color="amber"
          delay={3}
        />
        <StatCard
          title="Recent Hires"
          value={stats.recentHires}
          change="Last 3 months"
          icon={UserPlus}
          color="coral"
          delay={4}
        />
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Employees */}
        <div className="lg:col-span-2 glass-card p-6 animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Recent Employees</h2>
            <Link to="/employees" className="text-electric-400 hover:text-electric-300 
                                           flex items-center gap-1 text-sm font-medium">
              View all <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="space-y-2">
            {recentEmployees.map((employee, index) => (
              <RecentEmployee key={employee.id} employee={employee} index={index} />
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <h2 className="text-xl font-bold text-white mb-6">Quick Actions</h2>
          <div className="space-y-3">
            <Link to="/employees" className="btn-primary w-full flex items-center justify-center gap-2">
              <UserPlus className="w-4 h-4" />
              Add Employee
            </Link>
            <Link to="/teams" className="btn-secondary w-full flex items-center justify-center gap-2">
              <Building2 className="w-4 h-4" />
              Create Team
            </Link>
            <Link to="/org-chart" className="btn-secondary w-full flex items-center justify-center gap-2">
              <TrendingUp className="w-4 h-4" />
              View Org Chart
            </Link>
          </div>
          
          <div className="mt-8 pt-6 border-t border-midnight-700/50">
            <h3 className="text-sm font-medium text-midnight-400 mb-4">Export Data</h3>
            <div className="space-y-2">
              <a 
                href={exportUrls.employeesCsv} 
                className="flex items-center gap-3 p-3 rounded-xl hover:bg-midnight-800/30 transition-colors"
              >
                <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
                <span className="text-sm">Export as CSV</span>
                <Download className="w-4 h-4 ml-auto text-midnight-500" />
              </a>
              <a 
                href={exportUrls.employeesExcel} 
                className="flex items-center gap-3 p-3 rounded-xl hover:bg-midnight-800/30 transition-colors"
              >
                <FileSpreadsheet className="w-5 h-5 text-electric-400" />
                <span className="text-sm">Export as Excel</span>
                <Download className="w-4 h-4 ml-auto text-midnight-500" />
              </a>
              <a 
                href={exportUrls.employeesPdf} 
                className="flex items-center gap-3 p-3 rounded-xl hover:bg-midnight-800/30 transition-colors"
              >
                <FileText className="w-5 h-5 text-coral-400" />
                <span className="text-sm">Export as PDF</span>
                <Download className="w-4 h-4 ml-auto text-midnight-500" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

