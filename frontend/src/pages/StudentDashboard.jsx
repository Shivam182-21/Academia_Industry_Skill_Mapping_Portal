import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import RadialGauge from '../components/RadialGauge';
import MetricCard from '../components/MetricCard';
import ProgressBar from '../components/ProgressBar';
import {
  Briefcase,
  CheckCircle2,
  AlertCircle,
  XCircle,
  ExternalLink,
  Plus,
  BookOpen,
  Award,
  Sparkles,
  Info
} from 'lucide-react';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [jobRoles, setJobRoles] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [gapData, setGapData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [showAddEvidence, setShowAddEvidence] = useState(false);
  const [newSkillName, setNewSkillName] = useState('');
  const [newEvidenceSource, setNewEvidenceSource] = useState('project');
  const [newProficiency, setNewProficiency] = useState('intermediate');

  // Load available roles and initial analysis
  useEffect(() => {
    async function init() {
      try {
        const roles = await api.getJobRoles();
        setJobRoles(roles);
        if (roles.length > 0) {
          const defaultId = roles[0].job_id;
          setSelectedJobId(defaultId);
          await loadAnalysis(defaultId);
        }
      } catch (err) {
        console.error("Initialization error:", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const loadAnalysis = async (jobId) => {
    setAnalyzing(true);
    try {
      const studentId = user?.student?.student_id || user?.student_id;
      const res = await api.analyzeStudentGap(jobId, studentId);
      setGapData(res);

      const recs = await api.getRecommendationsForJob(jobId, studentId);
      setRecommendations(recs.recommendations || []);
    } catch (err) {
      console.error("Error analyzing gap:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleRoleChange = async (e) => {
    const jobId = e.target.value;
    setSelectedJobId(jobId);
    await loadAnalysis(jobId);
  };

  const handleAddEvidence = async (e) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;
    try {
      await api.addStudentSkill({
        skill_name: newSkillName.trim(),
        evidence_source: newEvidenceSource,
        proficiency_level: newProficiency
      });
      setShowAddEvidence(false);
      setNewSkillName('');
      // Reload analysis
      await loadAnalysis(selectedJobId);
    } catch (err) {
      alert(err.message || 'Error submitting skill evidence.');
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
      {/* Welcome & Role Selector Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-sky-600 bg-sky-50 px-2 py-0.5 rounded border border-sky-100">
              Student Placement Readiness
            </span>
            <span className="text-xs text-slate-500 font-mono">
              Roll: {user?.student?.roll_number || 'RK3P25ORA20'} · Reg: {user?.student?.registration_number || '12522547'}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">
            Skill-Gap Analysis & Placement Trajectory
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluating student demonstrated competencies against target industry requirements.
          </p>
        </div>

        {/* Role Selector */}
        <div className="flex items-center space-x-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-600 whitespace-nowrap">
            Target Job Profile:
          </label>
          <select
            value={selectedJobId}
            onChange={handleRoleChange}
            className="bg-slate-50 border border-slate-300 text-slate-800 text-xs font-semibold rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 outline-none"
          >
            {jobRoles.map((role) => (
              <option key={role.job_id} value={role.job_id}>
                {role.title} ({role.company_name})
              </option>
            ))}
          </select>
          <button
            onClick={() => setShowAddEvidence(true)}
            className="flex items-center space-x-1.5 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-xs transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add Skill Evidence</span>
          </button>
        </div>
      </div>

      {analyzing ? (
        <div className="flex justify-center items-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600" />
        </div>
      ) : gapData ? (
        <>
          {/* Key Metric Gauges */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Weighted Coverage</p>
                <div className="mt-1">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">
                    {gapData.weighted_coverage}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Weighted by skill importance ($w_i \in [1, 5]$)
                </p>
              </div>
              <RadialGauge value={gapData.weighted_coverage} size={84} strokeWidth={8} />
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Unweighted Coverage</p>
                <div className="mt-1">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">
                    {gapData.unweighted_coverage}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Direct ratio: {gapData.demonstrated_count} of {gapData.total_required_skills} skills
                </p>
              </div>
              <RadialGauge value={gapData.unweighted_coverage} size={84} strokeWidth={8} />
            </div>

            <MetricCard
              title="Demonstrated Skills"
              value={gapData.demonstrated_count}
              subtitle="Verified coursework & projects"
              icon={CheckCircle2}
              badgeColor="bg-emerald-50 text-emerald-700 border-emerald-200"
            />

            <MetricCard
              title="Critical Skill Gaps"
              value={gapData.missing_count}
              subtitle="Skills requiring upskilling"
              icon={XCircle}
              badgeColor="bg-rose-50 text-rose-700 border-rose-200"
            />
          </div>

          {/* Categorized Skills Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 1. Demonstrated Skills */}
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                    Demonstrated Skills ({gapData.demonstrated?.length || 0})
                  </h3>
                </div>
                <span className="text-[10px] uppercase font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                  Full Match (1.0)
                </span>
              </div>

              <div className="space-y-3">
                {gapData.demonstrated?.length > 0 ? (
                  gapData.demonstrated.map((s, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-emerald-100 bg-emerald-50/30 flex flex-col justify-between"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-900">{s.canonical_name}</span>
                        <span className="text-[10px] font-semibold text-slate-500 capitalize">
                          {s.student_proficiency}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-emerald-100/50">
                        <span>Source: <strong className="capitalize text-slate-700">{s.evidence_source}</strong></span>
                        <span className="text-emerald-700 font-semibold flex items-center">
                          <Award className="w-3 h-3 mr-0.5" /> Verified
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 italic py-4 text-center">No fully demonstrated skills.</p>
                )}
              </div>
            </div>

            {/* 2. Partially Demonstrated Skills */}
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 text-amber-500" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                    Partially Covered ({gapData.partially_demonstrated?.length || 0})
                  </h3>
                </div>
                <span className="text-[10px] uppercase font-mono font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-100">
                  Partial (0.5)
                </span>
              </div>

              <div className="space-y-3">
                {gapData.partially_demonstrated?.length > 0 ? (
                  gapData.partially_demonstrated.map((s, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-amber-100 bg-amber-50/30 flex flex-col justify-between"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-900">{s.canonical_name}</span>
                        <span className="text-[10px] font-bold text-amber-700 font-mono">
                          Weight: {s.importance_weight}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-600 mt-1">
                        Demonstrated at <span className="font-semibold">{s.student_proficiency}</span> level; role demands <span className="font-semibold">{s.required_proficiency}</span>.
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 italic py-4 text-center">No partially demonstrated skills.</p>
                )}
              </div>
            </div>

            {/* 3. Critical Missing Skill Gaps */}
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                <div className="flex items-center space-x-2">
                  <XCircle className="w-4 h-4 text-rose-500" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                    Missing Skill Gaps ({gapData.missing?.length || 0})
                  </h3>
                </div>
                <span className="text-[10px] uppercase font-mono font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-100">
                  Unmet (0.0)
                </span>
              </div>

              <div className="space-y-3">
                {gapData.missing?.length > 0 ? (
                  gapData.missing.map((s, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-rose-100 bg-rose-50/30 flex flex-col justify-between"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-900">{s.canonical_name}</span>
                        <span className="text-[10px] font-bold text-rose-700 font-mono">
                          Weight: {s.importance_weight} / 5.0
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-500 mt-0.5">
                        Category: {s.category} · Target level: {s.required_proficiency}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-emerald-600 font-semibold py-4 text-center">
                    Congratulations! All required skills are demonstrated.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Actionable Learning Recommendations Section (FR-06) */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg border border-indigo-100">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Targeted Learning Recommendations
                  </h3>
                  <p className="text-xs text-slate-500">
                    Ranked by role relevance & missing skill weights to close your placement gap.
                  </p>
                </div>
              </div>
              <span className="text-xs font-mono font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-full border border-indigo-100">
                {recommendations.length} Curated Pathways
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl border border-slate-200 hover:border-sky-300 hover:bg-sky-50/20 transition-all flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-xs font-bold text-slate-900 group-hover:text-sky-700">
                        #{rec.rank}. {rec.title}
                      </span>
                      <span className="text-[10px] font-bold uppercase font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 whitespace-nowrap">
                        {rec.provider}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 text-[11px] text-slate-500 mb-2">
                      <span className="font-semibold text-slate-700">Target Skill:</span>
                      <span className="text-sky-700 font-bold bg-sky-50 px-1.5 py-0.5 rounded border border-sky-100">
                        {rec.skill_name}
                      </span>
                      <span>·</span>
                      <span>{rec.difficulty}</span>
                    </div>

                    <p className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 mb-3">
                      <span className="font-semibold text-slate-700">Why recommended: </span>
                      {rec.reason}
                    </p>
                  </div>

                  <a
                    href={rec.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center justify-center space-x-1.5 text-xs font-bold text-white bg-slate-900 hover:bg-sky-600 px-3 py-2 rounded-lg transition"
                  >
                    <span>Enroll / View Resource</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}

      {/* Modal: Add Student Skill Evidence */}
      {showAddEvidence && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100">
            <h3 className="text-base font-bold text-slate-900 mb-1">Submit Student Skill Evidence</h3>
            <p className="text-xs text-slate-500 mb-4">
              Add verified competencies from your lab coursework, capstone projects, or external certifications.
            </p>

            <form onSubmit={handleAddEvidence} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">
                  Skill / Technology Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Docker & Containerization, PyTest, or FastAPI"
                  value={newSkillName}
                  onChange={(e) => setNewSkillName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">
                  Evidence Source
                </label>
                <select
                  value={newEvidenceSource}
                  onChange={(e) => setNewEvidenceSource(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                >
                  <option value="project">Capstone / GitHub Project</option>
                  <option value="coursework">Academic Coursework / Lab</option>
                  <option value="certification">External Certification</option>
                  <option value="assessment">Proctored Assessment</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">
                  Proficiency Level
                </label>
                <select
                  value={newProficiency}
                  onChange={(e) => setNewProficiency(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                >
                  <option value="intermediate">Intermediate (Hands-on)</option>
                  <option value="advanced">Advanced (Production-ready)</option>
                  <option value="beginner">Beginner (Foundational)</option>
                </select>
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddEvidence(false)}
                  className="px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-lg shadow-xs transition"
                >
                  Add to Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
