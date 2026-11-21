import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  Briefcase,
  Upload,
  Plus,
  Sliders,
  Sparkles,
  CheckCircle2,
  Building2,
  Layers
} from 'lucide-react';

export default function EmployerDashboard() {
  const [jobRoles, setJobRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUploadJD, setShowUploadJD] = useState(false);

  // Upload JD Form State
  const [title, setTitle] = useState('');
  const [companyName, setCompanyName] = useState('TechCorp Solutions');
  const [industry, setIndustry] = useState('Information Technology');
  const [experienceLevel, setExperienceLevel] = useState('Entry-Level / 0–2 Years');
  const [jdText, setJdText] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadJobRoles();
  }, []);

  const loadJobRoles = async () => {
    try {
      const roles = await api.getJobRoles();
      setJobRoles(roles);
      if (roles.length > 0 && !selectedRole) {
        setSelectedRole(roles[0]);
      } else if (selectedRole) {
        const updated = roles.find(r => r.job_id === selectedRole.job_id);
        if (updated) setSelectedRole(updated);
      }
    } catch (err) {
      console.error("Error loading roles:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadJD = async (e) => {
    e.preventDefault();
    if (!jdText.trim()) return;
    setUploading(true);
    try {
      const res = await api.uploadJD({
        title,
        company_name: companyName,
        industry,
        experience_level: experienceLevel,
        job_description_text: jdText
      });
      alert(`Job Description uploaded! Extracted ${res.extracted_skills_count} skills.`);
      setShowUploadJD(false);
      setTitle('');
      setJdText('');
      await loadJobRoles();
    } catch (err) {
      alert(err.message || 'Error processing JD.');
    } finally {
      setUploading(false);
    }
  };

  const handleWeightChange = async (jsId, newWeight, proficiency) => {
    if (!selectedRole) return;
    try {
      await api.updateJobSkillWeight(selectedRole.job_id, jsId, {
        importance_weight: Number(newWeight),
        required_proficiency: proficiency
      });
      await loadJobRoles();
    } catch (err) {
      alert(err.message || 'Error updating weight');
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
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
              Industry Partner & Employer Portal
            </span>
            <span className="text-xs text-slate-500 font-medium">Job Profile & Competency Weighting Engine</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">
            Job Description Extraction & Skill Weighting Workspace
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Ingest unstructured Job Descriptions to extract technical competencies and customize importance weights ($w_i \in [1, 5]$).
          </p>
        </div>

        <button
          onClick={() => setShowUploadJD(true)}
          className="flex items-center space-x-1.5 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold px-4 py-2.5 rounded-lg shadow-xs transition"
        >
          <Upload className="w-4 h-4" />
          <span>Upload / Paste Job Description</span>
        </button>
      </div>

      {/* Main Dual-Pane Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Pane: Job Profiles List */}
        <div className="lg:col-span-4 space-y-3">
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center justify-between">
              <span>Target Job Profiles ({jobRoles.length})</span>
            </h3>

            <div className="space-y-2">
              {jobRoles.map((role) => {
                const isSelected = selectedRole?.job_id === role.job_id;
                return (
                  <button
                    key={role.job_id}
                    onClick={() => setSelectedRole(role)}
                    className={`w-full text-left p-3.5 rounded-xl border transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'border-sky-500 bg-sky-50/50 shadow-xs ring-1 ring-sky-500'
                        : 'border-slate-200 hover:border-slate-300 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs text-slate-900 line-clamp-1">{role.title}</span>
                    </div>
                    <p className="text-[11px] text-slate-500">{role.company_name} · {role.industry}</p>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 pt-1.5 border-t border-slate-100">
                      <span>{role.experience_level}</span>
                      <span className="font-mono font-bold text-sky-600">{role.required_skill_count} skills</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Pane: Skill Requirements & Weight Slider Editor */}
        <div className="lg:col-span-8 space-y-4">
          {selectedRole ? (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-6">
              {/* Header */}
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                    {selectedRole.company_name}
                  </span>
                  <span className="text-xs text-slate-500">{selectedRole.industry}</span>
                </div>
                <h3 className="text-lg font-extrabold text-slate-900">{selectedRole.title}</h3>
                <p className="text-xs text-slate-600 mt-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
                  {selectedRole.description}
                </p>
              </div>

              {/* Skill Requirements Weight Adjuster (FR-03 & SRS 6.3) */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
                    <Sliders className="w-4 h-4 text-sky-600" />
                    <span>Skill Importance Weights ($w_i$) & Proficiency Thresholds</span>
                  </h4>
                  <span className="text-[11px] text-slate-500">
                    5.0 = Core Requirement · 1.0 = Nice to have
                  </span>
                </div>

                <div className="space-y-3">
                  {selectedRole.skills.map((js) => (
                    <div
                      key={js.job_skill_id}
                      className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/40 flex flex-col md:flex-row md:items-center justify-between gap-4"
                    >
                      <div className="space-y-0.5 min-w-[200px]">
                        <span className="text-xs font-bold text-slate-900">{js.canonical_name}</span>
                        <div className="text-[10px] text-slate-500">{js.category}</div>
                      </div>

                      {/* Weight Slider */}
                      <div className="flex items-center space-x-3 flex-1 max-w-xs">
                        <label className="text-[10px] font-bold uppercase text-slate-600">Weight:</label>
                        <input
                          type="range"
                          min="1.0"
                          max="5.0"
                          step="0.5"
                          value={js.importance_weight}
                          onChange={(e) => handleWeightChange(js.job_skill_id, e.target.value, js.required_proficiency)}
                          className="w-full accent-sky-600"
                        />
                        <span className="font-mono text-xs font-bold text-sky-700 w-8 text-right">
                          {js.importance_weight.toFixed(1)}
                        </span>
                      </div>

                      {/* Proficiency Selector */}
                      <div className="flex items-center space-x-2">
                        <label className="text-[10px] font-bold uppercase text-slate-600">Target:</label>
                        <select
                          value={js.required_proficiency}
                          onChange={(e) => handleWeightChange(js.job_skill_id, js.importance_weight, e.target.value)}
                          className="bg-white border border-slate-300 text-slate-800 text-xs font-medium rounded px-2 py-1 outline-none"
                        >
                          <option value="beginner">Beginner</option>
                          <option value="intermediate">Intermediate</option>
                          <option value="advanced">Advanced</option>
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Modal: Upload JD */}
      {showUploadJD && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100">
            <h3 className="text-base font-bold text-slate-900 mb-1">Upload Industry Job Description</h3>
            <p className="text-xs text-slate-500 mb-4">
              Paste the text of your job posting. Our skill extractor will parse the requirements and populate initial weights.
            </p>

            <form onSubmit={handleUploadJD} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Job Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Associate DevOps Engineer"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Company Name</label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Industry</label>
                  <input
                    type="text"
                    required
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">
                  Job Description Text
                </label>
                <textarea
                  required
                  rows={5}
                  placeholder="Paste requirements, technologies, frameworks, and job duties..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowUploadJD(false)}
                  className="px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-lg shadow-xs transition"
                >
                  {uploading ? 'Parsing Skills...' : 'Extract & Create Role'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
