import { useState, useEffect } from 'react';
import { 
  Search, Plus, Edit2, Trash2, X, ChevronLeft, ChevronRight,
  Filter, Download, Upload
} from 'lucide-react';
import { 
  getEmployees, createEmployee, updateEmployee, deleteEmployee, 
  getDepartments, exportUrls 
} from '../api';

function EmployeeModal({ employee, onClose, onSave, departments }) {
  const [formData, setFormData] = useState(employee || {
    employee_id: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    title: '',
    department: '',
    hire_date: new Date().toISOString().split('T')[0],
    salary: '',
    status: 'active',
    manager_id: null,
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
        salary: formData.salary ? parseFloat(formData.salary) : null,
        manager_id: formData.manager_id ? parseInt(formData.manager_id) : null,
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
      <div className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-fade-in">
        <div className="p-6 border-b border-midnight-700/50 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">
            {employee ? 'Edit Employee' : 'Add New Employee'}
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
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {!employee && (
              <div>
                <label className="block text-sm font-medium text-midnight-300 mb-2">Employee ID *</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                  placeholder="EMP001"
                />
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">First Name *</label>
              <input
                type="text"
                required
                className="input-field"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                placeholder="John"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Last Name *</label>
              <input
                type="text"
                required
                className="input-field"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                placeholder="Doe"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Email *</label>
              <input
                type="email"
                required
                className="input-field"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john.doe@company.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Phone</label>
              <input
                type="tel"
                className="input-field"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+1-555-0001"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Title *</label>
              <input
                type="text"
                required
                className="input-field"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Software Engineer"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Department *</label>
              <select
                required
                className="input-field"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              >
                <option value="">Select Department</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
                <option value="__new__">+ Add New Department</option>
              </select>
              {formData.department === '__new__' && (
                <input
                  type="text"
                  className="input-field mt-2"
                  placeholder="New department name"
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                />
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Hire Date *</label>
              <input
                type="date"
                required
                className="input-field"
                value={formData.hire_date}
                onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Salary</label>
              <input
                type="number"
                className="input-field"
                value={formData.salary}
                onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
                placeholder="100000"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Status</label>
              <select
                className="input-field"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="on_leave">On Leave</option>
                <option value="terminated">Terminated</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-midnight-300 mb-2">Manager ID</label>
              <input
                type="number"
                className="input-field"
                value={formData.manager_id || ''}
                onChange={(e) => setFormData({ ...formData, manager_id: e.target.value })}
                placeholder="Leave empty if none"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Saving...' : (employee ? 'Update' : 'Create')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function DeleteConfirmModal({ employee, onClose, onConfirm }) {
  const [loading, setLoading] = useState(false);

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onConfirm();
      onClose();
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-midnight-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card w-full max-w-md animate-fade-in p-6">
        <h2 className="text-xl font-bold text-white mb-4">Delete Employee</h2>
        <p className="text-midnight-300 mb-6">
          Are you sure you want to delete <span className="text-white font-medium">
            {employee.first_name} {employee.last_name}
          </span>? This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={handleDelete} disabled={loading} className="btn-danger">
            {loading ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [filterDept, setFilterDept] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [deletingEmployee, setDeletingEmployee] = useState(null);
  const pageSize = 10;

  const loadEmployees = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
      };
      if (filterDept) params.department = filterDept;
      
      const data = await getEmployees(params);
      setEmployees(data.items);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    try {
      const depts = await getDepartments();
      setDepartments(depts);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  useEffect(() => {
    loadEmployees();
  }, [page, filterDept]);

  const handleCreate = async (data) => {
    await createEmployee(data);
    loadEmployees();
    loadDepartments();
  };

  const handleUpdate = async (data) => {
    await updateEmployee(editingEmployee.id, data);
    loadEmployees();
    setEditingEmployee(null);
  };

  const handleDelete = async () => {
    await deleteEmployee(deletingEmployee.id);
    loadEmployees();
    setDeletingEmployee(null);
  };

  const filteredEmployees = search
    ? employees.filter(e => 
        `${e.first_name} ${e.last_name} ${e.email} ${e.title}`.toLowerCase().includes(search.toLowerCase())
      )
    : employees;

  const statusColors = {
    active: 'badge-active',
    inactive: 'badge-inactive',
    on_leave: 'badge-on-leave',
    terminated: 'badge-terminated',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="text-3xl font-display font-bold text-white">Employees</h1>
          <p className="text-midnight-400">{total} employees in your organization</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Employee
        </button>
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex flex-col sm:flex-row gap-4 animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-midnight-500" />
          <input
            type="text"
            placeholder="Search employees..."
            className="input-field pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-4">
          <select
            className="input-field w-48"
            value={filterDept}
            onChange={(e) => { setFilterDept(e.target.value); setPage(1); }}
          >
            <option value="">All Departments</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
          <div className="flex gap-2">
            <a href={exportUrls.employeesCsv} className="btn-secondary flex items-center gap-2">
              <Download className="w-4 h-4" />
              CSV
            </a>
            <a href={exportUrls.employeesExcel} className="btn-secondary flex items-center gap-2">
              <Download className="w-4 h-4" />
              Excel
            </a>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden animate-fade-in" style={{ animationDelay: '0.2s' }}>
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-electric-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-midnight-700/50 bg-midnight-800/30">
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Employee</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Title</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Department</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Status</th>
                  <th className="text-left p-4 text-sm font-medium text-midnight-400">Hire Date</th>
                  <th className="text-right p-4 text-sm font-medium text-midnight-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((employee) => (
                  <tr key={employee.id} className="table-row">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric-500/20 to-electric-600/20 
                                      border border-electric-500/30 flex items-center justify-center flex-shrink-0">
                          <span className="text-electric-400 font-bold text-sm">
                            {employee.first_name[0]}{employee.last_name[0]}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-white">{employee.first_name} {employee.last_name}</p>
                          <p className="text-sm text-midnight-400">{employee.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4 text-midnight-200">{employee.title}</td>
                    <td className="p-4 text-midnight-200">{employee.department}</td>
                    <td className="p-4">
                      <span className={`badge ${statusColors[employee.status]}`}>
                        {employee.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="p-4 text-midnight-300">
                      {new Date(employee.hire_date).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button 
                          onClick={() => setEditingEmployee(employee)}
                          className="p-2 hover:bg-midnight-700 rounded-lg transition-colors text-midnight-400 hover:text-white"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => setDeletingEmployee(employee)}
                          className="p-2 hover:bg-coral-500/20 rounded-lg transition-colors text-midnight-400 hover:text-coral-400"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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

      {/* Modals */}
      {showModal && (
        <EmployeeModal
          onClose={() => setShowModal(false)}
          onSave={handleCreate}
          departments={departments}
        />
      )}
      
      {editingEmployee && (
        <EmployeeModal
          employee={editingEmployee}
          onClose={() => setEditingEmployee(null)}
          onSave={handleUpdate}
          departments={departments}
        />
      )}
      
      {deletingEmployee && (
        <DeleteConfirmModal
          employee={deletingEmployee}
          onClose={() => setDeletingEmployee(null)}
          onConfirm={handleDelete}
        />
      )}
    </div>
  );
}

