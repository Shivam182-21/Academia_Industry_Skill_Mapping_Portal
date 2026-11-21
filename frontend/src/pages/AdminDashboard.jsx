import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  ShieldCheck,
  Users,
  Activity,
  Layers,
  Search,
  CheckCircle2,
  Lock,
  ChevronRight
} from 'lucide-react';

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [taxonomy, setTaxonomy] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState('users');

  useEffect(() => {
    async function loadData() {
      try {
        const [uList, logs, tax] = await Promise.all([
          api.getAdminUsers(),
          api.getAuditLogs(30),
          api.getTaxonomy()
        ]);
        setUsers(uList);
        setAuditLogs(logs);
        setTaxonomy(tax);
      } catch (err) {
        console.error("Error loading admin data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.updateUserRole(userId, newRole);
      setUsers(users.map(u => u.user_id === userId ? { ...u, role: newRole } : u));
      // Refresh audit logs
      const updatedLogs = await api.getAuditLogs(30);
      setAuditLogs(updatedLogs);
    } catch (err) {
      alert(err.message || 'Error updating role');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
              System Administration
            </span>
            <span className="text-xs text-slate-500 font-mono">FR-08 Governance Module</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">
            User Governance, Audit Logs & Skill Taxonomy
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Maintain role-based access permissions, verify system audit trails, and review canonical skill definitions.
          </p>
        </div>

        {/* Sub-tab navigation */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setActiveSubTab('users')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              activeSubTab === 'users' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            User Accounts ({users.length})
          </button>
          <button
            onClick={() => setActiveSubTab('audit')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              activeSubTab === 'audit' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Audit Logs ({auditLogs.length})
          </button>
          <button
            onClick={() => setActiveSubTab('taxonomy')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              activeSubTab === 'taxonomy' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Skill Taxonomy ({taxonomy.length})
          </button>
        </div>
      </div>

      {/* Sub-tab 1: User Accounts */}
      {activeSubTab === 'users' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900">User Directory & Role Governance</h3>
            <span className="text-xs text-slate-500">RBAC Role-Based Access Control</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                  <th className="py-2.5 px-3">Name</th>
                  <th className="py-2.5 px-3">Email Address</th>
                  <th className="py-2.5 px-3">Active Role</th>
                  <th className="py-2.5 px-3">Associated Profile</th>
                  <th className="py-2.5 px-3">Modify Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.user_id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-3 font-bold text-slate-900">{u.name}</td>
                    <td className="py-3 px-3 font-mono text-slate-600">{u.email}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-sky-50 text-sky-800 border border-sky-100">
                        {u.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[11px] text-slate-500">
                      {u.student_profile ? (
                        <span>Roll: <strong>{u.student_profile.roll_number}</strong> ({u.student_profile.department})</span>
                      ) : (
                        <span className="text-slate-400">Institutional Staff</span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.user_id, e.target.value)}
                        className="bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded px-2 py-1 outline-none font-medium"
                      >
                        <option value="student">student</option>
                        <option value="faculty">faculty</option>
                        <option value="placement_officer">placement_officer</option>
                        <option value="employer">employer</option>
                        <option value="admin">admin</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sub-tab 2: Audit Logs */}
      {activeSubTab === 'audit' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">System Audit Trail</h3>
              <p className="text-xs text-slate-500">Immutable trace of user logins, syllabus uploads, and model evaluations.</p>
            </div>
            <span className="text-xs font-mono font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded">
              FR-08 Compliance
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Actor / User</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Target Entity</th>
                  <th className="py-2.5 px-3">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {auditLogs.map((log) => (
                  <tr key={log.log_id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 font-bold text-slate-900">{log.user_name}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-slate-100 text-slate-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-600 text-[11px]">
                      {log.entity_type} {log.entity_id ? `(${log.entity_id.slice(0, 8)})` : ''}
                    </td>
                    <td className="py-3 px-3 font-mono text-[10px] text-slate-500 max-w-xs truncate">
                      {log.details || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sub-tab 3: Canonical Skill Taxonomy */}
      {activeSubTab === 'taxonomy' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Canonical Skills & Synonym Taxonomy</h3>
              <p className="text-xs text-slate-500">Normalized skill representations with recognized aliases used for entity linking.</p>
            </div>
            <span className="text-xs font-mono font-bold text-sky-700 bg-sky-50 px-2 py-1 rounded border border-sky-100">
              {taxonomy.length} Normalized Skills
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {taxonomy.map((skill) => (
              <div
                key={skill.skill_id}
                className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/40 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-900">{skill.canonical_name}</span>
                    <span className="text-[10px] font-mono uppercase bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                      {skill.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-1 line-clamp-2">{skill.description}</p>
                </div>

                <div className="mt-2 pt-2 border-t border-slate-100 flex flex-wrap gap-1">
                  <span className="text-[10px] font-semibold text-slate-500 mr-1">Aliases:</span>
                  {skill.aliases && skill.aliases.map((alias, i) => (
                    <span key={i} className="text-[10px] font-mono bg-white px-1.5 py-0.2 rounded border border-slate-200 text-slate-700">
                      {alias}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
