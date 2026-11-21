import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { GraduationCap, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

const FALLBACK_DEMO_USERS = [
  { name: 'Shivam Chandel', email: 'chandels0708@gmail.com', password: 'student123', role: 'student', note: 'Reg: 12522547 | Roll: RK3P25ORA20 | Project Lead' },
  { name: 'Nayneet Kumar', email: 'nayneet.student@portal.edu', password: 'student123', role: 'student', note: 'Reg: 12518540 | Roll: RK3P25ORB37 | Research' },
  { name: 'Dr. Rajesh Sharma', email: 'faculty@portal.edu', password: 'faculty123', role: 'faculty', note: 'School of CSE | Curriculum Lead' },
  { name: 'Prof. Sunita Verma', email: 'placement@portal.edu', password: 'placement123', role: 'placement_officer', note: 'Placement Cell | Industry Liaison' },
  { name: 'TechCorp Recruiter', email: 'partner@techcorp.com', password: 'partner123', role: 'employer', note: 'Industry Partner | Recruitment' },
  { name: 'System Admin', email: 'admin@portal.edu', password: 'admin123', role: 'admin', note: 'Governance and Verification' }
];

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState('chandels0708@gmail.com');
  const [password, setPassword] = useState('student123');
  const [loading, setLoading] = useState(false);
  const [demoUsers, setDemoUsers] = useState(FALLBACK_DEMO_USERS);

  useEffect(() => {
    async function loadDemo() {
      try {
        const users = await api.getDemoUsers();
        if (users && users.length > 0) {
          const hasShivam = users.some(u => u.email === 'chandels0708@gmail.com');
          if (!hasShivam) {
            setDemoUsers([FALLBACK_DEMO_USERS[0], ...users]);
          } else {
            setDemoUsers(users);
          }
        }
      } catch (err) {
        // Fallback demo users will be used
      }
    }
    loadDemo();
  }, []);

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setLoading(true);
    try {
      const activeEmail = email.trim() || 'chandels0708@gmail.com';
      const activePassword = password || 'student123';
      await login(activeEmail, activePassword);
    } catch (err) {
      console.warn('Login processed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (user) => {
    setEmail(user.email);
    setPassword(user.password);
    setLoading(true);
    try {
      await login(user.email, user.password);
    } catch (err) {
      console.warn('Quick login processed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-10 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-sky-500/15 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center relative z-10">
        <div className="inline-flex p-3.5 bg-sky-600 rounded-2xl text-white shadow-xl mb-4">
          <GraduationCap className="w-9 h-9" />
        </div>
        <h1 className="text-3xl font-black text-white tracking-tight sm:text-4xl">
          Academia–Industry Portal
        </h1>
        <p className="mt-2 text-xs font-semibold text-sky-300 uppercase tracking-widest">
          Smart India Hackathon 2026 · Problem Statement SIH26044 · Group G29
        </p>
        <p className="text-xs text-slate-400 mt-1 font-medium">
          Ministry of Ayush · Shivam Chandel and Nayneet Kumar · LPU
        </p>
      </div>

      <div className="mt-7 sm:mx-auto sm:w-full sm:max-w-xl px-4 relative z-10">
        <div className="bg-white py-8 px-6 sm:px-9 shadow-2xl rounded-3xl border border-slate-100">
          
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-sky-600" />
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-800">
                  Quick Evaluator Login (One-Click Role Access)
                </h3>
              </div>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                <Sparkles className="w-3 h-3" /> Instant
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {demoUsers.map((u, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleQuickLogin(u)}
                  className={`text-left p-3 rounded-2xl border transition-all group flex flex-col justify-between ${
                    u.email === 'chandels0708@gmail.com' 
                      ? 'bg-sky-50/80 border-sky-300 hover:border-sky-500 shadow-sm'
                      : 'bg-slate-50/70 border-slate-200 hover:border-sky-400 hover:bg-sky-50/40'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <span className="font-bold text-xs text-slate-900 group-hover:text-sky-700 flex items-center gap-1.5">
                      {u.name}
                      {u.email === 'chandels0708@gmail.com' && (
                        <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
                      )}
                    </span>
                    <span className="text-[9px] uppercase px-2 py-0.5 rounded-lg bg-white border border-slate-200 font-mono text-slate-700 font-bold shadow-2xs">
                      {u.role.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-1 font-medium">{u.note}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-[11px] uppercase">
              <span className="bg-white px-3 text-slate-400 font-bold tracking-wider">
                Or Sign In with Email
              </span>
            </div>
          </div>

          <form className="space-y-3.5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="e.g. chandels0708@gmail.com"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700">
                  Password
                </label>
                <span className="text-[10px] text-slate-400 font-medium">Default: student123</span>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-3 flex justify-center items-center space-x-2 py-3 px-4 rounded-xl shadow-lg shadow-sky-600/25 text-sm font-bold text-white bg-sky-600 hover:bg-sky-700 active:scale-[0.99] transition-all"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In to Portal'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-medium">
            <span>Pre-configured Credentials:</span>
            <span className="font-mono font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-100">
              student123
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
