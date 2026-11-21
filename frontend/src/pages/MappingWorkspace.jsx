import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import RadialGauge from '../components/RadialGauge';
import {
  GitCompare,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sparkles,
  BookOpen,
  Briefcase,
  ArrowRight
} from 'lucide-react';

export default function MappingWorkspace() {
  const [jobRoles, setJobRoles] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [mappingData, setMappingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mappingLoading, setMappingLoading] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const roles = await api.getJobRoles();
        setJobRoles(roles);
        if (roles.length > 0) {
          const defaultId = roles[0].job_id;
          setSelectedJobId(defaultId);
          await loadMapping(defaultId);
        }
      } catch (err) {
        console.error("Error initializing mapping workspace:", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const loadMapping = async (jobId) => {
    setMappingLoading(true);
    try {
      const data = await api.runCurriculumMapping(jobId);
      setMappingData(data);
    } catch (err) {
      console.error("Error running mapping:", err);
    } finally {
      setMappingLoading(false);
    }
  };

  const handleRoleChange = async (e) => {
    const jobId = e.target.value;
    setSelectedJobId(jobId);
    await loadMapping(jobId);
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
            <span className="text-xs font-bold uppercase tracking-wider text-sky-600 bg-sky-50 px-2 py-0.5 rounded border border-sky-100">
              Curriculum-to-Industry Alignment
            </span>
            <span className="text-xs text-slate-500 font-medium">Core Intelligence Engine</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">
            Academia–Industry Skill Mapping Workspace
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Trace relationships between university course syllabi and industry job requirements with semantic similarity confidence scores.
          </p>
        </div>

        {/* Role Selector */}
        <div className="flex items-center space-x-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-600 whitespace-nowrap">
            Compare Against Role:
          </label>
          <select
            value={selectedJobId}
            onChange={handleRoleChange}
            className="bg-slate-50 border border-slate-300 text-slate-800 text-xs font-semibold rounded-lg px-3 py-2 outline-none"
          >
            {jobRoles.map((r) => (
              <option key={r.job_id} value={r.job_id}>
                {r.title} ({r.company_name})
              </option>
            ))}
          </select>
        </div>
      </div>

      {mappingLoading ? (
        <div className="flex justify-center items-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600" />
        </div>
      ) : mappingData ? (
        <>
          {/* Summary Coverage Gauge Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Curriculum Coverage</p>
                <div className="mt-1">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">
                    {mappingData.weighted_coverage}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Importance-weighted syllabus alignment
                </p>
              </div>
              <RadialGauge value={mappingData.weighted_coverage} size={84} strokeWidth={8} />
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Unweighted Coverage</p>
                <div className="mt-1">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">
                    {mappingData.unweighted_coverage}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  {mappingData.covered_skills_count} of {mappingData.total_required_skills} required skills addressed
                </p>
              </div>
              <RadialGauge value={mappingData.unweighted_coverage} size={84} strokeWidth={8} />
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Academic Scope</p>
                <div className="mt-1">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">
                    {mappingData.academic_courses_evaluated}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  University courses evaluated for this mapping
                </p>
              </div>
              <span className="text-[11px] font-mono text-emerald-600 font-bold">
                ✓ Full syllabus outcomes scanned
              </span>
            </div>
          </div>

          {/* Mapping Grid: Covered vs Unmapped Requirements */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Matched Curriculum Skills */}
            <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <h3 className="text-sm font-bold text-slate-900">
                    Mapped Skills & Curriculum Linkages ({mappingData.matched_curriculum_skills.length})
                  </h3>
                </div>
                <span className="text-xs text-slate-500">Exact & Semantic Connections</span>
              </div>

              <div className="space-y-3">
                {mappingData.matched_curriculum_skills.map((item, idx) => {
                  const isExact = item.mapping_type === 'exact';
                  return (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col md:flex-row md:items-center justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-slate-900">{item.job_skill}</span>
                          <span
                            className={`text-[9px] uppercase font-bold font-mono px-1.5 py-0.5 rounded ${
                              isExact
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-sky-100 text-sky-800'
                            }`}
                          >
                            {item.mapping_type} match ({Math.round(item.confidence * 100)}%)
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-500 flex items-center space-x-1">
                          <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                          <span>Taught in: <strong className="text-slate-700">{item.course_info}</strong></span>
                        </div>
                      </div>

                      <div className="text-right">
                        <span className="text-[10px] font-mono font-bold text-slate-600 bg-white px-2 py-1 rounded border border-slate-200">
                          Weight: {item.importance_weight}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right: Unmapped Requirements (Curriculum Gaps) */}
            <div className="lg:col-span-5 bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-5 h-5 text-rose-500" />
                  <h3 className="text-sm font-bold text-slate-900">
                    Unmapped Industry Skills ({mappingData.unmapped_industry_skills.length})
                  </h3>
                </div>
                <span className="text-xs text-rose-600 font-bold font-mono">Curriculum Gaps</span>
              </div>

              <div className="space-y-3">
                {mappingData.unmapped_industry_skills.length > 0 ? (
                  mappingData.unmapped_industry_skills.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border border-rose-200 bg-rose-50/30 flex flex-col justify-between"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-900">{item.job_skill}</span>
                        <span className="text-[10px] font-bold text-rose-700 font-mono">
                          Weight: {item.importance_weight}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-500">
                        Category: {item.category} · Required: {item.required_proficiency}
                      </p>
                      <div className="mt-2 text-[10px] text-rose-700 font-semibold bg-rose-50 px-2 py-1 rounded border border-rose-100">
                        Recommendation: Introduce in advanced elective or syllabus revision.
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-emerald-600 font-semibold py-8 text-center">
                    Full curriculum coverage! No unmapped skills for this role.
                  </p>
                )}
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
