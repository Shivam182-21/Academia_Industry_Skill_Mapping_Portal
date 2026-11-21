import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import MetricCard from '../components/MetricCard';
import ProgressBar from '../components/ProgressBar';
import RadialGauge from '../components/RadialGauge';
import {
  BarChart3,
  Download,
  Users,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Briefcase,
  Search,
  Filter
} from 'lucide-react';

export default function PlacementDashboard() {
  const [cohorts, setCohorts] = useState([]);
  const [selectedCohortId, setSelectedCohortId] = useState('');
  const [jobRoles, setJobRoles] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    async function init() {
      try {
        const [cohortList, roleList] = await Promise.all([
          api.getCohorts(),
          api.getJobRoles()
        ]);
        setCohorts(cohortList);
        setJobRoles(roleList);

        if (cohortList.length > 0) {
          const defaultCohort = cohortList[0].cohort_id;
          const defaultJob = roleList.length > 0 ? roleList[0].job_id : '';
          setSelectedCohortId(defaultCohort);
          setSelectedJobId(defaultJob);
          await loadSummary(defaultCohort, defaultJob);
        }
      } catch (err) {
        console.error("Error loading placement data:", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const loadSummary = async (cohortId, jobId) => {
    try {
      const data = await api.getCohortSummary(cohortId, jobId);
      setSummary(data);
    } catch (err) {
      console.error("Error loading cohort summary:", err);
    }
  };

  const handleCohortChange = async (e) => {
    const cId = e.target.value;
    setSelectedCohortId(cId);
    await loadSummary(cId, selectedJobId);
  };

  const handleJobChange = async (e) => {
    const jId = e.target.value;
    setSelectedJobId(jId);
    await loadSummary(selectedCohortId, jId);
  };

  const handleExportCSV = async () => {
    setExporting(true);
    try {
      await api.exportCohortReportCSV(selectedCohortId, selectedJobId);
    } catch (err) {
      alert(err.message || 'Error exporting CSV report.');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600" />
      </div>
    );
  }

  // Combine students for candidate table
  const allStudents = summary ? [
    ...summary.students.high_readiness.map(s => ({ ...s, tier: 'High Readiness (>=75%)', tierColor: 'text-emerald-700 bg-emerald-50' })),
    ...summary.students.moderate_readiness.map(s => ({ ...s, tier: 'Moderate (50-74%)', tierColor: 'text-amber-700 bg-amber-50' })),
    ...summary.students.needs_upskilling.map(s => ({ ...s, tier: 'Needs Upskilling (<50%)', tierColor: 'text-rose-700 bg-rose-50' }))
  ] : [];

  const filteredStudents = allStudents.filter(s =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (s.roll_number && s.roll_number.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Top Header & Controls */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-purple-600 bg-purple-50 px-2 py-0.5 rounded border border-purple-100">
              Placement Analytics & Cohort Readiness
            </span>
            <span className="text-xs text-slate-500 font-medium">SIH 2026 Institutional Module</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">
            Cohort Placement Readiness & Skill Shortage Analytics
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Identify batch-wide competency distributions and aggregate skill shortages for targeted pre-placement training.
          </p>
        </div>

        {/* Cohort & Role Dropdowns */}
        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={selectedCohortId}
            onChange={handleCohortChange}
            className="bg-slate-50 border border-slate-300 text-slate-800 text-xs font-semibold rounded-lg px-3 py-2 outline-none"
          >
            {cohorts.map((c) => (
              <option key={c.cohort_id} value={c.cohort_id}>
                {c.name}
              </option>
            ))}
          </select>

          <select
            value={selectedJobId}
            onChange={handleJobChange}
            className="bg-slate-50 border border-slate-300 text-slate-800 text-xs font-semibold rounded-lg px-3 py-2 outline-none"
          >
            {jobRoles.map((r) => (
              <option key={r.job_id} value={r.job_id}>
                Role: {r.title}
              </option>
            ))}
          </select>

          <button
            onClick={handleExportCSV}
            disabled={exporting}
            className="flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold px-3.5 py-2 rounded-lg shadow-xs transition"
          >
            <Download className="w-3.5 h-3.5 text-sky-400" />
            <span>{exporting ? 'Generating CSV...' : 'Export Report (CSV)'}</span>
          </button>
        </div>
      </div>

      {summary ? (
        <>
          {/* Key Metric Gauges */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Cohort Average</p>
                <div className="mt-1">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">
                    {summary.average_coverage}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Mean readiness across {summary.total_students} students
                </p>
              </div>
              <RadialGauge value={summary.average_coverage} size={84} strokeWidth={8} />
            </div>

            <MetricCard
              title="Job Ready Candidates"
              value={summary.distribution.high_readiness_count}
              subtitle={`${summary.distribution.high_readiness_pct}% of batch (>=75% coverage)`}
              icon={CheckCircle2}
              badgeColor="bg-emerald-50 text-emerald-700 border-emerald-200"
            />

            <MetricCard
              title="Moderate Readiness"
              value={summary.distribution.moderate_readiness_count}
              subtitle={`${summary.distribution.moderate_readiness_pct}% of batch (50-74% coverage)`}
              icon={AlertTriangle}
              badgeColor="bg-amber-50 text-amber-700 border-amber-200"
            />

            <MetricCard
              title="Needs Upskilling"
              value={summary.distribution.needs_upskilling_count}
              subtitle={`${summary.distribution.needs_upskilling_pct}% of batch (<50% coverage)`}
              icon={XCircle}
              badgeColor="bg-rose-50 text-rose-700 border-rose-200"
            />
          </div>

          {/* Aggregate Skill Shortage Heatmap / Bar Distribution (FR-07) */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Aggregate Cohort Skill Shortages (Most Urgent Curriculum & Placement Gaps)
                </h3>
                <p className="text-xs text-slate-500">
                  Top skills required by industry but lacking verified evidence across the cohort.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-slate-600 bg-slate-100 px-2.5 py-1 rounded">
                Target: {summary.target_job_title}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              {summary.shortage_distribution.map((shortage, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col justify-between"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-900">{shortage.skill_name}</span>
                    <span className="text-xs font-mono font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-100">
                      {shortage.shortage_percentage}% missing ({shortage.missing_students_count} students)
                    </span>
                  </div>
                  <ProgressBar
                    value={shortage.shortage_percentage}
                    max={100}
                    showPercentage={false}
                    height="h-2"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Student Candidate Finder Table */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Candidate Readiness Directory</h3>
                <p className="text-xs text-slate-500">Filter students by name, roll number, and placement tier.</p>
              </div>

              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search students..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-sky-500 w-60"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                    <th className="py-2.5 px-3">Roll No.</th>
                    <th className="py-2.5 px-3">Student Name</th>
                    <th className="py-2.5 px-3">Readiness Tier</th>
                    <th className="py-2.5 px-3">Weighted Coverage</th>
                    <th className="py-2.5 px-3">Demonstrated Skills</th>
                    <th className="py-2.5 px-3">Missing Gaps</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredStudents.map((s, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70 transition">
                      <td className="py-3 px-3 font-mono font-bold text-slate-700">{s.roll_number || 'N/A'}</td>
                      <td className="py-3 px-3 font-bold text-slate-900">{s.name}</td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${s.tierColor}`}>
                          {s.tier}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono font-extrabold text-slate-900">
                        {s.weighted_coverage}%
                      </td>
                      <td className="py-3 px-3 font-mono text-emerald-600 font-bold">{s.demonstrated_count} skills</td>
                      <td className="py-3 px-3 font-mono text-rose-600 font-bold">{s.missing_skills_count} gaps</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
