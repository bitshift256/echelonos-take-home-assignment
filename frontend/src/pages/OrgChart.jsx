import { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, User, Download, Maximize2, Minimize2 } from 'lucide-react';
import { getOrgChart, exportUrls } from '../api';

function OrgNode({ node, level = 0, expandedNodes, toggleNode }) {
  const isExpanded = expandedNodes.has(node.id);
  const hasChildren = node.children && node.children.length > 0;
  
  const levelColors = [
    'from-electric-500 to-electric-600 shadow-electric-500/30',
    'from-emerald-500 to-emerald-600 shadow-emerald-500/30',
    'from-amber-500 to-amber-600 shadow-amber-500/30',
    'from-coral-500 to-coral-600 shadow-coral-500/30',
    'from-purple-500 to-purple-600 shadow-purple-500/30',
  ];
  
  const colorClass = levelColors[level % levelColors.length];
  
  return (
    <div className="relative">
      {/* Connection line */}
      {level > 0 && (
        <div className="absolute left-0 top-0 w-8 h-8 border-l-2 border-b-2 border-midnight-700/50 rounded-bl-xl -translate-x-8 -translate-y-4" />
      )}
      
      <div 
        className={`glass-card-hover p-4 mb-3 cursor-pointer transition-all duration-200
          ${isExpanded ? 'ring-1 ring-electric-500/30' : ''}`}
        onClick={() => hasChildren && toggleNode(node.id)}
      >
        <div className="flex items-center gap-4">
          {hasChildren && (
            <button className="flex-shrink-0 w-6 h-6 rounded-lg bg-midnight-700/50 flex items-center justify-center">
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-electric-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-midnight-400" />
              )}
            </button>
          )}
          
          {!hasChildren && <div className="w-6" />}
          
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClass} 
                        flex items-center justify-center shadow-lg flex-shrink-0`}>
            <span className="text-white font-bold">
              {node.name.split(' ').map(n => n[0]).join('')}
            </span>
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-white truncate">{node.name}</h3>
            <p className="text-sm text-midnight-400 truncate">{node.title}</p>
            <p className="text-xs text-midnight-500">{node.department}</p>
          </div>
          
          {hasChildren && (
            <span className="badge bg-midnight-700/50 text-midnight-300 border border-midnight-600/30">
              {node.children.length} report{node.children.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>
      
      {/* Children */}
      {isExpanded && hasChildren && (
        <div className="ml-8 pl-8 border-l-2 border-midnight-700/50">
          {node.children.map((child) => (
            <OrgNode
              key={child.id}
              node={child}
              level={level + 1}
              expandedNodes={expandedNodes}
              toggleNode={toggleNode}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TreeView({ orgChart }) {
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  
  const toggleNode = (nodeId) => {
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };
  
  const expandAll = () => {
    const getAllIds = (nodes) => {
      let ids = [];
      for (const node of nodes) {
        ids.push(node.id);
        if (node.children) {
          ids = [...ids, ...getAllIds(node.children)];
        }
      }
      return ids;
    };
    setExpandedNodes(new Set(getAllIds(orgChart)));
  };
  
  const collapseAll = () => {
    setExpandedNodes(new Set());
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end gap-2">
        <button onClick={expandAll} className="btn-secondary flex items-center gap-2">
          <Maximize2 className="w-4 h-4" />
          Expand All
        </button>
        <button onClick={collapseAll} className="btn-secondary flex items-center gap-2">
          <Minimize2 className="w-4 h-4" />
          Collapse All
        </button>
      </div>
      
      <div className="space-y-2">
        {orgChart.map((root) => (
          <OrgNode
            key={root.id}
            node={root}
            expandedNodes={expandedNodes}
            toggleNode={toggleNode}
          />
        ))}
      </div>
    </div>
  );
}

function StatsOverview({ orgChart }) {
  const countAll = (nodes) => {
    let count = nodes.length;
    for (const node of nodes) {
      if (node.children) {
        count += countAll(node.children);
      }
    }
    return count;
  };
  
  const getMaxDepth = (nodes, depth = 0) => {
    let maxDepth = depth;
    for (const node of nodes) {
      if (node.children && node.children.length > 0) {
        maxDepth = Math.max(maxDepth, getMaxDepth(node.children, depth + 1));
      }
    }
    return maxDepth;
  };
  
  const getDepartments = (nodes) => {
    let depts = new Set();
    for (const node of nodes) {
      depts.add(node.department);
      if (node.children) {
        getDepartments(node.children).forEach(d => depts.add(d));
      }
    }
    return depts;
  };
  
  const totalEmployees = countAll(orgChart);
  const maxDepth = getMaxDepth(orgChart) + 1;
  const departments = getDepartments(orgChart).size;
  const topLevel = orgChart.length;
  
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div className="glass-card p-4 text-center">
        <p className="text-2xl font-bold text-white">{totalEmployees}</p>
        <p className="text-sm text-midnight-400">Total Employees</p>
      </div>
      <div className="glass-card p-4 text-center">
        <p className="text-2xl font-bold text-white">{maxDepth}</p>
        <p className="text-sm text-midnight-400">Hierarchy Levels</p>
      </div>
      <div className="glass-card p-4 text-center">
        <p className="text-2xl font-bold text-white">{departments}</p>
        <p className="text-sm text-midnight-400">Departments</p>
      </div>
      <div className="glass-card p-4 text-center">
        <p className="text-2xl font-bold text-white">{topLevel}</p>
        <p className="text-sm text-midnight-400">Top Level</p>
      </div>
    </div>
  );
}

export default function OrgChart() {
  const [orgChart, setOrgChart] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOrgChart() {
      try {
        const data = await getOrgChart();
        setOrgChart(data);
      } catch (error) {
        console.error('Failed to load org chart:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadOrgChart();
  }, []);

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
          <h1 className="text-3xl font-display font-bold text-white">Organization Chart</h1>
          <p className="text-midnight-400">Visualize your company's reporting structure</p>
        </div>
        <a href={exportUrls.orgChartPdf} className="btn-primary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export PDF
        </a>
      </div>

      {/* Stats */}
      <div className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <StatsOverview orgChart={orgChart} />
      </div>

      {/* Tree View */}
      <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '0.2s' }}>
        {orgChart.length > 0 ? (
          <TreeView orgChart={orgChart} />
        ) : (
          <div className="text-center py-12">
            <User className="w-12 h-12 text-midnight-600 mx-auto mb-4" />
            <p className="text-midnight-400">No employees found</p>
            <p className="text-sm text-midnight-500">Add employees to see the organization chart</p>
          </div>
        )}
      </div>
    </div>
  );
}

