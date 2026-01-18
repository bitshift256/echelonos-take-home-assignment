import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, X, Users, UserPlus, UserMinus, ChevronDown, ChevronRight } from 'lucide-react';
import { getTeams, getTeam, createTeam, updateTeam, deleteTeam, getEmployees, addTeamMember, removeTeamMember } from '../api';

function TeamModal({ team, teams, employees, onClose, onSave }) {
  const [formData, setFormData] = useState(team || {
    name: '',
    description: '',
    parent_team_id: null,
    lead_id: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const data = {
        ...formData,
        parent_team_id: formData.parent_team_id ? parseInt(formData.parent_team_id) : null,
        lead_id: formData.lead_id ? parseInt(formData.lead_id) : null,
      };
      await onSave(data);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-midnight-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card w-full max-w-lg animate-fade-in">
        <div className="p-6 border-b border-midnight-700/50 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">
            {team ? 'Edit Team' : 'Create New Team'}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-midnight-800 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-4 bg-coral-500/20 border border-coral-500/30 rounded-xl text-coral-400 text-sm">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-midnight-300 mb-2">Team Name *</label>
            <input
              type="text"
              required
              className="input-field"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Engineering"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-midnight-300 mb-2">Description</label>
            <textarea
              className="input-field"
              rows={3}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Team description..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-midnight-300 mb-2">Parent Team</label>
            <select
              className="input-field"
              value={formData.parent_team_id || ''}
              onChange={(e) => setFormData({ ...formData, parent_team_id: e.target.value })}
            >
              <option value="">None (Top-level team)</option>
              {teams.filter(t => t.id !== team?.id).map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-midnight-300 mb-2">Team Lead</label>
            <select
              className="input-field"
              value={formData.lead_id || ''}
              onChange={(e) => setFormData({ ...formData, lead_id: e.target.value })}
            >
              <option value="">Select a team lead</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.first_name} {emp.last_name} - {emp.title}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Saving...' : (team ? 'Update' : 'Create')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function TeamCard({ team, employees, onEdit, onDelete, onManageMembers }) {
  const [expanded, setExpanded] = useState(false);
  const [details, setDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const loadDetails = async () => {
    if (details) {
      setExpanded(!expanded);
      return;
    }
    
    setLoadingDetails(true);
    try {
      const data = await getTeam(team.id);
      setDetails(data);
      setExpanded(true);
    } catch (error) {
      console.error('Failed to load team details:', error);
    } finally {
      setLoadingDetails(false);
    }
  };

  const lead = employees.find(e => e.id === team.lead_id);

  return (
    <div className="glass-card-hover overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 
                          border border-emerald-500/30 flex items-center justify-center">
              <Users className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">{team.name}</h3>
              {team.description && (
                <p className="text-sm text-midnight-400 line-clamp-1">{team.description}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => onEdit(team)}
              className="p-2 hover:bg-midnight-700 rounded-lg transition-colors text-midnight-400 hover:text-white"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button 
              onClick={() => onDelete(team)}
              className="p-2 hover:bg-coral-500/20 rounded-lg transition-colors text-midnight-400 hover:text-coral-400"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {lead && (
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs text-midnight-500">Lead:</span>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-electric-500/20 border border-electric-500/30 
                            flex items-center justify-center">
                <span className="text-electric-400 font-bold text-xs">
                  {lead.first_name[0]}{lead.last_name[0]}
                </span>
              </div>
              <span className="text-sm text-midnight-200">{lead.first_name} {lead.last_name}</span>
            </div>
          </div>
        )}
        
        <button
          onClick={loadDetails}
          disabled={loadingDetails}
          className="w-full flex items-center justify-between p-3 rounded-xl bg-midnight-800/30 
                   hover:bg-midnight-800/50 transition-colors text-sm"
        >
          <span className="text-midnight-300">
            {loadingDetails ? 'Loading...' : 'View team members'}
          </span>
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-midnight-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-midnight-400" />
          )}
        </button>
      </div>
      
      {expanded && details && (
        <div className="border-t border-midnight-700/50 p-6 bg-midnight-800/20">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-medium text-midnight-300">
              Members ({details.members?.length || 0})
            </h4>
            <button
              onClick={() => onManageMembers(team, details)}
              className="text-sm text-electric-400 hover:text-electric-300 flex items-center gap-1"
            >
              <UserPlus className="w-4 h-4" />
              Manage
            </button>
          </div>
          
          {details.members && details.members.length > 0 ? (
            <div className="space-y-2">
              {details.members.map((member) => (
                <div key={member.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-midnight-700/30">
                  <div className="w-8 h-8 rounded-lg bg-midnight-700 flex items-center justify-center">
                    <span className="text-midnight-300 font-medium text-xs">
                      {member.employee?.first_name?.[0]}{member.employee?.last_name?.[0]}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">
                      {member.employee?.first_name} {member.employee?.last_name}
                    </p>
                    <p className="text-xs text-midnight-400 truncate">{member.employee?.title}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-midnight-500 text-center py-4">No members yet</p>
          )}
          
          {details.sub_teams && details.sub_teams.length > 0 && (
            <div className="mt-4 pt-4 border-t border-midnight-700/30">
              <h4 className="text-sm font-medium text-midnight-300 mb-2">Sub-teams</h4>
              <div className="flex flex-wrap gap-2">
                {details.sub_teams.map((subTeam) => (
                  <span key={subTeam.id} className="badge bg-midnight-700/50 text-midnight-300 border border-midnight-600/30">
                    {subTeam.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ManageMembersModal({ team, details, employees, onClose, onUpdate }) {
  const [memberIds, setMemberIds] = useState(
    details.members?.map(m => m.employee_id) || []
  );
  const [loading, setLoading] = useState(false);

  const toggleMember = (empId) => {
    setMemberIds(prev => 
      prev.includes(empId) 
        ? prev.filter(id => id !== empId)
        : [...prev, empId]
    );
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const currentIds = details.members?.map(m => m.employee_id) || [];
      const toAdd = memberIds.filter(id => !currentIds.includes(id));
      const toRemove = currentIds.filter(id => !memberIds.includes(id));
      
      for (const empId of toAdd) {
        await addTeamMember(team.id, empId);
      }
      for (const empId of toRemove) {
        await removeTeamMember(team.id, empId);
      }
      
      onUpdate();
      onClose();
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-midnight-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card w-full max-w-lg max-h-[80vh] flex flex-col animate-fade-in">
        <div className="p-6 border-b border-midnight-700/50 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Manage Members - {team.name}</h2>
          <button onClick={onClose} className="p-2 hover:bg-midnight-800 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-2">
            {employees.map((emp) => (
              <label
                key={emp.id}
                className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors
                  ${memberIds.includes(emp.id) ? 'bg-electric-500/10 border border-electric-500/30' : 'hover:bg-midnight-800/30'}`}
              >
                <input
                  type="checkbox"
                  checked={memberIds.includes(emp.id)}
                  onChange={() => toggleMember(emp.id)}
                  className="w-4 h-4 rounded border-midnight-600 bg-midnight-800 text-electric-500 focus:ring-electric-500/50"
                />
                <div className="w-8 h-8 rounded-lg bg-midnight-700 flex items-center justify-center flex-shrink-0">
                  <span className="text-midnight-300 font-medium text-xs">
                    {emp.first_name[0]}{emp.last_name[0]}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{emp.first_name} {emp.last_name}</p>
                  <p className="text-xs text-midnight-400 truncate">{emp.title} • {emp.department}</p>
                </div>
              </label>
            ))}
          </div>
        </div>
        
        <div className="p-6 border-t border-midnight-700/50 flex justify-end gap-3">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={handleSave} disabled={loading} className="btn-primary">
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Teams() {
  const [teams, setTeams] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTeam, setEditingTeam] = useState(null);
  const [deletingTeam, setDeletingTeam] = useState(null);
  const [managingMembers, setManagingMembers] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [teamsData, employeesData] = await Promise.all([
        getTeams({ limit: 100 }),
        getEmployees({ limit: 500 }),
      ]);
      setTeams(teamsData.items);
      setEmployees(employeesData.items);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (data) => {
    await createTeam(data);
    loadData();
  };

  const handleUpdate = async (data) => {
    await updateTeam(editingTeam.id, data);
    loadData();
    setEditingTeam(null);
  };

  const handleDelete = async () => {
    await deleteTeam(deletingTeam.id);
    loadData();
    setDeletingTeam(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-electric-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="text-3xl font-display font-bold text-white">Teams</h1>
          <p className="text-midnight-400">{teams.length} teams in your organization</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Team
        </button>
      </div>

      {/* Teams Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {teams.map((team, index) => (
          <div 
            key={team.id} 
            className="animate-fade-in"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <TeamCard
              team={team}
              employees={employees}
              onEdit={setEditingTeam}
              onDelete={setDeletingTeam}
              onManageMembers={(team, details) => setManagingMembers({ team, details })}
            />
          </div>
        ))}
      </div>

      {/* Modals */}
      {showModal && (
        <TeamModal
          teams={teams}
          employees={employees}
          onClose={() => setShowModal(false)}
          onSave={handleCreate}
        />
      )}
      
      {editingTeam && (
        <TeamModal
          team={editingTeam}
          teams={teams}
          employees={employees}
          onClose={() => setEditingTeam(null)}
          onSave={handleUpdate}
        />
      )}
      
      {deletingTeam && (
        <div className="fixed inset-0 bg-midnight-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-md animate-fade-in p-6">
            <h2 className="text-xl font-bold text-white mb-4">Delete Team</h2>
            <p className="text-midnight-300 mb-6">
              Are you sure you want to delete <span className="text-white font-medium">{deletingTeam.name}</span>? 
              This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button onClick={() => setDeletingTeam(null)} className="btn-secondary">Cancel</button>
              <button onClick={handleDelete} className="btn-danger">Delete</button>
            </div>
          </div>
        </div>
      )}
      
      {managingMembers && (
        <ManageMembersModal
          team={managingMembers.team}
          details={managingMembers.details}
          employees={employees}
          onClose={() => setManagingMembers(null)}
          onUpdate={loadData}
        />
      )}
    </div>
  );
}

