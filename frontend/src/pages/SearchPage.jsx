import { useState } from 'react';
import { Search, Users, Building2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { globalSearch } from '../api';

function EmployeeResult({ employee }) {
  const statusColors = {
    active: 'badge-active',
    inactive: 'badge-inactive',
    on_leave: 'badge-on-leave',
    terminated: 'badge-terminated',
  };
  
  return (
    <div className="flex items-center gap-4 p-4 glass-card-hover">
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-electric-500/20 to-electric-600/20 
                    border border-electric-500/30 flex items-center justify-center flex-shrink-0">
        <span className="text-electric-400 font-bold">
          {employee.first_name[0]}{employee.last_name[0]}
        </span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-white truncate">
            {employee.first_name} {employee.last_name}
          </h3>
          <span className={`badge ${statusColors[employee.status]}`}>
            {employee.status}
          </span>
        </div>
        <p className="text-sm text-midnight-400 truncate">{employee.title}</p>
        <p className="text-xs text-midnight-500">{employee.department} • {employee.email}</p>
      </div>
      <Link 
        to="/employees" 
        className="p-2 hover:bg-midnight-700 rounded-lg transition-colors text-midnight-400 hover:text-white"
      >
        <ArrowRight className="w-5 h-5" />
      </Link>
    </div>
  );
}

function TeamResult({ team }) {
  return (
    <div className="flex items-center gap-4 p-4 glass-card-hover">
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 
                    border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
        <Building2 className="w-6 h-6 text-emerald-400" />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-white truncate">{team.name}</h3>
        {team.description && (
          <p className="text-sm text-midnight-400 truncate">{team.description}</p>
        )}
      </div>
      <Link 
        to="/teams" 
        className="p-2 hover:bg-midnight-700 rounded-lg transition-colors text-midnight-400 hover:text-white"
      >
        <ArrowRight className="w-5 h-5" />
      </Link>
    </div>
  );
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setSearched(true);
    try {
      const data = await globalSearch(query);
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto animate-fade-in">
        <h1 className="text-3xl font-display font-bold text-white mb-2">Search</h1>
        <p className="text-midnight-400">Find employees and teams across your organization</p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="max-w-2xl mx-auto animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-midnight-500" />
          <input
            type="text"
            placeholder="Search by name, title, department, email..."
            className="w-full pl-14 pr-32 py-4 bg-midnight-800/50 border border-midnight-700 rounded-2xl
                     text-lg text-midnight-100 placeholder-midnight-500
                     focus:outline-none focus:ring-2 focus:ring-electric-500/50 focus:border-electric-500
                     transition-all duration-200"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 btn-primary"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Results */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-electric-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {!loading && results && (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
          {/* Employees */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-5 h-5 text-electric-400" />
              <h2 className="text-lg font-semibold text-white">
                Employees ({results.total_employees})
              </h2>
            </div>
            {results.employees.length > 0 ? (
              <div className="space-y-3">
                {results.employees.map((employee) => (
                  <EmployeeResult key={employee.id} employee={employee} />
                ))}
              </div>
            ) : (
              <p className="text-midnight-500 text-center py-8 glass-card">
                No employees found matching "{query}"
              </p>
            )}
          </div>

          {/* Teams */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <Building2 className="w-5 h-5 text-emerald-400" />
              <h2 className="text-lg font-semibold text-white">
                Teams ({results.total_teams})
              </h2>
            </div>
            {results.teams.length > 0 ? (
              <div className="space-y-3">
                {results.teams.map((team) => (
                  <TeamResult key={team.id} team={team} />
                ))}
              </div>
            ) : (
              <p className="text-midnight-500 text-center py-8 glass-card">
                No teams found matching "{query}"
              </p>
            )}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !searched && (
        <div className="text-center py-12 animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <div className="w-24 h-24 rounded-2xl bg-midnight-800/50 border border-midnight-700/50 
                        flex items-center justify-center mx-auto mb-6">
            <Search className="w-12 h-12 text-midnight-600" />
          </div>
          <p className="text-midnight-400 mb-2">Start typing to search</p>
          <p className="text-sm text-midnight-500">
            Search across employees and teams by name, title, department, or email
          </p>
        </div>
      )}
    </div>
  );
}

