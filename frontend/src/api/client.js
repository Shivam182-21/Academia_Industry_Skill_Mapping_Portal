/**
 * API Client for Academia-Industry Skill Mapping Portal.
 * Connects to FastAPI backend (/api/v1).
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let errorDetail = 'Request failed';
    try {
      const err = await response.json();
      errorDetail = err.detail || JSON.stringify(err);
    } catch (e) {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }

  // Handle file downloads (e.g. CSV reports)
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('text/csv')) {
    return response.blob();
  }

  return response.json();
}

export const api = {
  // Auth
  login: (email, password) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    }),
  register: (data) =>
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  getMe: () => apiRequest('/auth/me'),
  getDemoUsers: () => apiRequest('/auth/demo-users'),

  // Curriculum
  getCourses: (department, cohortId) => {
    const params = new URLSearchParams();
    if (department) params.append('department', department);
    if (cohortId) params.append('cohort_id', cohortId);
    return apiRequest(`/curriculum/courses?${params.toString()}`);
  },
  createCourse: (courseData) =>
    apiRequest('/curriculum/courses', {
      method: 'POST',
      body: JSON.stringify(courseData)
    }),
  extractCourseSkills: (courseId) =>
    apiRequest(`/curriculum/courses/${courseId}/extract-skills`, {
      method: 'POST'
    }),
  reviewCourseSkill: (courseId, csId, reviewData) =>
    apiRequest(`/curriculum/courses/${courseId}/skills/${csId}`, {
      method: 'PUT',
      body: JSON.stringify(reviewData)
    }),

  // Jobs
  getJobRoles: (industry) => {
    const params = new URLSearchParams();
    if (industry) params.append('industry', industry);
    return apiRequest(`/jobs/roles?${params.toString()}`);
  },
  getJobRole: (jobId) => apiRequest(`/jobs/roles/${jobId}`),
  uploadJD: (data) =>
    apiRequest('/jobs/upload-jd', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  updateJobSkillWeight: (jobId, jsId, data) =>
    apiRequest(`/jobs/roles/${jobId}/skills/${jsId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  // Mapping
  runCurriculumMapping: (jobId, department) =>
    apiRequest('/mapping/curriculum-to-job', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, department })
    }),

  // Gap Analysis
  analyzeStudentGap: (jobId, studentId) =>
    apiRequest('/gap-analysis/student/analyze', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, student_id: studentId })
    }),
  getStudentSkills: (studentId) => {
    const query = studentId ? `?student_id=${studentId}` : '';
    return apiRequest(`/gap-analysis/student/skills${query}`);
  },
  addStudentSkill: (data) =>
    apiRequest('/gap-analysis/student/skills', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Recommendations
  getRecommendationsForJob: (jobId, studentId) => {
    const query = studentId ? `?student_id=${studentId}` : '';
    return apiRequest(`/recommendations/for-job/${jobId}${query}`);
  },
  getLearningResources: () => apiRequest('/recommendations/resources'),

  // Cohort Analytics
  getCohorts: () => apiRequest('/analytics/cohorts'),
  getCohortSummary: (cohortId, jobId) => {
    const query = jobId ? `?job_id=${jobId}` : '';
    return apiRequest(`/analytics/cohort/${cohortId}/summary${query}`);
  },
  exportCohortReportCSV: async (cohortId, jobId) => {
    const query = jobId ? `&job_id=${jobId}` : '';
    const blob = await apiRequest(`/analytics/export/cohort/${cohortId}?format=csv${query}`);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `placement_readiness_cohort_${cohortId.slice(0, 8)}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  },

  // Model Evaluation & Admin
  getEvaluationResults: () => apiRequest('/evaluation/results'),
  runEvaluationBenchmark: () =>
    apiRequest('/evaluation/run', { method: 'POST' }),
  getEvaluationErrors: () => apiRequest('/evaluation/errors'),
  getAdminUsers: () => apiRequest('/admin/users'),
  updateUserRole: (userId, role) =>
    apiRequest(`/admin/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role })
    }),
  getAuditLogs: (limit = 50) => apiRequest(`/admin/audit-logs?limit=${limit}`),
  getTaxonomy: () => apiRequest('/admin/taxonomy')
};
