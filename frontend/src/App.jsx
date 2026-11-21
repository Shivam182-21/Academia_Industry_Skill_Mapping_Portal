import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import StudentDashboard from './pages/StudentDashboard';
import FacultyDashboard from './pages/FacultyDashboard';
import PlacementDashboard from './pages/PlacementDashboard';
import EmployerDashboard from './pages/EmployerDashboard';
import MappingWorkspace from './pages/MappingWorkspace';
import EvaluationLab from './pages/EvaluationLab';
import AdminDashboard from './pages/AdminDashboard';

function MainApp() {
  const { user, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('student');

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-400" />
          <p className="text-xs font-semibold text-sky-200">Loading Academia–Industry Skill Portal...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between">
      <div>
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === 'student' && <StudentDashboard />}
          {activeTab === 'faculty' && <FacultyDashboard />}
          {activeTab === 'placement' && <PlacementDashboard />}
          {activeTab === 'employer' && <EmployerDashboard />}
          {activeTab === 'mapping' && <MappingWorkspace />}
          {activeTab === 'evaluation' && <EvaluationLab />}
          {activeTab === 'admin' && <AdminDashboard />}
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div>
            <strong className="text-slate-800">Smart India Hackathon 2026</strong> · Problem Statement SIH26044 · Group G29
          </div>
          <div>
            Team Members: <strong className="text-slate-700">Shivam Chandel</strong> (12522547) &amp; <strong className="text-slate-700">Nayneet Kumar</strong> (12518540)
          </div>
          <div className="text-[11px] font-mono text-slate-400">
            FastAPI + React + NLP Intelligence Engine
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
