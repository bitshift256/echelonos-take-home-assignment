import { useState, useEffect } from 'react';
import { FileText, Filter, ChevronLeft, ChevronRight, Plus, Edit2, Trash2 } from 'lucide-react';
import { getAuditLogs } from '../api';

const actionIcons = {
  create: Plus,
  update: Edit2,
  delete: Trash2,
};

const actionColors = {
  create: 'text-emerald-400 bg-emerald-500/20',
  update: 'text-electric-400 bg-electric-500/20',
  delete: 'text-coral-400 bg-coral-500/20',
};

function AuditLogRow({ log }) {
  const Icon = actionIcons[log.action] || FileText;
  const colorClass = actionColors[log.action] || 'text-midnight-400 bg-midnight-700/50';
  
  let changes = null;
  try {
    changes = log.changes ? JSON.parse(log.changes) : null;
  } catch (e) {
    changes = null;
  }
  
  return (
    <tr className="table-row">
      <td className="p-4">
        <div className={`w-8 h-8 rounded-lg ${colorClass} flex items-center justify-center`}>
          <Icon className="w-4 h-4" />
        </div>
      </td>
      <td className="p-4">
        <span className="capitalize font-medium text-white">{log.action}</span>
      </td>
      <td className="p-4">
        <span className="badge bg-midnight-700/50 text-midnight-300 border border-midnight-600/30">
          {log.entity_type}
        </span>
      </td>
      <td className="p-4 text-midnight-200">#{log.entity_id}</td>
      <td className="p-4">
        {changes && (
          <div className="text-sm text-midnight-400 max-w-xs truncate">
            {typeof changes === 'object' && !Array.isArray(changes) ? (
              Object.keys(changes).slice(0, 3).join(', ') + 
              (Object.keys(changes).length > 3 ? '...' : '')
            ) : (
              JSON.stringify(changes).substring(0, 50)
            )}
          </div>
        )}
      </td>
      <td className="p-4 text-midnight-300 whitespace-nowrap">
        {new Date(log.performed_at).toLocaleString()}
      </td>
    </tr>
  );
}

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [filterEntity, setFilterEntity] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const pageSize = 20;

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
      };
      if (filterEntity) params.entity_type = filterEntity;
      if (filterAction) params.action = filterAction;
      
      const data = await getAuditLogs(params);
      setLogs(data.items);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [page, filterEntity, filterAction]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-3xl font-display font-bold text-white">Audit Logs</h1>
        <p className="text-midnight-400">Track all changes made to employees and teams</p>
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex flex-wrap gap-4 items-center animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <Filter className="w-5 h-5 text-midnight-500" />
        <select
          className="input-field w-40"
          value={filterEntity}
          onChange={(e) => { setFilterEntity(e.target.value); setPage(1); }}
        >
          <option value="">All Entities</option>
          <option value="employee">Employees</option>
          <option value="team">Teams</option>
        </select>
        <select
          className="input-field w-40"
          value={filterAction}
          onChange={(e) => { setFilterAction(e.target.value); setPage(1); }}
        >
          <option value="">All Actions</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
        </select>
        <div className="flex-1" />
        <span className="text-sm text-midnight-400">
          {total} log entries
        </span>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden animate-fade-in" style={{ animationDelay: '0.2s' }}>
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-electric-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : logs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-midnight-700/50 bg-midnight-800/30">
                  <th className="text-left p-4 text-sm font-medium text-midnight-400 w-16"></th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Action</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Entity Type</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Entity ID</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Changes</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Date</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <AuditLogRow key={log.id} log={log} />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-midnight-600 mx-auto mb-4" />
            <p className="text-midnight-400">No audit logs found</p>
            <p className="text-sm text-midnight-500">Changes to employees and teams will appear here</p>
          </div>
        )}

        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="p-4 border-t border-midnight-700/50 flex items-center justify-between">
            <p className="text-sm text-midnight-400">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total}
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 hover:bg-midnight-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-sm text-midnight-300">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 hover:bg-midnight-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

