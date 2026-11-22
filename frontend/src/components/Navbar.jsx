import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  GraduationCap,
  BookOpen,
  Briefcase,
  GitCompare,
  BarChart3,
  FlaskConical,
  ShieldCheck,
  LogOut,
  ChevronDown,
  UserCheck
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const { user, logout, switchDemoRole } = useAuth();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const demoAccounts = [
    { role: 'student', name: 'Shivam Chandel (Student)', email: 'shivam.student@portal.edu', pass: 'student123' },
    { role: 'student', name: 'Navneet Kumar (Student)', email: 'navneet.student@portal.edu', pass: 'student123' },
    { role: 'faculty', name: 'Dr. Rajesh Sharma (Faculty)', email: 'faculty@portal.edu', pass: 'faculty123' },
    { role: 'placement_officer', name: 'Prof. Sunita Verma (Placement)', email: 'placement@portal.edu', pass: 'placement123' },
    { role: 'employer', name: 'TechCorp Recruiter (Industry)', email: 'partner@techcorp.com', pass: 'partner123' },
    { role: 'admin', name: 'System Administrator (Admin)', email: 'admin@portal.edu', pass: 'admin123' }
  ];

  const handleRoleSwitch = async (acc) => {
    setRoleDropdownOpen(false);
    await switchDemoRole(acc.email, acc.pass);
    // Switch default tab to match new role
    if (acc.role === 'student') setActiveTab('student');
    else if (acc.role === 'faculty') setActiveTab('faculty');
    else if (acc.role === 'placement_officer') setActiveTab('placement');
    else if (acc.role === 'employer') setActiveTab('employer');
    else if (acc.role === 'admin') setActiveTab('admin');
  };

  const navItems = [
    { id: 'student', label: 'Student Readiness', icon: GraduationCap },
    { id: 'faculty', label: 'Curriculum & Syllabi', icon: BookOpen },
    { id: 'placement', label: 'Cohort Analytics', icon: BarChart3 },
    { id: 'employer', label: 'Job Requirements', icon: Briefcase },
    { id: 'mapping', label: 'Skill Mapping', icon: GitCompare },
    { id: 'evaluation', label: 'Model Evaluation', icon: FlaskConical },
    { id: 'admin', label: 'Admin & Audit', icon: ShieldCheck }
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
      {/* Top Banner */}
      <div className="bg-slate-900 text-slate-300 text-[11px] px-4 py-1.5 flex justify-between items-center border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="bg-sky-500 text-white font-bold px-1.5 py-0.5 rounded text-[10px] tracking-wider uppercase">SIH 2026</span>
          <span className="font-medium text-slate-200">Problem ID: SIH26044 · Group G29 (Ministry of Ayush)</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="hidden sm:inline text-slate-400">Team: Shivam Chandel & Navneet Kumar</span>
          <div className="relative">
            <button
              onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
              className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-sky-300 px-2.5 py-0.5 rounded transition text-xs font-medium border border-slate-700"
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Switch Evaluator Role</span>
              <ChevronDown className="w-3 h-3" />
            </button>

            {roleDropdownOpen && (
              <div className="absolute right-0 mt-1 w-64 bg-white rounded-lg shadow-xl border border-slate-200 py-1 text-slate-700 z-50 text-xs">
                <div className="px-3 py-1.5 bg-slate-50 border-b border-slate-100 font-bold text-slate-500 text-[10px] uppercase">
                  Instant Evaluator Logins
                </div>
                {demoAccounts.map((acc, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleRoleSwitch(acc)}
                    className="w-full text-left px-3 py-2 hover:bg-sky-50 flex items-center justify-between transition"
                  >
                    <div>
                      <div className="font-semibold text-slate-800">{acc.name}</div>
                      <div className="text-[10px] text-slate-600">{acc.email}</div>
                    </div>
                    <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-slate-100 font-mono font-bold text-slate-700">
                      {acc.role.replace('_', ' ')}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('student')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-base text-slate-900 tracking-tight leading-tight">
                SkillMapping<span className="text-sky-600">Portal</span>
              </h1>
              <p className="text-[11px] text-slate-500 font-medium">Academia–Industry Skill Intelligence</p>
            </div>
          </div>

          {/* User profile & Logout */}
          <div className="flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-bold text-slate-800">{user.name}</div>
                  <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-sky-100 text-sky-800 border border-sky-200">
                    {user.role ? user.role.replace('_', ' ') : 'User'}
                  </span>
                </div>
                <button
                  onClick={logout}
                  title="Sign Out"
                  className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : null}
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 overflow-x-auto pb-2 scrollbar-none border-t border-slate-100 pt-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-sky-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
