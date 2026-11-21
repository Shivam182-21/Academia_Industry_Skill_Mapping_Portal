import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  BookOpen,
  Plus,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  Layers,
  FileText,
  Search,
  Filter
} from 'lucide-react';

export default function FacultyDashboard() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddCourse, setShowAddCourse] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);

  // New course form state
  const [courseCode, setCourseCode] = useState('');
  const [courseName, setCourseName] = useState('');
  const [semester, setSemester] = useState(3);
  const [department, setDepartment] = useState('Computer Science & Engineering');
  const [description, setDescription] = useState('');
  const [learningOutcomes, setLearningOutcomes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await api.getCourses();
      setCourses(data);
      if (data.length > 0 && !selectedCourse) {
        setSelectedCourse(data[0]);
      } else if (selectedCourse) {
        // Keep updated
        const updated = data.find(c => c.course_id === selectedCourse.course_id);
        if (updated) setSelectedCourse(updated);
      }
    } catch (err) {
      console.error("Error loading courses:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createCourse({
        course_code: courseCode,
        course_name: courseName,
        semester: Number(semester),
        department,
        description,
        learning_outcomes: learningOutcomes
      });
      setShowAddCourse(false);
      // Reset
      setCourseCode('');
      setCourseName('');
      setDescription('');
      setLearningOutcomes('');
      await loadCourses();
    } catch (err) {
      alert(err.message || 'Error creating course');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReviewSkill = async (csId, status, coverageLevel = 1.0) => {
    if (!selectedCourse) return;
    try {
      await api.reviewCourseSkill(selectedCourse.course_id, csId, {
        status,
        coverage_level: coverageLevel
      });
      await loadCourses();
    } catch (err) {
      alert(err.message || 'Error updating skill review status.');
    }
  };

  const handleReExtract = async (courseId) => {
    try {
      const res = await api.extractCourseSkills(courseId);
      alert(res.message);
      await loadCourses();
    } catch (err) {
      alert(err.message || 'Extraction failed');
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
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
              Academic Curriculum Portal
            </span>
            <span className="text-xs text-slate-500 font-medium">Faculty Curriculum Mapping & Validation</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">
            Course Syllabi & Skill Extraction Workspace
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Upload course descriptions and learning outcomes to automatically identify and validate taught technical competencies.
          </p>
        </div>

        <button
          onClick={() => setShowAddCourse(true)}
          className="flex items-center space-x-1.5 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold px-4 py-2.5 rounded-lg shadow-xs transition"
        >
          <Plus className="w-4 h-4" />
          <span>Add Course & Upload Syllabus</span>
        </button>
      </div>

      {/* Main Dual-Pane Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Pane: Course List */}
        <div className="lg:col-span-4 space-y-3">
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center justify-between">
              <span>Department Courses ({courses.length})</span>
              <span className="text-[10px] text-slate-400 font-mono">CSE & Ayush</span>
            </h3>

            <div className="space-y-2">
              {courses.map((course) => {
                const isSelected = selectedCourse?.course_id === course.course_id;
                return (
                  <button
                    key={course.course_id}
                    onClick={() => setSelectedCourse(course)}
                    className={`w-full text-left p-3.5 rounded-xl border transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'border-sky-500 bg-sky-50/50 shadow-xs ring-1 ring-sky-500'
                        : 'border-slate-200 hover:border-slate-300 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-xs font-bold text-sky-700 bg-sky-100 px-2 py-0.5 rounded">
                        {course.course_code}
                      </span>
                      <span className="text-[10px] font-bold text-slate-500">
                        Semester {course.semester}
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{course.course_name}</h4>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 pt-1.5 border-t border-slate-100">
                      <span>{course.department}</span>
                      <span className="font-mono font-semibold text-sky-600">{course.skill_count} skills extracted</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Pane: Course Inspector & Extracted Skills */}
        <div className="lg:col-span-8 space-y-4">
          {selectedCourse ? (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-6">
              {/* Course Title & Metadata */}
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-sky-100 text-sky-800 border border-sky-200">
                      {selectedCourse.course_code}
                    </span>
                    <span className="text-xs font-medium text-slate-500">
                      Semester {selectedCourse.semester} · {selectedCourse.department}
                    </span>
                  </div>
                  <h3 className="text-lg font-extrabold text-slate-900">{selectedCourse.course_name}</h3>
                </div>

                <button
                  onClick={() => handleReExtract(selectedCourse.course_id)}
                  className="flex items-center space-x-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-lg transition"
                >
                  <Sparkles className="w-3.5 h-3.5 text-sky-600" />
                  <span>Re-run NLP Extraction</span>
                </button>
              </div>

              {/* Syllabus Description */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1 flex items-center space-x-1.5">
                  <FileText className="w-4 h-4 text-slate-500" />
                  <span>Syllabus Content & Learning Outcomes</span>
                </h4>
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs text-slate-700 leading-relaxed font-mono">
                  {selectedCourse.description}
                  {selectedCourse.learning_outcomes && (
                    <div className="mt-2 pt-2 border-t border-slate-200">
                      <strong className="text-slate-900">Learning Outcomes: </strong>
                      {selectedCourse.learning_outcomes}
                    </div>
                  )}
                </div>
              </div>

              {/* Extracted Skills Table & Approval Controls (FR-02) */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
                    <Layers className="w-4 h-4 text-sky-600" />
                    <span>Extracted Academic Competencies ({selectedCourse.skills.length})</span>
                  </h4>
                  <span className="text-[11px] text-slate-500">
                    Human-in-the-loop review: Approve or reject AI extractions
                  </span>
                </div>

                <div className="space-y-2.5">
                  {selectedCourse.skills.map((cs) => {
                    const isApproved = cs.status === 'approved';
                    const isRejected = cs.status === 'rejected';

                    return (
                      <div
                        key={cs.course_skill_id}
                        className={`p-3.5 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-3 transition ${
                          isApproved
                            ? 'bg-emerald-50/20 border-emerald-200'
                            : isRejected
                            ? 'bg-rose-50/20 border-rose-200 opacity-60'
                            : 'bg-amber-50/20 border-amber-200'
                        }`}
                      >
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-bold text-slate-900">{cs.canonical_name}</span>
                            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                              {cs.category}
                            </span>
                            <span
                              className={`text-[9px] uppercase font-bold font-mono px-1.5 py-0.5 rounded ${
                                isApproved
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : isRejected
                                  ? 'bg-rose-100 text-rose-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              {cs.status}
                            </span>
                          </div>
                          {cs.evidence_snippet && (
                            <p className="text-[10px] text-slate-500 italic font-mono line-clamp-1">
                              Context: "{cs.evidence_snippet}"
                            </p>
                          )}
                        </div>

                        {/* Faculty Review Action Buttons */}
                        <div className="flex items-center space-x-1.5">
                          <button
                            onClick={() => handleReviewSkill(cs.course_skill_id, 'approved', 1.0)}
                            className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-semibold transition ${
                              isApproved && cs.coverage_level === 1.0
                                ? 'bg-emerald-600 text-white'
                                : 'bg-slate-100 hover:bg-emerald-50 text-slate-700 hover:text-emerald-700'
                            }`}
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Full (1.0)</span>
                          </button>

                          <button
                            onClick={() => handleReviewSkill(cs.course_skill_id, 'approved', 0.5)}
                            className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-semibold transition ${
                              isApproved && cs.coverage_level === 0.5
                                ? 'bg-amber-600 text-white'
                                : 'bg-slate-100 hover:bg-amber-50 text-slate-700 hover:text-amber-700'
                            }`}
                          >
                            <span>Partial (0.5)</span>
                          </button>

                          <button
                            onClick={() => handleReviewSkill(cs.course_skill_id, 'rejected', 0.0)}
                            className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-semibold transition ${
                              isRejected
                                ? 'bg-rose-600 text-white'
                                : 'bg-slate-100 hover:bg-rose-50 text-slate-700 hover:text-rose-700'
                            }`}
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Reject</span>
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Modal: Add Course */}
      {showAddCourse && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100">
            <h3 className="text-base font-bold text-slate-900 mb-1">Add Academic Course & Syllabus</h3>
            <p className="text-xs text-slate-500 mb-4">
              Enter course information. Our NLP extractor will automatically identify technical skills upon saving.
            </p>

            <form onSubmit={handleCreateCourse} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Course Code</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. CS401"
                    value={courseCode}
                    onChange={(e) => setCourseCode(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Semester</label>
                  <input
                    type="number"
                    min="1"
                    max="8"
                    required
                    value={semester}
                    onChange={(e) => setSemester(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Course Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Cloud Computing & Microservices Architecture"
                  value={courseName}
                  onChange={(e) => setCourseName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Department</label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                >
                  <option value="Computer Science & Engineering">Computer Science & Engineering</option>
                  <option value="Ayush Informatics & HealthTech">Ayush Informatics & HealthTech</option>
                  <option value="Information Technology">Information Technology</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">
                  Syllabus Description (Text for NLP Extraction)
                </label>
                <textarea
                  required
                  rows={4}
                  placeholder="Paste syllabus modules, concepts, lab topics, and tools..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">
                  Expected Learning Outcomes
                </label>
                <input
                  type="text"
                  placeholder="e.g. Master container orchestration with Docker and automated testing..."
                  value={learningOutcomes}
                  onChange={(e) => setLearningOutcomes(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddCourse(false)}
                  className="px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-lg shadow-xs transition"
                >
                  {submitting ? 'Extracting Skills...' : 'Create Course & Extract Skills'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
