const API_BASE = '/api/v1';

async function fetchApi(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || 'Request failed');
  }
  
  if (response.status === 204) {
    return null;
  }
  
  return response.json();
}

// Employees
export const getEmployees = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchApi(`/employees${query ? `?${query}` : ''}`);
};

export const getEmployee = (id) => fetchApi(`/employees/${id}`);

export const createEmployee = (data) => fetchApi('/employees', {
  method: 'POST',
  body: JSON.stringify(data),
});

export const updateEmployee = (id, data) => fetchApi(`/employees/${id}`, {
  method: 'PUT',
  body: JSON.stringify(data),
});

export const deleteEmployee = (id) => fetchApi(`/employees/${id}`, {
  method: 'DELETE',
});

export const searchEmployees = (query) => fetchApi(`/employees/search?q=${encodeURIComponent(query)}`);

export const getDepartments = () => fetchApi('/employees/departments');

// Teams
export const getTeams = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchApi(`/teams${query ? `?${query}` : ''}`);
};

export const getTeam = (id) => fetchApi(`/teams/${id}`);

export const createTeam = (data) => fetchApi('/teams', {
  method: 'POST',
  body: JSON.stringify(data),
});

export const updateTeam = (id, data) => fetchApi(`/teams/${id}`, {
  method: 'PUT',
  body: JSON.stringify(data),
});

export const deleteTeam = (id) => fetchApi(`/teams/${id}`, {
  method: 'DELETE',
});

export const addTeamMember = (teamId, employeeId) => fetchApi(`/teams/${teamId}/members`, {
  method: 'POST',
  body: JSON.stringify({ employee_id: employeeId }),
});

export const removeTeamMember = (teamId, employeeId) => fetchApi(`/teams/${teamId}/members/${employeeId}`, {
  method: 'DELETE',
});

// Org Chart
export const getOrgChart = () => fetchApi('/org-chart');
export const getOrgChartFlat = () => fetchApi('/org-chart/flat');

// Search
export const globalSearch = (query) => fetchApi(`/search?q=${encodeURIComponent(query)}`);

// Audit
export const getAuditLogs = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchApi(`/audit${query ? `?${query}` : ''}`);
};

// Export URLs (for downloads)
export const exportUrls = {
  employeesCsv: `${API_BASE}/employees/export/csv`,
  employeesExcel: `${API_BASE}/employees/export/excel`,
  employeesPdf: `${API_BASE}/employees/export/pdf`,
  orgChartPdf: `${API_BASE}/org-chart/export/pdf`,
  teamsCsv: `${API_BASE}/teams/export/csv`,
  teamsExcel: `${API_BASE}/teams/export/excel`,
};

